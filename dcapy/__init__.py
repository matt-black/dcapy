import dcapy.algo as algo

class DecisionCurveAnalysis:
    """
    """
    
    #universal parameters for DCA
    data = None  # the data set to use
    outcome = None
    predictors = None  
    #threshold boundaries
    thresh_lb = 0.01
    thresh_ub = 0.99
    thresh_step = 0.01
    #metrics for the predictors
    probability = None
    harm = None
    #other metrics
    intervention_per = 100

    #stdca-specific attributes
    tt_outcome = None
    time_point = None
    cmp_risk = False

    def __init__(self, algorithm='dca', **kwargs):
        valid_keywords = None
        if algorithm == 'dca':
            from dcapy.validate import dca_keywords
            valid_keywords = dca_keywords
            self.algo = algo.dca
        elif algorithm == 'stdca':
            from dcapy.validate import stdca_keywords
            valid_keywords = stdca_keywords
            self.algo = algo.stdca

        #set attributes based on keywords passed in
        for kw in kwargs:
            try:  # to set the attribute matching that keyword
                setattr(self, kw, kwargs[kw])
            except AttributeError as e:
                raise ValueError("{kw} is not a valid keyword for DCA"
                                 .format(kw=repr(kw)))

    def run(self, return_results=False):
        """Performs the analysis

        Parameters
        ----------
        return_results : bool
            if `True`, sets the results to the instance attribute `results`
            if `False`, the function returns the results as a tuple

        Returns
        -------
        tuple(pd.DataFrame, pd.DataFrame)
            Returns net_benefit, interventions_avoided if `return_results=True`
        """
        nb, ia = self.algo(self.data, self.outcome, self.predictors,
                           self.thresh_lb, self.thresh_ub, self.thresh_step,
                           self.probability, self.harm, self.intervention_per)
        if return_results:
            return nb, ia
        else:
            self.results = {'net benefit' : nb, 'interventions avoided' : ia}
    
    def plot_net_benefit(self, custom_axes=None, make_legend=True):
        """Plots the net benefit from the analysis

        Parameters
        ----------

        Returns
        -------
        """
        import matplotlib.pyplot as plt
        try:
            net_benefit = getattr(self, 'results')
        except AttributeError:
            raise DCAError("must run analysis before plotting!")
        nbplot = plt.plot(net_benefit)
        #TODO: graph prettying/customization
        return nbplot

    def plot_interventions_avoided(self, custom_axes=None, make_legend=True):
        """Plots the interventions avoided per `interventions_per` patients

        Parameters
        ----------

        Returns
        -------

        """
        import matplotlib.pyplot as plt
        try:
            interv_avoid = getattr(self, 'results')
        except AttributeError:
            raise DCAError("must run analysis before plotting!")
        iaplot = plt.plot(interv_avoid)
        #TODO: graph prettying/customization
        return iaplot


class DCAError(Exception):
    pass