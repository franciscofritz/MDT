from mdt.components_loader import bind_function
from mdt.models.compartments import CompartmentConfig

__author__ = 'Robbert Harms'
__date__ = "2015-06-21"
__maintainer__ = "Robbert Harms"
__email__ = "robbert.harms@maastrichtuniversity.nl"


class Zeppelin(CompartmentConfig):

    parameter_list = ('g', 'b', 'd', 'dperp0', 'theta', 'phi')
    cl_code = '''
        return exp(-b *
                    (((d - dperp) *
                          pown(dot(g, (mot_float_type4)(cos(phi) * sin(theta),
                                                        sin(phi) * sin(theta), cos(theta), 0.0)), 2)
                    ) + dperp));
    '''

    @bind_function
    def get_extra_results_maps(self, results_dict):
        return self._get_vector_result_maps(results_dict[self.name + '.theta'],
                                            results_dict[self.name + '.phi'])
