from mdt.models.compartments import CompartmentConfig

__author__ = 'Robbert Harms'
__date__ = "2015-06-21"
__maintainer__ = "Robbert Harms"
__email__ = "robbert.harms@maastrichtuniversity.nl"


class ExpT1DecTM(CompartmentConfig):

    parameter_list = ('TM', 'T1')
    cl_code = 'return exp( -TM / T1 );'
