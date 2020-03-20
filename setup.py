__author__ = "Gianluca Santoni"
__copyright__ = "Copyright 2015-2020"
__credits__ = ["Gianluca Santoni, Alexander Popov"]
__license__ = ""
__version__ = "1.0"
__maintainer__ = "Gianluca Santoni"
__email__ = "gianluca.santoni@esrf.fr"
__status__ = "Beta"


from setuptools import setup, find_packages

setup(name="ccCLuster",
      version="1.0",
      description='Hierarchical cluster analysis for MX',
      author='Gianluca Santoni',
      packages=["ccCluster"],
      setup_requires=['setuptools'],
      install_requires=[
          'numpy',
          'scipy',
          'pathos',
          'matplotlib',
          'PyQt5'],  # TODO: iotbx, cctbx
      entry_points={
          'console_scripts': [
              'ccCalc = ccCluster.ccCalc:main',
              'ccCluster = ccCluster.ccCluster:main',
			  'ccCluster-gui=ccCluster.ccCluster-gui:main'],
          },
      )
