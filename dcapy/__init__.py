import pandas as pd
import dcapy.algo as algo
import dcapy.validate as val
from dcapy.validate import DCAError

__all__ = ['DecisionCurveAnalysis']  # only public member should be the class

class DecisionCurveAnalysis:
    """DecisionCurveAnalysis(...)
        DecisionCurveAnalysis(algorithm='dca', **kwargs)

    Create an object of class DecisionCurveAnalysis for generating
    and plotting "net benefit" and "interventions avoided" curves
    
    Parameters
    ----------
    algorithm : str
        the type of analysis to run
        valid values are 'dca' (decision curve) or 'stdca' (survival time decision curve)
    **kwargs : object
        keyword arguments that are used in the analysis

    Attributes
    ----------
    data : pd.DataFrame
        The data set to analyze, with observations in each row, and
        outcomes/predictors in the columns
    outcome : str
        The column in `data` to use as the outcome for the analysis
        All observations in this column must be coded 0/1
    predictors : list(str)
        The column(s) in `data` to use as predictors during the analysis
        All observations, 'x', in this column must be in the range 0 <= x <= 1
    
    Methods
    -------
    run : runs the analysis
    smooth_results : use local regression (LOWESS) to smooth the
        results of the analysis, using the specified fraction
    plot_net_benefit : TODO
    plot_interv_avoid : TODO

    Examples
    --------
    TODO
    """
    #universal parameters for dca
    _common_args = {'data' : None,
                    'outcome' : None,
                    'predictors' : None,
                    'thresh_lo' : 0.01,
                    'thresh_hi' : 0.99,
                    'thresh_step' : 0.01,
                    'probabilities' : None,
                    'harms' : None,
                    'intervention_per' : 100}  
    
    #stdca-specific attributes
    _stdca_args = {'tt_outcome' : None,
                   'time_point' : None,
                   'cmp_risk' : False}
    
    def __init__(self, algorithm='dca', **kwargs):
        """Initializes the DecisionCurveAnalysis object

        Arguments for the analysis may be passed in as keywords upon object initialization

        Parameters
        ----------
        algorithm : str
            the algorithm to use, valid options are 'dca' or 'stdca'
        **kwargs : 
            keyword arguments to populate instance attributes that will be used in analysis

        Raises
        ------
        ValueError
            if user doesn't specify a valid algorithm; valid values are 'dca' or 'stdca'
            if the user specifies an invalid keyword
        """
        if algorithm not in ['dca', 'stdca']:
            raise ValueError("did not specify a valid algorithm, only 'dca' and 'stdca' are valid")
        self.algorithm = algorithm

        #set args based on keywords passed in
        #this naively assigns values passed in -- validation occurs afterwords
        for kw in kwargs:
            if kw in self._common_args:
                self._common_args[kw] = kwargs[kw]  #assign
                continue
            elif kw in self._stdca_args:
                self._stdca_args[kw] = kwargs[kw]
            else:
                raise ValueError("{kw} is not a valid DCA keyword"
                                 .format(kw=repr(kw)))

        #do validation on all args, make sure we still have a valid analysis
        self.data = val.data_validate(self.data)
        self.outcome = val.outcome_validate(self.data, self.outcome)
        self.predictors = val.predictors_validate(self.predictors, self.data)
        #validate bounds
        new_bounds = []
        curr_bounds = [self._common_args['thresh_lo'], self._common_args['thresh_hi'],
                       self._common_args['thresh_step']]
        for i, bound in enumerate(['lower', 'upper', 'step']):
            new_bounds.append(val.threshold_validate(bound, self.threshold_bound(bound),
                                                     curr_bounds))
        self.set_threshold_bounds(new_bounds[0], new_bounds[1], new_bounds[2])
        #validate predictor-reliant probs/harms
        self.probabilities = val.probabilities_validate(self.probabilities,
                                                        self.predictors)
        self.harms = val.harms_validate(self.harms, self.predictors)
        #validate the data in each predictor column
        self.data = val.validate_data_predictors(self.data, self.outcome, self.predictors,
                                                 self.probabilities)
                
    def _args_dict(self):
        """Forms the arguments to pass to the analysis algorithm

        Returns
        -------
        dict(str, object)
            A dictionary that can be unpacked and passed to the algorithm for the
            analysis
        """
        if self.algorithm == 'dca':
            return self._common_args
        else:
            from collections import Counter
            return dict(Counter(self._common_args) + Counter(self._stdca_args))

    def _algo(self):
        """The algorithm to use for this analysis
        """
        return algo.dca if self.algorithm == 'dca' else algo.stdca
            
    def run(self, return_results=False):
        """Performs the analysis

        Parameters
        ----------
        return_results : bool
            if `True`, sets the results to the instance attribute `results`
            if `False` (default), the function returns the results as a tuple

        Returns
        -------
        tuple(pd.DataFrame, pd.DataFrame)
            Returns net_benefit, interventions_avoided if `return_results=True`
        """
        nb, ia = self._algo()(**(self._args_dict()))
        if return_results:
            return nb, ia
        else:
            self.results = {'net benefit' : nb, 'interventions avoided' : ia}
    
    def smooth_results(self, lowess_frac, return_results=False):
        """Smooths the results using a LOWESS smoother
        
        Parameters
        ----------
        lowess_frac : float
            the fraction of the endog value to use when smoothing
        return_results : bool
            if `True`, sets the results to the instance attribute `results`
            if `False` (default), the function returns the results as a tuple
        
        Returns
        -------
        tuple(pd.DataFrame, pd.DataFrame)
            smoothed predictor dataFrames for results if `return_results=True`
        """
        from dcapy.calc import lowess_smooth_results
        _nb = _ia = None
        for predictor in self.predictors:
            nb, ia = lowess_smooth_results(predictor, self.results['net benefit'],
                                           self.results['interventions avoided'],
                                           lowess_frac)
            #concatenate results
            _nb = pd.concat([_nb, nb], axis=1)
            _ia = pd.concat([_ia, ia], axis=1)
        if return_results:
            return _nb, _ia
        else:
            self.results['net benefit'] = pd.concat(
                [self.results['net benefit'], _nb], axis=1)
            self.results['interventions avoided'] = pd.concat(
                [self.results['interventions avoided'], _ia], axis=1)

    def plot_net_benefit(self, custom_axes=None, make_legend=True):
        """Plots the net benefit from the analysis

        Parameters
        ----------
        custom_axes : list(float)
            a length-4 list of dimensions for the plot, `[x_min, x_max, y_min, y_max]`
        make_legend : bool
            whether to include a legend in the plot

        Returns
        -------
        matplotlib.rc_context

        """
        try:
            import matplotlib.pyplot as plt
        except ImportError as e:
            e.args += ("plotting the analysis requires matplotlib")
            raise
            
        try:
            net_benefit = getattr(self, 'results')['net benefit']
        except AttributeError:
            raise DCAError("must run analysis before plotting!")
        
        plt.plot(net_benefit)
        plt.ylabel("Net Benefit")
        plt.xlabel("Threshold Probability")
        #prettify the graph
        if custom_axes:
            plt.axis(custom_axes)
        else:  #use default
            plt.axis([0, self.threshold_bound('upper')*100,
                      -0.05, 0.20])
        

    def plot_interventions_avoided(self, custom_axes=None, make_legend=True):
        """Plots the interventions avoided per `interventions_per` patients

        Notes
        -----
        Generated plots are 'interventions avoided per `intervention_per` patients' vs. threshold

        Parameters
        ----------
        custom_axes : list(float)
            a length-4 list of dimensions for the plot, `[x_min, x_max, y_min, y_max]`
        make_legend : bool
            whether to include a legend in the plot

        Returns
        -------
        matplotlib.rc_context
            context manager for working with the newly-created plot
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError as e:
            e.args += ("plotting the analysis requires matplotlib")
            raise

        try:
            interv_avoid = getattr(self, 'results')['interventions avoided']
        except AttributeError:
            raise DCAError("must run analysis before plotting!")
        iaplot = plt.plot(interv_avoid)
        #TODO: graph prettying/customization
        return iaplot
    
    @property
    def data(self):
        """The data set to analyze

        Returns
        -------
        pd.DataFrame
        """
        return self._common_args['data']

    @data.setter
    def data(self, value):
        """Set the data for the analysis

        Parameters
        ----------
        value : pd.DataFrame
            the data to analyze
        """
        value = val.data_validate(value)  # validate
        self._common_args['data'] = value

    @property
    def outcome(self):
        """The outcome to use for the analysis
        """
        return self._common_args['outcome']

    @outcome.setter
    def outcome(self, value):
        """Sets the column in the dataset to use as the outcome for the analysis
        
        Parameters
        ----------
        value : str
            the name of the column in `data` to set as `outcome`
        """
        value = val.outcome_validate(self.data, value)  # validate
        self._common_args['outcome'] = value

    @property
    def predictors(self):
        """The predictors to use

        Returns
        -------
        list(str)
            A list of all predictors for the analysis
        """
        return self._common_args['predictors']

    @predictors.setter
    def predictors(self, value):
        """Sets the predictors to use for the analysis

        Parameters
        ----------
        value : list(str)
            the list of predictors to use
        """
        value = val.predictors_validate(value, self.data)
        self._common_args['predictors'] = value

    def threshold_bound(self, bound):
        """Gets the specified threshold boundary

        Parameters
        ----------
        bound : str
            the boundary to get; valid values are "lower", "upper", or "step"

        Returns
        -------
        float
            the current value of that boundary
        """
        mapping = {'lower' : 'thresh_lo',
                   'upper' : 'thresh_hi',
                   'step' : 'thresh_step'}
        try:
            return self._common_args[mapping[bound]]
        except KeyError:
            raise ValueError("did not specify a valid boundary")

    def set_threshold_bounds(self, lower, upper, step=None):
        """Sets the threshold boundaries (thresh_*) for the analysis

        Notes
        -----
        Passing `None` for any of the parameters will skip that parameter
        The analysis will be run over all steps, x, lower <= x <= upper

        Parameters
        ----------
        lower : float
            the lower boundary
        upper : float
            the upper boundary
        step : float
            the increment between calculations
        """
        _step = step if step else self._common_args['thresh_step']
        bounds_to_test = [lower, upper, _step]

        if lower is not None:
            lower = val.threshold_validate('lower', lower, bounds_to_test)
            self._common_args['thresh_lo'] = lower
        if upper is not None:
            upper = val.threshold_validate('upper', upper, bounds_to_test)
            self._common_args['thresh_hi'] = upper
        if step is not None:
            step = val.threshold_validate('step', step, bounds_to_test)
            self._common_args['thresh_step'] = step

    @property
    def probabilities(self):
        """The list of probability values for each predictor

        Returns
        -------
        list(bool)
            the probability list
        """
        return self._common_args['probabilities']

    @probabilities.setter
    def probabilities(self, value):
        """Sets the probabilities list for the analysis

        Notes
        -----
        The length of the parameter `value` must match that of the predictors

        Parameters
        ----------
        value : list(bool)
            a list of probabilities to assign, one for each predictor
        """
        value = val.probabilities_validate(value, self.predictors)
        self._common_args['probabilities'] = value

    def set_probability_for_predictor(self, predictor, probability):
        """Sets the probability value for the given predictor

        Parameters
        ----------
        predictor : str
            the predictor to set the probability value for
        probability : bool
            the probability value
        """
        try:  # make sure we're setting a valid predictor
            ind = self._common_args['predictors'].index(predictor)
        except ValueError as e:
            e.args += ("did not specify a valid predictor")
            raise
        self._common_args['probabilities'][ind] = probability

    @property
    def harms(self):
        """The list of harm values for the predictors

        Returns
        -------
        list(float)
        """
        return self._common_args['harms']

    @harms.setter
    def harms(self, value):
        """Sets the list of harm values to be used

        Notes
        -----
        The length of the parameter `value` must match that of the predictors

        Parameters
        ----------
        value : list(float)
            a list of floats to assign, one for each predictor
        """
        value = val.harms_validate(value, self.predictors)  # validate
        self._common_args['harms'] = value

    def set_harm_for_predictor(self, predictor, harm):
        """Sets the harm value for the given predictor

        Parameters
        ----------
        predictor : str
            the predictor to set the harm value for
        harm : float
            the harm value (must be between 0 and 1)
        """
        try:  # make sure specifying a valid predictor
            ind = self._common_args['harm'].index(predictor)
        except ValueError as e:
            e.args += ("did not specify a valid predictor")
            raise
        self._common_args['harm'][ind] = harm

    @property
    def intervention_per(self):
        """The number of patients per intervention

        Returns
        -------
        int
        """
        return self._common_args['intervention_per']

    @intervention_per.setter
    def intervention_per(self, value):
        """Sets the value of the number of patients to assume per intervention

        Parameters
        ----------
        value : int
        """
        self._common_args['intervention_per'] = value

    @property
    def time_to_outcome(self):
        """The column in the data used to specify the time taken to reach the outcome
        
        Returns
        -------
        str
        """
        return self._common_args['tt_outcome']

    @time_to_outcome.setter
    def time_to_outcome(self, value):
        """Sets the column to use as the `tt_outcome` for the analysis

        Parameters
        ----------
        value : str
        """
        if value in data.columns:
            self._stdca_args['tt_outcome'] = value
        else:
            raise ValueError("time to outcome must be a valid column in the data set")

    @property
    def time_point(self):
        """The time point of interest

        Returns
        -------
        float
        """
        return self._stdca_args['time_point']

    @time_point.setter
    def time_point(self, value):
        """Sets the time point of interest

        Parameters
        ----------
        value : float
        """
        self._stdca_args['time_point'] = value

    @property
    def competing_risk(self):
        """Run competing risk analysis

        Returns
        -------
        bool
        """
        return self._stdca_args['cmp_risk']

    @competing_risk.setter
    def competing_risk(self, value):
        """Sets whether to run a competing risk analysis

        Parameters
        ----------
        value : bool
        """
        if not isinstance(value, bool):
            raise TypeError("competing risk must be a boolean value")
        self._stdca_args['cmp_risk'] = value