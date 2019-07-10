
import matplotlib.pyplot as plt
from numpy import linspace, sqrt, pi, array
from numpy.random import normal, seed

from inference.mcmc import PcaChain

"""
This is a duplicate of /demos/spectroscopy_demo.py which produces
example figures for the documentation
"""



class SpectroPosterior(object):
    def __init__(self, wavelength, intensity, errors):
        self.x = wavelength
        self.y = intensity
        self.sigma = errors
        # Central wavelengths of the lines are known constants:
        self.c1 = 422.
        self.c2 = 428.

    def __call__(self, theta):
        return self.likelihood(theta) + self.prior(theta)

    def prior(self, theta):
        return 0.

    def likelihood(self, theta):
        return -0.5*sum( ((self.y - self.forward_model(self.x, theta)) / self.sigma)**2 )

    def forward_model(self, x, theta):
        # unpack the model parameters
        A1, w1, A2, w2, b0, b1 = theta
        # evaluate each term of the model
        peak_1 = (A1 / (pi*w1)) / (1 + ((x - self.c1)/w1)**2)
        peak_2 = (A2 / (pi*w2)) / (1 + ((x - self.c2)/w2)**2)
        d = (b1-b0)/(max(x) - min(x))
        background = d*x + (b0 - d*min(x))
        # return the prediction of the data
        return peak_1 + peak_2 + background




def build_plots():
    # Create some simulated data
    seed(9)
    N = 35
    x_data = linspace(410, 440, N)
    P = SpectroPosterior(x_data, None, None)
    theta = [1000, 2, 400, 1.5, 35, 25]
    y_data = P.forward_model(x_data, theta)
    errors = sqrt(y_data + 1) + 5
    y_data += normal(size = N) * errors




    # plot the simulated data we're going to use
    plt.errorbar(x_data, y_data, errors, marker = 'D', ls = 'none', markersize = 4)
    plt.plot(x_data, y_data, alpha = 0.5, c = 'C0', ls = 'dashed')
    plt.title('synthetic spectroscopy data')
    plt.xlabel('wavelength (nm)')
    plt.ylabel('intensity')
    plt.grid()
    plt.tight_layout()
    plt.savefig('spectroscopy_data.png')
    plt.close()
    print(' # spectroscopy data plot finished')

    # create the posterior object
    posterior = SpectroPosterior(x_data, y_data, errors)

    # create the markov chain object
    chain = PcaChain( posterior = posterior, start = [1000, 1, 1000, 1, 30, 30] )

    # generate a sample by advancing the chain
    chain.advance(50000)

    # we can check the status of the chain using the plot_diagnostics method
    chain.plot_diagnostics(show = False, filename = 'plot_diagnostics_example.png')
    print(' # diagnostics plot finished')
    # We can automatically set sensible burn and thin values for the sample
    chain.autoselect_burn_and_thin()

    # we can get a quick overview of the posterior using the matrix_plot
    # functionality of chain objects, which plots all possible 1D & 2D
    # marginal distributions of the full parameter set (or a chosen sub-set).
    chain.thin = 1
    chain.matrix_plot(show = False, filename = 'matrix_plot_example.png')
    print(' # matrix plot finished')
    # We can easily estimate 1D marginal distributions for any parameter
    # using the get_marginal method:
    w1_pdf = chain.get_marginal(1, unimodal = True)
    w2_pdf = chain.get_marginal(3, unimodal = True)

    # get_marginal returns a density estimator object, which can be called
    ax = linspace(0.2, 4., 1000)  # build an axis to evaluate the pdf estimates
    plt.plot(ax, w1_pdf(ax), label = 'peak #1 width marginal', lw = 2)  # plot estimates of each marginal PDF
    plt.plot(ax, w2_pdf(ax), label = 'peak #2 width marginal', lw = 2)
    plt.xlabel('peak width')
    plt.ylabel('probability density')
    plt.legend()
    plt.grid()
    plt.savefig('width_pdfs_example.png')
    plt.close()
    print(' # marginals plot finished')





    # what if instead we wanted a PDF for the ratio of the two widths?
    # get the sample for each width
    width_1 = chain.get_parameter(1)
    width_2 = chain.get_parameter(3)

    # make a new set of samples for the ratio
    widths_ratio = [i/j for i,j in zip(width_1, width_2)]

    # Use one of the density estimator objects from pdf_tools to get the PDF
    from inference.pdf_tools import UnimodalPdf
    pdf = UnimodalPdf(widths_ratio)

    # plot the PDF
    pdf.plot_summary(label = 'Peak widths ratio', show = False, filename = 'pdf_summary_example.png')
    print(' # widths ratio pdf plot finished')



    # You may also want to assess the level of uncertainty in the model predictions.
    # This can be done easily by passing each sample through the forward-model
    # and observing the distribution of model expressions that result.

    # generate an axis on which to evaluate the model
    M = 500
    x_fits = linspace(400, 450, M)
    # get the sample
    sample = chain.get_sample()
    # pass each through the forward model
    curves = array([posterior.forward_model(x_fits, theta) for theta in sample])

    # we can use the sample_hdi function from the pdf_tools module to produce highest-density
    # intervals for each point where the model is evaluated:
    from inference.pdf_tools import sample_hdi
    hdi_1sigma = array([sample_hdi(curves[:,i], 0.68, force_single = True) for i in range(curves.shape[1])])
    hdi_2sigma = array([sample_hdi(curves[:,i], 0.95, force_single = True) for i in range(curves.shape[1])])

    # construct the plot
    plt.figure(figsize = (8,5))
    # plot the 1 and 2-sigma highest-density intervals
    plt.fill_between(x_fits, hdi_2sigma[:, 0], hdi_2sigma[:, 1], color = 'red', alpha = 0.10, label = '2-sigma HDI')
    plt.fill_between(x_fits, hdi_1sigma[:, 0], hdi_1sigma[:, 1], color = 'red', alpha = 0.20, label = '1-sigma HDI')
    # plot the MAP estimate
    MAP = posterior.forward_model(x_fits, chain.mode())
    plt.plot(x_fits, MAP, c = 'red', lw = 2, ls = 'dashed', label = 'MAP estimate')
    # plot the data
    plt.plot(x_data, y_data, 'D', c = 'blue', markeredgecolor = 'black', markersize = 5, label = 'data')
    # configure the plot
    plt.xlabel('wavelength (nm)')
    plt.ylabel('intensity')
    plt.xlim([410, 440])
    plt.legend()
    plt.grid()
    plt.savefig('prediction_uncertainty_example.png')
    plt.close()
    print(' # model prediction plot finished')