import sys
sys.path.append('/home/rchhibba/shaded_planning/Utils')

import osmUtils as osmUtils
import imageLinkUtils as imageLinkUtils
import imageUtils as imUtils
import pickle
import os
import numpy as np;
import math
import matplotlib.pyplot as plt
import mapSegmentUtils as mapSegUtils
# Parameters
zoom = 20
imgSize = 400

latTop = 48.325738
latBottom = 48.108876
longLeft = 16.171687
longRight = 16.581223

dirName = "/home/rchhibba/shaded_planning/Dataset/DataSetParis"
areaName = "Vienna"

# Downloading
mapSegUtils.downloadSegmentedMap(latTop, latBottom, longLeft, longRight, zoom, imgSize, dirName, areaName);
