# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='duplicateDetector',
      version='1.0',
      description='Efficient implementation to compute pairs with the lowest\
      levenshtein distance in a list of excel data',
      url='https://github.com/austrian-code-wizard/DuplicateDetection',
      author='Moritz Stephan',
      author_email='moritz.stephan@stanford.edu',
      license='MIT',
      packages=['duplicateDetector'],
      install_requires=[
          'pylev', 'pandas', 'pyjarowinkler', 'scipy', 'numpy', 'scikit-learn', 'sklearn', 'xlrd', 'cython',
            'sparse-dot-topn', 'networkx', 'flask'],
      zip_safe=False)

