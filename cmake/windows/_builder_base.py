#!/usr/bin/env python3

import abc

import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent)

from _configure_environment import environment

class builder_base(object):
    def __init__(self):
        self.env = environment()

    @abc.abstractmethod
    def build(self):
        pass
