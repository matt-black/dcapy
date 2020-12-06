dcapy
---

DEPRECATED: you probably shouldn't use this. the code is useful, but I'm not working on it anymore. 

A Python library for Decision Curve Analysis

## Decision Curve Analysis

"Decision curve analysis is a simple method for evaluating prediction models, diagnostic tests, and molecular markers."

The algorithms in this library were originally developed by [Dr. Andrew Vickers](http://www.mskcc.org/research/epidemiology-biostatistics/health-outcomes/staff/andrew-vickers) at Memorial Sloan Kettering Cancer Center. 
I'm just a guy who re-implemented the algorithms in Python. 

For more information on decision curve analysis, see [here](http://www.mskcc.org/research/epidemiology-biostatistics/health-outcomes/decision-curve-analysis-0). 

## Installing

End users can install via pip:

	pip install dcapy

Developers can install via git/pip:

	git clone https://github.com/matt-black/dcapy.git
	cd dcapy
	pip install -r requirements.txt

## Run Tests

Tests are held in the /test folder, along with resources
To run the tests, run the following command from this project's root directory:
	
	python -m unittest discover

## Using dcapy

See example IPython notebooks in the `/example` folder. 

After installing, import dcapy as:

	import dcapy

## License

GPLv3
