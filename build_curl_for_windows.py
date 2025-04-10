#!/usr/bin/env python3

import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent / "cmake" / "windows"))

from _configure_environment import environment
from _builder_base          import builder_base

from builder_libpsl         import builder_libpsl

class builder_curl(builder_base):
    def __init__(self):
        super().__init__()
        self.__project_dir = pathlib.Path(__file__).parent
        self.__module_dir  = self.__project_dir / "third_party" / "curl"
        if(
            not self.__module_dir.exists() or
            not self.__module_dir.is_dir()
        ):
            raise

    def __build_submodules(self):
        builder_libpsl_obj = builder_libpsl()
        builder_libpsl_obj.build()

    def __run_cmake(self):
        build_dir        = self.__project_dir / "__build"
        install_dir      = self.__project_dir / "__install"

        curl_build_dir   = self.__project_dir / "__build"   / "curl"
        curl_install_dir = self.__project_dir / "__install" / "curl"

        for build_type in ["Debug", "Release"]:
            cur_build_dir = curl_build_dir / build_type
            self.env.run_commands(
                commands = [
                    f'cmake -B        {cur_build_dir}'
                        f' -DCMAKE_INSTALL_PREFIX={curl_install_dir / build_type}'
                        f' -DBUILD_STATIC_LIBS=ON'
                        f' -DLIBPSL_INCLUDE_DIR="{install_dir / "libpsl" / "Release" / "include"}"'
                        f' -DLIBPSL_LIBRARY="{install_dir / "libpsl" / "Release" / "lib" / "psl.lib"}"'
                        f' -DLIBPSL_CFLAGS="-DPSL_API="',
                    f'cmake --build   {cur_build_dir} --config={build_type}',
                    f'cmake --install {cur_build_dir} --config={build_type}'
                ],
                cwd = self.__module_dir
            )


    def build(self):
        self.__build_submodules()
        self.__run_cmake()


def main():
    builder = builder_curl()
    builder.build()

if(__name__ == "__main__"):
    main()

