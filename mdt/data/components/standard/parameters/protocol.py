from mdt.models.parameters import ProtocolParameterConfig

__author__ = 'Robbert Harms'
__date__ = "2015-12-12"
__maintainer__ = "Robbert Harms"
__email__ = "robbert.harms@maastrichtuniversity.nl"


"""The protocol parameters

The type of these parameters signifies that the data for this parameter should come from the protocol defined in the
model data. These will never be optimized and are always set to the data defined in the protocol.

Please choose the parameter type for a model and parameter carefully since the type signifies how the parameter and
its data are handled during model construction.

"""


class g(ProtocolParameterConfig):
    name = 'g'
    data_type = 'mot_float_type4'


class b(ProtocolParameterConfig):
    name = 'b'


class G(ProtocolParameterConfig):
    name = 'G'


class Delta(ProtocolParameterConfig):
    name = 'Delta'


class delta(ProtocolParameterConfig):
    name = 'delta'


class q(ProtocolParameterConfig):
    name = 'q'


class TE(ProtocolParameterConfig):
    name = 'TE'


class TM(ProtocolParameterConfig):
    name = 'TM'


class Ti(ProtocolParameterConfig):
    name = 'Ti'


class TR(ProtocolParameterConfig):
    name = 'TR'


class flip_angle(ProtocolParameterConfig):
    name = 'flip_angle'


class FA1(ProtocolParameterConfig):
    name = 'FA1'


class FA2(ProtocolParameterConfig):
    name = 'FA2'


class FA3(ProtocolParameterConfig):
    name = 'FA3'


class SEf(ProtocolParameterConfig):
    name = 'SEf'
