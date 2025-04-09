#!/usr/bin/env python3

import shutil

import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent)

from _configure_environment import environment
from _builder_base          import builder_base

class builder_libpsl(builder_base):
    def __init__(self):
        super().__init__()
        self.__project_dir = pathlib.Path(__file__).parent.parent.parent
        self.__module_dir  = pathlib.Path(__file__).parent.parent.parent / "third_party" / "libpsl"
        if(
            not self.__module_dir.exists() or
            not self.__module_dir.is_dir()
        ):
            raise

    def __generate_suffixes_dafsa_h(self):
        self.env.run_commands(
            commands = [
                "python3 src/psl-make-dafsa --output-format=cxx+ list/public_suffix_list.dat suffixes_dafsa.h",
            ],
            cwd = self.__module_dir
        )
        
        source_files = [
            "./src/lookup_string_in_fixed_set.c",
            "./src/psl.c"
        ]

    def __generate_libpsl_h(self):
        psl_version        = ""
        psl_version_major  = ""
        psl_version_minor  = ""
        psl_version_patch  = ""
        psl_version_number = ""

        with open(self.__module_dir / "version.txt") as version_file:
            psl_version = version_file.read().strip()
            psl_version_major, psl_version_minor, psl_version_patch = psl_version.split(".")
            psl_version_number = f"0x{int(psl_version_major):02X}{int(psl_version_minor):02X}{int(psl_version_patch):02X}"

        libpsl_h_content = ""
        with open(self.__module_dir / "include" / "libpsl.h.in") as libpsl_h_in_file:
            libpsl_h_in_file_lines = libpsl_h_in_file.readlines()
            for line in libpsl_h_in_file_lines:
                line = line.replace("@LIBPSL_VERSION@",        f"{psl_version}")
                line = line.replace("@LIBPSL_VERSION_MAJOR@",  f"{psl_version_major}")
                line = line.replace("@LIBPSL_VERSION_MINOR@",  f"{psl_version_minor}")
                line = line.replace("@LIBPSL_VERSION_PATCH@",  f"{psl_version_patch}")
                line = line.replace("@LIBPSL_VERSION_NUMBER@", f"{psl_version_number}")
                libpsl_h_content += line

        with open(self.__module_dir / "include" / "libpsl.h", "w") as libpsl_h_file:
            libpsl_h_file.write(libpsl_h_content)

    def __generate_cmake_file(self):
        content = '''
            cmake_minimum_required(VERSION 3.15)

            set(CMAKE_CXX_STANDARD 20)
            set(CMAKE_EXPORT_COMPILE_COMMANDS 1)

            project(psl_test)

            set(${PROJECT_NAME}_INC     "")
            set(${PROJECT_NAME}_INC_DIR "")
            set(${PROJECT_NAME}_SRC     "")
            set(${PROJECT_NAME}_SRC_DIR "")
            set(${PROJECT_NAME}_LIB     "")
            set(${PROJECT_NAME}_LIB_DIR "")

            set(PROGRAM_NAME
                "${PROJECT_NAME}"
            )
            add_library(psl STATIC
                "${CMAKE_SOURCE_DIR}/src/psl.c"
                "${CMAKE_SOURCE_DIR}/src/lookup_string_in_fixed_set.c"
            )
            target_include_directories(psl PUBLIC
                "${CMAKE_SOURCE_DIR}/"
                "${CMAKE_SOURCE_DIR}/include/"
            )
            target_compile_definitions(psl PUBLIC
                "ENABLE_BUILTIN"
                "PSL_STATIC"
                PACKAGE_VERSION="0.21.5"
            )

            install(DIRECTORY "${CMAKE_SOURCE_DIR}/include/"
                DESTINATION "include"
                FILES_MATCHING PATTERN "*.h"
            )
            install(TARGETS psl
                ARCHIVE DESTINATION "lib"
            )
        '''
        with open(self.__module_dir / "CMakeLists.txt", "w") as libpsl_cmake_file:
            libpsl_cmake_file.write(content)

    def __run_cmake(self):
        build_dir   = self.__project_dir / "__build"   / "libpsl"
        install_dir = self.__project_dir / "__install" / "libpsl"

        for build_type in ["Debug", "Release"]:
            self.env.run_commands(
                commands = [
                    f"cmake  -B {build_dir} -DCMAKE_INSTALL_PREFIX={install_dir / build_type}",
                    f"cmake --build {build_dir} --config={build_type}",
                    f"cmake --install {build_dir}"
                ],
                cwd = self.__module_dir
            )
            shutil.rmtree(build_dir)

    def build(self):
        self.__generate_suffixes_dafsa_h()
        self.__generate_libpsl_h()
        self.__generate_cmake_file()
        self.__run_cmake()

def main():
    builder = builder_libpsl()
    builder.build()

if(__name__ == "__main__"):
    main()

