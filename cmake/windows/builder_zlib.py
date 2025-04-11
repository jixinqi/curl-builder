#!/usr/bin/env python3

import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent)

from _configure_environment import environment
from _builder_base          import builder_base

class builder_zlib(builder_base):
    def __init__(self):
        super().__init__()
        self.__project_dir = pathlib.Path(__file__).parent.parent.parent
        self.__module_dir  = self.__project_dir / "third_party" / "zlib"
        if(
            not self.__module_dir.exists() or
            not self.__module_dir.is_dir()
        ):
            raise

    def __run_cmake(self):
        build_dir   = self.__project_dir / "__build"   / "zlib"
        install_dir = self.__project_dir / "__install" / "zlib"

        for build_type in ["Debug", "Release"]:
            cur_build_dir = build_dir / build_type
            self.env.run_commands(
                commands = [
                    f'cmake -B        {cur_build_dir}'
                        f' -DCMAKE_INSTALL_PREFIX={install_dir / build_type}'
                        f' -DZLIB_BUILD_TESTING=OFF'
                        f' -DZLIB_BUILD_SHARED=OFF',
                    f'cmake --build   {cur_build_dir} --config={build_type}',
                    f'cmake --install {cur_build_dir} --config={build_type}'
                ],
                cwd = self.__module_dir
            )

    def build(self):
        self.__run_cmake()

def main():
    builder = builder_zlib()
    builder.build()

if(__name__ == "__main__"):
    main()

