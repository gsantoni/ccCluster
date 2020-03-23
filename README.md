# ccCluster v. 1.0
copyright 2015-2020

Welcome to ccCluster
Developed at the ESRF by Gianluca Santoni.
gianluca.santoni@esrf.fr

This program is used to run hierarchycal cluster analysis on protein diffraction data.
When using, please cite:

Santoni, G., Zander, U., Mueller-Dieckmann, C., Leonard, G. & Popov, A. (2017). J. Appl. Cryst. 50,
https://doi.org/10.1107/S1600576717015229.

## Installation with conda
First, you would need to create a virtual environment:
```
conda create --name HCA --file environment.txt
```
After, activate the environment and build the program:
```
conda activate HCA

python setup.py build 

pip install .
```
Now ccCluster commands will be available every time you activate the virtual environment.
## Basic Usage
At first, you must run ccCalc to generate the distance files.
ccCalc must receive, the first time you run it for a project, a list of HKL files.
To do this, you can simply call
```
ccCalc -f <FILE1>.HKL ... <FILEn>.HKL
```

if no file is specified, it will walk all the subdirectories of the current folder and look for HKL files.
This will produce a file named ccClusterLog.txt
One the run is done, you can open ccCluster.
The most basic run can be launched with
```
ccCluster -i ccClusterLog.txt
```

## Dependencies are:

PyQt5

cctbx

matplotlib

numpy

scipy

## Note on cctbx
To generate a virtual environment with the requirement.txt, you need to have 
conda-forge in your .condarc file.

