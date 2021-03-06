#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
"""Generate a protocol from a bvec and bval file.

MDT uses a protocol file (with extension .prtcl) to store all the acquisition related values.
This is a column based file which can hold, next to the b-values and gradient directions,
the big Delta, small delta, gradient amplitude G and more of these extra acquisition details.
"""
import argparse
import os
from argcomplete.completers import FilesCompleter
import textwrap
import mdt.protocols
from mdt.shell_utils import BasicShellApplication, get_citation_message
from mdt.protocols import load_bvec_bval

__author__ = 'Robbert Harms'
__date__ = "2015-08-18"
__maintainer__ = "Robbert Harms"
__email__ = "robbert.harms@maastrichtuniversity.nl"


class GenerateProtocol(BasicShellApplication):

    def __init__(self):
        mdt.init_user_settings(pass_if_exists=True)

    def _get_arg_parser(self):
        description = textwrap.dedent(__doc__)
        description += get_citation_message()

        epilog = textwrap.dedent("""
        Examples of use:
            mdt-generate-protocol data.bvec data.bval
            mdt-generate-protocol data.bvec data.bval -o my_protocol.prtcl
            mdt-generate-protocol data.bvec data.bval
            mdt-generate-protocol data.bvec data.bval --Delta 30 --delta 20
            mdt-generate-protocol data.bvec data.bval --sequence-timing-units 's' --Delta 0.03
            mdt-generate-protocol data.bvec data.bval --TE ../my_TE_file.txt
        """)

        parser = argparse.ArgumentParser(description=description, epilog=epilog,
                                         formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument('bvec', help='the gradient vectors file').completer = FilesCompleter()
        parser.add_argument('bval', help='the gradient b-values').completer = FilesCompleter()
        parser.add_argument('-s', '--bval-scale-factor', type=float,
                            help="We expect the b-values in the output protocol in units of s/m^2. "
                                 "Example use: 1 or 1e6. The default is autodetect.")

        parser.add_argument('-o', '--output_file',
                            help='the output protocol, defaults to "<bvec_name>.prtcl" in the same '
                                 'directory as the bvec file.').completer = FilesCompleter()

        parser.add_argument('--sequence-timing-units', choices=('ms', 's'), default='ms',
                            help="The units of the sequence timings. The default is 'ms' which we will convert to 's'.")

        parser.add_argument('--G',
                            help="The gradient amplitudes in T/m.")

        parser.add_argument('--maxG',
                            help="The maximum gradient amplitude in T/m. This is only useful if we need to guess "
                                 "big Delta and small delta. Default is 0.04 T/m")

        parser.add_argument('--Delta',
                            help="The big Delta to use, either a single number or a file with either a single number "
                                 "or one number per gradient direction.")

        parser.add_argument('--delta',
                            help="The small delta to use, either a single number or a file with either a single number "
                                 "or one number per gradient direction.")

        parser.add_argument('--TE',
                            help="The TE to use, either a single number or a file with either a single number "
                                 "or one number per gradient direction.")

        parser.add_argument('--TR',
                            help="The TR to use, either a single number or a file with either a single number "
                                 "or one number per gradient direction.")

        return parser

    def run(self, args):
        bvec = os.path.realpath(args.bvec)
        bval = os.path.realpath(args.bval)

        if args.output_file:
            output_prtcl = os.path.realpath(args.output_file)
        else:
            output_prtcl = os.path.join(os.path.dirname(bvec),
                                        os.path.splitext(os.path.basename(bvec))[0] + '.prtcl')

        if args.bval_scale_factor:
            bval_scale_factor = float(args.bval_scale_factor)
        else:
            bval_scale_factor = 'auto'

        protocol = load_bvec_bval(bvec=bvec, bval=bval, bval_scale=bval_scale_factor)

        if args.G is None and args.maxG is not None:
            if os.path.isfile(str(args.maxG)):
                protocol.add_column_from_file('maxG', os.path.realpath(str(args.maxG)), 1)
            else:
                protocol.add_column('maxG', float(args.maxG))

        if args.Delta is not None:
            add_sequence_timing_column_to_protocol(protocol, 'Delta', args.Delta, args.sequence_timing_units)
        if args.delta is not None:
            add_sequence_timing_column_to_protocol(protocol, 'delta', args.delta, args.sequence_timing_units)
        if args.TE is not None:
            add_sequence_timing_column_to_protocol(protocol, 'TE', args.TE, args.sequence_timing_units)
        if args.TR is not None:
            add_sequence_timing_column_to_protocol(protocol, 'TR', args.TR, args.sequence_timing_units)
        if args.G is not None:
            add_column_to_protocol(protocol, 'G', args.G, 1)

        mdt.protocols.write_protocol(protocol, output_prtcl)


def add_column_to_protocol(protocol, column, value, mult_factor):
    if value is not None:
        if os.path.isfile(value):
            protocol.add_column_from_file(column, os.path.realpath(value), mult_factor)
        else:
            protocol.add_column(column, float(value) * mult_factor)


def add_sequence_timing_column_to_protocol(protocol, column, value, units):
    mult_factor = 1e-3 if units == 'ms' else 1
    add_column_to_protocol(protocol, column, value, mult_factor)


if __name__ == '__main__':
    GenerateProtocol().start()
