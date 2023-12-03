"""
Visualizer for HDF5 files used in the paper

Bertram Taetz, Michael Lorenz1, Markus Miezal, Didier Stricker, Gabriele Bleser-Taetz
"JointTracker: real-time inertial kinematic chain tracking
with joint position estimation" (to appear)

"""

import argparse
from utils.HDF5Visualizer import HDF5Vis

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize HDF5 file!')
    parser.add_argument('--hdf5File', nargs='?', action="store", default="data/P11_Retest_6_min_walking_test.h5"
                        , help='HDF5 path ans filename')
    parser.set_defaults(doNotshowIMUs=False)
    parser.add_argument('--doNotshowIMUs', dest='doNotshowIMUs', action='store_true', help="Do not show IMUs in visualizer")
    parser.set_defaults(doNotshowSegs=False)
    parser.add_argument('--doNotshowSegs', dest='doNotshowSegs', action='store_true', help="Do not show no segments in visualizer")
    parser.add_argument('--showIMUData', nargs='+', action='store', default=["RightFoot", "LeftFoot"]
                        , help="Show IMUs in visualizer?")
    args = parser.parse_args()

    hdf5Vis = HDF5Vis(args)
    hdf5Vis.animateSkel()

    print("Done!")

