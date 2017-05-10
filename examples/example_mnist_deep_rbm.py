from paysage import batch
from paysage import layers
from paysage.models import model
from paysage import fit
from paysage import optimizers
from paysage import backends as be

be.set_seed(137) # for determinism

import example_util as util

def example_mnist_deep_rbm(paysage_path=None, num_epochs=10, show_plot=False):
    num_hidden_units = 500
    batch_size = 50
    learning_rate = 0.01
    mc_steps = 1

    (_, _, shuffled_filepath) = \
            util.default_paths(paysage_path)

    # set up the reader to get minibatches
    data = batch.HDFBatch(shuffled_filepath,
                          'train/images',
                          batch_size,
                          transform=batch.binarize_color,
                          train_fraction=0.99)

    # set up the model and initialize the parameters
    vis_layer = layers.BernoulliLayer(data.ncols)
    hid_1_layer = layers.BernoulliLayer(num_hidden_units)
    hid_2_layer = layers.BernoulliLayer(num_hidden_units)

    rbm = model.Model([vis_layer, hid_1_layer, hid_2_layer])
    rbm.initialize(data)

    metrics = ['ReconstructionError', 'EnergyDistance', 'EnergyGap', 'EnergyZscore']
    perf = fit.ProgressMonitor(data, metrics=metrics)

    # set up the optimizer and the fit method
    opt = optimizers.ADAM(stepsize=learning_rate,
                          scheduler=optimizers.PowerLawDecay(0.1))

    sampler = fit.DrivenSequentialMC.from_batch(rbm, data,
                                                method='stochastic')

    cd = fit.SGD(rbm, data, opt, num_epochs, method=fit.pcd, sampler=sampler,
                 mcsteps=mc_steps, monitor=perf)

    # fit the model
    print('training with contrastive divergence')
    cd.train()

    # evaluate the model
    util.show_metrics(rbm, perf)
    util.show_reconstructions(rbm, data.get('validate'), fit, show_plot)
    util.show_fantasy_particles(rbm, data.get('validate'), fit, show_plot)
    util.show_weights(rbm, show_plot)

    # close the HDF5 store
    data.close()
    print("Done")

if __name__ == "__main__":
    example_mnist_deep_rbm(show_plot = False)