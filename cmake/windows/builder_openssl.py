#!/usr/bin/env python3

import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent)

from _configure_environment import environment
from _builder_base          import builder_base

class builder_openssl(builder_base):
    def __init__(self):
        super().__init__()
        self.__project_dir = pathlib.Path(__file__).parent.parent.parent
        self.__module_dir  = self.__project_dir / "third_party" / "openssl"
        if(
            not self.__module_dir.exists() or
            not self.__module_dir.is_dir()
        ):
            raise

    def __run_make(self):
        build_dir   = self.__project_dir / "__build"   / "openssl"
        install_dir = self.__project_dir / "__install" / "openssl"

        for build_type in ["Debug", "Release"]:
            configure_buid_type_param = ""
            if(build_type == "Debug"):
                configure_buid_type_param = "--debug"

            self.env.run_commands(
                commands = [
                    f'git reset --hard',
                    f'git clean -f -d',
                    f'perl Configure VC-WIN64A {configure_buid_type_param} no-shared'
                        f' --prefix="{install_dir / build_type}"'
                        f' --openssldir="{install_dir / build_type / "ssl"}"',
                    f'set CL=/MP',
                    f'nmake',
                    # f'nmake test',
                    f'nmake install',
                ],
                cwd = self.__module_dir
            )

    def build(self):
        self.__run_make()

def main():
    builder = builder_openssl()
    builder.build()

if(__name__ == "__main__"):
    main()

