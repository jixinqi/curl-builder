#!/usr/bin/env python3

import os
import pathlib
import subprocess

class environment:
    def __init__(self):
        self.__env = None
        self.__update_vcvarsall_env()

    def __update_vcvarsall_env(self):
        process_vswhere = subprocess.run(
            [
                "%ProgramFiles(x86)%/Microsoft Visual Studio/Installer/vswhere.exe",
                "-latest",
                "-products", "*",
                "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                "-property", "installationPath"
            ],
            shell=True,
            capture_output = True,
            text = True
        )
        process_vswhere_stdout_buffer = process_vswhere.stdout
        
        vcvars64_bat_dir_path = pathlib.Path(process_vswhere_stdout_buffer.strip()) / "VC" / "Auxiliary" / "Build"
        self.__env = os.environ.copy()
        self.__env["PATH"] = f"{self.__env["PATH"]};{vcvars64_bat_dir_path};"

    def run_commands(self, commands:list[str], cwd):
        for command in commands:
            temp_process = subprocess.run(
                f"vcvars64.bat && {command}",
                shell=True,
                env=self.__env,
                cwd=cwd
            )

if(__name__ == "__main__"):
    os._exit(1)
