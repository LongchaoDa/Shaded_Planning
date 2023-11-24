import cv2;
import matplotlib.pyplot as plt
import imp;
import json
mp = imp.load_source('mercatorUtils.py', '../Utils/mercatorUtils.py');

imgData = {};

# This command should be run first.
def getImageDirData(*args):
    global imgData;
    if(len(imgData) == 0):
        imgData = loadImageDirData(args[0]);
        return imgData;
    return imgData;


def loadImageDirData(imgDirPath):
    f = open(imgDirPath);
    imgData = json.load(f);
    return imgData;


def getImage(imgPath, displayImage = False):
    image = cv2.imread(imgPath);
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB);
    if(displayImage):
        plt.imshow(image);
    return image;


def getImageCentreCoords(imgXIndex, imgYIndex):
    global imgData;
    imgCoords = imgData['imageIndex'][f"{imgXIndex}-{imgYIndex}"];
    return imgCoords;

def getImageLatLongFactor():
    global imgData;
    areaCoords = imgData["coordinates"];
    latTop = areaCoords['latTop'];
    longLeft = areaCoords['longLeft'];
    imgSize = imgData["imageSize"];
    zoom = imgData["zoom"];
    [SWlat, SWlng, NElat, NElng] = mp.getImageBounds(imgSize, zoom, latTop, longLeft);
    
    latFactor = latTop - SWlat
    longFactor = longLeft - SWlng
    
    return latFactor, longFactor;

def getImageCornerCoords(imgX, imgY):
    (latFactor, longFactor) = getImageLatLongFactor();
    imgCoords = getImageCentreCoords(imgX, imgY);
    imgLatTop = imgCoords["lat"] + latFactor/2;
    imgLatBot = imgCoords["lat"] - latFactor/2;
    imgLongLeft = imgCoords["long"] - longFactor/2;
    imgLongRight = imgCoords["long"] + longFactor/2;
    
    return (imgLatTop, imgLatBot, imgLongLeft, imgLongRight);
