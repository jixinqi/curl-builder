#!/usr/bin/env python3

import http.client
import ssl
import shutil 

import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent / "cmake" / "windows"))

from _configure_environment import environment
from _builder_base          import builder_base

from builder_openssl        import builder_openssl
from builder_libpsl         import builder_libpsl
from builder_zlib           import builder_zlib

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
        builder_openssl_obj = builder_openssl()
        builder_openssl_obj.build()

        builder_zlib_obj = builder_zlib()
        builder_zlib_obj.build()

        builder_libpsl_obj = builder_libpsl()
        builder_libpsl_obj.build()

    def __download_cacert_pem(self, download_dir:pathlib.Path):
        host = "curl.se"
        path = "/ca/cacert.pem"
        output_file = download_dir / "cacert.pem"

        context = ssl.create_default_context()
        conn = http.client.HTTPSConnection(host, context=context)
        conn.request("GET", path)

        response = conn.getresponse()

        if(response.status == 200):
            with open(output_file, "wb") as f:
                f.write(response.read())
        conn.close()

        return output_file

    def __run_cmake(self):
        build_dir        = self.__project_dir / "__build"
        install_dir      = self.__project_dir / "__install"

        curl_build_dir   = self.__project_dir / "__build"   / "curl"
        curl_install_dir = self.__project_dir / "__install" / "curl"

        cacert_pem_path = self.__download_cacert_pem(build_dir)

        for build_type in ["Debug", "Release"]:
            cur_build_dir = curl_build_dir / build_type
            self.env.run_commands(
                commands = [
                    f'cmake -B        {cur_build_dir}'
                        f' -DCMAKE_INSTALL_PREFIX='    f'"{ curl_install_dir / build_type }"'
                        f' -DBUILD_STATIC_LIBS='       f'ON'

                        f' -DCURL_CA_BUNDLE='          f'"./{cacert_pem_path.name}"'
                        f' -DCURL_USE_OPENSSL='        f'ON'
                        f' -DOPENSSL_ROOT_DIR='        f'"{ install_dir / "openssl" / build_type }"'

                        f' -DLIBPSL_INCLUDE_DIR='      f'"{ install_dir / "libpsl"  / build_type / "include" }"'
                        f' -DLIBPSL_LIBRARY='          f'"{ install_dir / "libpsl"  / build_type / "lib" / "psl.lib" }"'
                        f' -DLIBPSL_CFLAGS='           f'"-DPSL_API="'

                        f' -DZLIB_INCLUDE_DIR='        f'"{ install_dir / "zlib"    / build_type / "include" }"'
                        f' -DZLIB_LIBRARY='            f'"{ install_dir / "zlib"    / build_type / "lib" / ("zsd.lib" if (build_type == "Debug") else "zs.lib") }"',
                    f'cmake --build   { cur_build_dir } --config={ build_type }',
                    f'cmake --install { cur_build_dir } --config={ build_type }'
                ],
                cwd = self.__module_dir
            )

            shutil.copy(cacert_pem_path, curl_install_dir / build_type / "bin" / cacert_pem_path.name)

    def build(self):
        # self.__build_submodules()
        self.__run_cmake()


def main():
    builder = builder_curl()
    builder.build()

if(__name__ == "__main__"):
    main()

