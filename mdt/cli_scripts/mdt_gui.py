#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
"""Launches the MDT Graphical User Interface."""
import argparse
import os
import textwrap

from argcomplete.completers import FilesCompleter

from mdt import init_user_settings
from mdt.gui.model_fit.qt_main import start_gui
from mdt.shell_utils import BasicShellApplication, get_citation_message

__author__ = 'Robbert Harms'
__date__ = "2015-08-18"
__maintainer__ = "Robbert Harms"
__email__ = "robbert.harms@maastrichtuniversity.nl"


class GUI(BasicShellApplication):

    def __init__(self):
        init_user_settings(pass_if_exists=True)

    def _get_arg_parser(self):
        description = textwrap.dedent(__doc__)
        description += get_citation_message()

        parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('-d', '--dir', metavar='dir', type=str, help='the base directory for the file choosers',
                            default=None).completer = FilesCompleter()
        return parser

    def run(self, args):
        if args.dir:
            cwd = os.path.realpath(args.dir)
        else:
            cwd = os.getcwd()

        start_gui(cwd)

if __name__ == '__main__':
    GUI().start()
