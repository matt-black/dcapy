#!/usr/bin/env python
"""
Setup script for the dcapy module

Author: Matthew Black
"""
from setuptools import setup, find_packages
from os import path

this_dir = path.abspath(path.dirname(__file__))

with open(path.join(this_dir, "DESCRIPTION.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(name='dcapy',

      version='0.1',

      description='Decision Curve Analysis library',
      long_description=long_description,

      license='GPLv3+',
      install_requires=[
          'pandas',
          'statsmodels'
          ],

      author='Matthew Black',
      author_email='matt.black7@gmail.com',
      url='http://matt-black.github.io',

      packages=find_packages(exclude=['test']),

      keywords='statistics analysis',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering :: Mathematics'
          ]
      )
