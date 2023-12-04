# Visualizer-SkeletalMotionHDF5

![Demo](demo.gif)

## Description

This repository contains a visualizer to animate the HDF5 data of the open access datasets:

* [6-Minute-Walking-Dataset](https://doi.org/10.5281/zenodo.10253111)
* [Humanoid-Robot-Dataset](https://doi.org/10.5281/zenodo.10253284)

To inspect the data and view, e.g. the data hierarchy of the HDF5 files, we recommend [Panoply](https://www.giss.nasa.gov/tools/panoply/). 

To visualize the BVH files from the dataset we recommend to use [Blender](https://www.blender.org/download/). 

## Installation

### Linux
Assuming that python3 is installed, you can install the required dependencies as follows:
```
> python3 -m pip install -r requirements.txt
```
This was tested on Ubuntu 22.04 LTS.

## Getting started
To visualize the HDF5 files we suggest to mount the data folder to the "data" folder of the repo. Assuming that you downloaded the data to the folder with the path "PATH-TO-YOUR-DATA-FOLDER" you can mount the folder via the following command, executed from the repo root:

```
> sudo mount -bind PATH-TO-YOUR-DATA-FOLDER data
```

After mounting the data you can visualize the data via 

```
> python3 ShowDataHDF5.py
```

You can change the input parameter via command line, see for options

```
> python3 ShowDataHDF5.py --help
```

Otherwise you can edit the file "ShowDataHDF5.py" directly.

## Support
In case you need support, please contact <Bertram.Taetz@dfki.de>.

## Contribution and license
All contributions welcome! All content in this repository is licensed under the MIT license.




