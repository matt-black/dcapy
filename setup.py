#!/usr/bin/env python
"""
Setup script for the dcapy module

Author: Matthew Black
"""
from distutils.core import setup

setup(name='dcapy',
      version='0.1',
      description='Decision Curve Analysis library',
      license='GPLv3+',
      install_requires=[
          'pandas'
          ],
      author='Matthew Black',
      author_email='matt.black7@gmail.com',
      url='http://matt-black.github.io',
      keywords='statistics analysis',
      packages=['dcapy'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering :: Mathematics'
          ]
      )