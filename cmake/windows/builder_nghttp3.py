#!/usr/bin/env python3

import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent)

from _configure_environment import environment
from _builder_base          import builder_base

class builder_nghttp3(builder_base):
    def __init__(self):
        super().__init__()
        self.__project_dir = pathlib.Path(__file__).parent.parent.parent
        self.__module_dir  = self.__project_dir / "third_party" / "nghttp3"
        if(
            not self.__module_dir.exists() or
            not self.__module_dir.is_dir()
        ):
            raise

    def __run_cmake(self):
        build_dir   = self.__project_dir / "__build"   / "nghttp3"
        install_dir = self.__project_dir / "__install" / "nghttp3"

        for build_type in ["Debug", "Release"]:
            cur_build_dir = build_dir / build_type
            self.env.run_commands(
                commands = [
                    f'cmake -B        {cur_build_dir}'
                        f' -DCMAKE_INSTALL_PREFIX={install_dir / build_type}'
                        f' -DCMAKE_BUILD_TYPE={build_type}'
                        f' -DENABLE_LIB_ONLY=ON'
                        f' -DENABLE_STATIC_LIB=ON'
                        f' -DENABLE_SHARED_LIB=OFF'
                        f' -DBUILD_TESTING=OFF',
                    f'cmake --build   {cur_build_dir} --config={build_type}',
                    f'cmake --install {cur_build_dir} --config={build_type}'
                ],
                cwd = self.__module_dir
            )

    def build(self):
        self.__run_cmake()

def main():
    builder = builder_nghttp3()
    builder.build()

if(__name__ == "__main__"):
    main()

