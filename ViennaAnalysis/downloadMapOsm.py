import sys
sys.path.append('/home/rchhibba/shaded_planning/Utils')

import osmUtils as osmUtils
import os
import numpy as np;
import math
import matplotlib.pyplot as plt
import requests

# Setting parameters

zoom = 20
imgSize = 400

latTop = 48.8857
latBottom = 48.8309
longLeft = 2.3027
longRight = 2.3919

dirName = "../Dataset/DataSetParis"
areaName = "Paris City"

n = latTop;
s = latBottom;
w = longLeft;
e = longRight

# Downloading map from OSM.
url = f"http://overpass.openstreetmap.ru/cgi/xapi_meta?*[bbox={w},{s},{e},{n}]";

print(f"url: {url}")
response = requests.get(url)
if response.status_code == 200:
    file_path = "./mapParis" + ".osm"
    with open(file_path, 'wb') as file:
        file.write(response.content)
else:
    file_path = 'None'
    print("Failed to retrieve the data.")

# Outputting net and csv files
net = osmUtils.getOsmNodeLinksUsingExistingMap("mapParis.osm");
osmUtils.outputNetToCSV(net);

