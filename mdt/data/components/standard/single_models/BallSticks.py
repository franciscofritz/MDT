import math
from mdt.components_loader import CompartmentModelsLoader
from mdt.models.single import DMRISingleModelBuilder, DMRISingleModel
from mot.evaluation_models import GaussianEvaluationModel, OffsetGaussianEvaluationModel
from mot.trees import CompartmentModelTree

__author__ = 'Robbert Harms'
__date__ = "2015-06-22"
__maintainer__ = "Robbert Harms"
__email__ = "robbert.harms@maastrichtuniversity.nl"


def get_components_list():
    models = []
    for x in range(1, 4):
        models.append(get_ball_sticks(x, invivo=True))
        models.append(get_ball_sticks(x, invivo=False))
    return models

compartments_loader = CompartmentModelsLoader()


def get_ball_sticks(nmr_sticks=1, invivo=True):
    name = 'Ball' + ('Stick' * nmr_sticks)
    if invivo:
        d_ani = 1.7e-9
        d_iso = 3.0e-9
        vivo_type = 'in-vivo'
    else:
        d_ani = 0.6e-9
        d_iso = 2.0e-9
        name += '-ExVivo'
        vivo_type = 'ex-vivo'

    description = 'The Ball and Stick model with {0} Sticks and with {1} defaults.'.format(nmr_sticks, vivo_type)

    def model_construction_cb(evaluation_model=GaussianEvaluationModel().fix('sigma', 1),
                              signal_noise_model=None):
        csf = (compartments_loader.get_class('Weight')('Wball'),
               compartments_loader.load('Ball').fix('d', d_iso),
               '*')

        if nmr_sticks == 1:
            ic = (compartments_loader.get_class('Weight')('Wstick'),
                  compartments_loader.load('Stick').fix('d', d_ani),
                  '*')
        else:
            ic = []
            for i in range(nmr_sticks):
                ic.append((compartments_loader.get_class('Weight')('Wstick' + repr(i)),
                           compartments_loader.get_class('Stick')('Stick' + repr(i)).fix('d', d_ani),
                           '*'))
            ic.append('+')

        ml = (compartments_loader.load('S0'), (csf, ic, '+'), '*')

        model = DMRISingleModel(name, CompartmentModelTree(ml), evaluation_model, signal_noise_model)
        modifiers = [('SNIF', lambda results: 1 - results['Wball.w'])]
        model.add_post_optimization_modifiers(modifiers)
        return model

    return [model_construction_cb,
            {'name': name,
             'in_vivo_suitable': invivo,
             'ex_vivo_suitable': not invivo,
             'description': description}]