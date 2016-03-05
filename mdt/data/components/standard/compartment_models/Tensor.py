import numpy as np

from mdt.components_loader import bind_function
from mdt.models.compartments import CompartmentConfig
from mdt.cl_routines.mapping.dti_measures import DTIMeasures
from mdt.utils import eigen_vectors_from_tensor
from mot import runtime_configuration

__author__ = 'Robbert Harms'
__date__ = "2015-06-21"
__maintainer__ = "Robbert Harms"
__email__ = "robbert.harms@maastrichtuniversity.nl"


class Tensor(CompartmentConfig):

    name = 'Tensor'
    cl_function_name = 'cmTensor'
    parameter_list = ('g', 'b', 'd', 'dperp0', 'dperp1', 'theta', 'phi', 'psi')

    @bind_function
    def get_extra_results_maps(self, results_dict):
        eigen_vectors = eigen_vectors_from_tensor(results_dict[self.name + '.theta'], results_dict[self.name + '.phi'],
                                                  results_dict[self.name + '.psi'])

        eigen_values = np.squeeze(np.concatenate([m[..., None] for m in [results_dict[self.name + '.d'],
                                                                         results_dict[self.name + '.dperp0'],
                                                                         results_dict[self.name + '.dperp1']]], axis=1))

        ranking = np.squeeze(np.argsort(eigen_values, axis=1)[:, ::-1])

        voxels_listing = np.arange(ranking.shape[0])
        sorted_eigen_values = [eigen_values[voxels_listing, ranking[:, ind]] for ind in range(ranking.shape[1])]

        extra_maps = {self.name + '.eigen_ranking': ranking}
        for ind in range(3):
            extra_maps.update({self.name + '.vec' + repr(ind): eigen_vectors[:, ind, :]})

            for dimension in range(3):
                extra_maps.update({self.name + '.vec' + repr(ind) + '_' + repr(dimension):
                                   eigen_vectors[:, ind, dimension]})

        dti_measures = DTIMeasures(runtime_configuration.runtime_config['cl_environments'],
                                   runtime_configuration.runtime_config['load_balancer'])

        fa, md = dti_measures.concat_and_calculate(eigen_values[:, 0], eigen_values[:, 1], eigen_values[:, 2])

        extra_maps.update({self.name + '.FA': fa,
                           self.name + '.MD': md,
                           self.name + '.AD': sorted_eigen_values[0],
                           self.name + '.RD': (sorted_eigen_values[1] + sorted_eigen_values[2]) / 2})

        return extra_maps
