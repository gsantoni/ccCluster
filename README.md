# ccCluster

Welcome to ccCluster
Developed at the ESRF by Gianluca Santoni

This program is used to run hierarchycal cluster analysis on protein diffraction data.
When using, please cite:

Santoni, G., Zander, U., Mueller-Dieckmann, C., Leonard, G. & Popov, A. (2017). J. Appl. Cryst. 50,
https://doi.org/10.1107/S1600576717015229.

## Installation
Once downloaded, the program runs if all dependencies are met and if you have libtbx.python in your path.
You can then add an alias to run the ccCluster.py executable.

## Basic Usage
ccCluster must receive, the first time you run it for a project, a list of HKL files.
To do this, you can simply call
ccCluster -f <FILE1>.HKL ... <FILEn>.HKL

if no file is specified, it will walk all the subdirectories of the current folder and look for HKL files.


## Dependencies are:

PyQt5
cctbx
matplotlib
numpy

