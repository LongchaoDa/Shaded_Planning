import sys
sys.path.append('/home/rchhibba/shaded_planning/Utils')

import osmUtils as osmUtils
import imageLinkUtils as imageLinkUtils
# import imageUtils as imUtils
import pickle
import os
import numpy as np;
import math
import matplotlib.pyplot as plt
import datashader as ds, pandas as pd, colorcet
from datashader.colors import Hot
from datashader.colors import viridis
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import ListedColormap

print("Import done");

# Note:- The net files will be created in the same directory as that of the file calling this function.
# net = osmUtils.getOsmNodeLinksUsingExistingMap("mapByeng.osm")
# osmUtils.outputNetToCSV(net) #net
# print("csv files created")

# Creating dictionary of image indices to roads present in the image
# Like in calculating shade rate, here too we can use link coordinates to find roads that are present in an image.
# However, it might not make that big of a difference.
imgFolderPath = "../Dataset/DataSetParis";
imgDirPath = os.path.join(imgFolderPath, "imageDirectory");
nodeFilePath = "node.csv";
linkFilePath = "link.csv";

# The dictionary
# imageLinksDir = imageLinkUtils.getImageLinksDict(imgDirPath, nodeFilePath, linkFilePath);
print("imageLinkDir created");

pkl_filename = 'imageLinksDir.pkl'

with open(pkl_filename, 'rb') as pkl_file:
	# pickle.dump(imageLinksDir, pkl_file)
	imageLinksDir = pickle.load(pkl_file)

print("imageLinksDir saved");

# Finding total shades for each of the road

dirPath = imgFolderPath;
# totalRoadShadeCoverage, totalMasks, totalImage = imageLinkUtils.calcShadeRatesForRoadsInAllImages(dirPath, nodeFilePath, linkFilePath, threshold = 70)
print("totalRoadShadeCoverage calculated");

pkl_filename = 'totalRoadShadeCoverage.pkl'
with open(pkl_filename, 'rb') as pkl_file:
    # pickle.dump(totalRoadShadeCoverage, pkl_file)
    totalRoadShadeCoverage = pickle.load(pkl_file)

print("totalRoadShadeCoverage saved");

pkl_filename = 'totalMasks.pkl'
with open(pkl_filename, 'rb') as pkl_file:
    # pickle.dump(totalMasks, pkl_file)
    totalMasks = pickle.load(pkl_file)

print("totalMasks saved");

pkl_filename = 'totalImage.pkl'
with open(pkl_filename, 'rb') as pkl_file:
    # pickle.dump(totalImage, pkl_file)
    totalImage = pickle.load(pkl_file)
print("totalImage saved");


# Data Visualization

node2CoordDict = osmUtils.getNode2CoordinatesDict(nodeFilePath)
linkID2NodeDict = osmUtils.getLinkID2EndNodesDict(linkFilePath);
linkIDToNodePair = osmUtils.getLinkID2EndNodesDict(linkFilePath)
nodes2LinkCoordsDict = osmUtils.getNodes2LinkCoordsDict(linkFilePath)
lineStringDict = osmUtils.getLineStringDict(linkFilePath)

print("Dictionaries created for Data visualization");

# coordinateSamples = [];
# for linkID in totalRoadShadeCoverage:
#     # Obtaining link coords from nodes.
#     nodePair0 = linkIDToNodePair[linkID]
#     linkCoords = nodes2LinkCoordsDict[nodePair0];
#     print("linkID", linkID);
#     for i in range(len(linkCoords) - 1):
    
#         percentageCover = totalRoadShadeCoverage[linkID]["percentageCover"];
#         node0Coords = linkCoords[i];
#         node1Coords = linkCoords[i + 1];


#         lat_1 = node0Coords[0];
#         long_1 = node0Coords[1];  

#         lat_2 = node1Coords[0];
#         long_2 = node1Coords[1];

#         alpha = np.linspace(0, 1, 50*(math.floor(percentageCover) + 10));

#         longSamples = long_1 + alpha * (long_2 - long_1);
#         latSamples  = lat_1  + alpha * (lat_2  - lat_1);
#         coordSamples = [];
#         n = 20;
#         addent = np.transpose(np.vstack((latSamples, longSamples)))        
#         if len(coordinateSamples) == 0:
#             coordinateSamples = addent;
#         else:
#             coordinateSamples = np.vstack((coordinateSamples, addent));
            
#         # coordinateSamples = np.vstack((coordinateSamples, coordSamples));
      

# print("Coordinate Samples calculated")
# import datashader as ds, pandas as pd, colorcet
# from datashader.colors import Hot
# from datashader.colors import viridis

# df  = pd.DataFrame(coordinateSamples, columns = ['lat', 'long']);
# cvs = ds.Canvas(plot_width=700, plot_height=700)
# agg = cvs.points(df, 'lat', 'long')
# img = ds.tf.shade(agg, cmap=['white', 'yellow', 'orange', 'red', 'maroon', 'brown'], how='log')
# plt.imshow(img.to_pil())
# plt.show()

# Vary dpi value with brickyard to check time taken and quality of image - 300 to 1500

# plt.savefig('output_image.png', dpi=1500);
# print("Figure saved")

line_width = 3;
node_radius = 1;

# colors = [(1, 0.9, 0.6), (1, 0.5, 0)] # RGB values for yellowish orange and dark brown
# cmap = LinearSegmentedColormap.from_list('custom_colormap', colors, N=256)

# Define the colors
colors = ['orange', 'red', 'maroon', 'black']
cmap = ListedColormap(colors)

figsize = None
network = osmUtils.getOsmNodeLinksUsingExistingMap("mapParis.osm")
print(network.link_dict[1].geometry);

xy_list = []
for node_id, node in network.node_dict.items():
    xy = list(node.geometry_xy.coords)[0]
    xy_list.append(xy)
xy_array = np.array(xy_list)

if figsize is None:
    net_length = xy_array[:,0].max() - xy_array[:,0].min()
    net_width = xy_array[:,1].max() - xy_array[:,1].min()
    fig_length = 16
    fig_width = fig_length / net_length * net_width
    plt.figure(figsize=(fig_length, fig_width))
else:
    plt.figure(figsize=figsize)

ax = plt.gca()
ax.axes.xaxis.set_visible(False)
ax.axes.yaxis.set_visible(False)

# plt.scatter(xy_array[:, 0], xy_array[:, 1], s=node_radius, color='pink', zorder=1)

# ... (your existing code)

for link_id, link in network.link_dict.items():
    # Check if link_id is present in totalRoadShadeCoverage
    if link_id not in totalRoadShadeCoverage:
        continue  # Skip to the next iteration if link_id is not present

    percentageCover = totalRoadShadeCoverage[link_id]["percentageCover"]
    xys = list(link.geometry_xy.coords)
    xys_array = np.array(xys)
    
    # Normalize the percentageCover to be in the range [0, 1]
    normalized_percentage = percentageCover / 100.0
    
    # Use the colormap to get the corresponding color for the normalized percentage
    link_color = cmap(normalized_percentage)
    
    plt.plot(xys_array[:, 0], xys_array[:, 1], linewidth=line_width, color=link_color, zorder=0)

# Save the plot
plt.savefig('ParisVisuals2.png', bbox_inches='tight')

# Show the plot
plt.show()
