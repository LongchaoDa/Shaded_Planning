import requests
import os.path
from MercatorProjection import *
from math import *
import numpy as np
import cv2;
import matplotlib.pyplot as plt


apiKey = "AIzaSyBYPwYOvF-GhIF8jBFJ06adOp_2z4wlhyM"
baseUrl = "https://maps.googleapis.com/maps/api/staticmap?"

def segmentMap(latTop, latBottom, longLeft, longRight, zoom, imgSize, dirName, areaName):

    mapType = 'satellite'

    # For first image, find lat,long of the edges, to estimate center for the next image.
    [SWlat, SWlng, NElat, NElng] = getImageBounds(imgSize, zoom, latTop, longLeft)

    # Factors with which to increase lat and long for each image
    latFactor = latTop - SWlat
    longFactor = longLeft - SWlng

    # Looping over all centre coordinates, and retrieving images.

    currLat = latTop
    xIndex = 1
    
    # TODO:- Move to a new function.
    # Image Directory that stores imageName: {lat, long} for each image(centre coordinates)
    # Also stores the radius or length of the side of each image in metres.
    # Stored as a JSON at the end.
    imageDirectory = {
        "dataSetName" : dirName,
        "location" : areaName,
        "imageRadius" : getImageRadius(latTop, longLeft, latTop, longRight),
        "coordinates" : {
            'latTop':latTop,
            'latBottom':latBottom,
            'longLeft':longLeft,
            'longRight':longRight
        },
        # These will be useful when we need corner coordinates for any image.
        "latFactor": latFactor,
        "longFactor": longFactor,
        "zoom" : zoom,
        "imageSize" : imgSize,
        "imageIndex": {}
    };
        
    while(currLat >= latBottom):
        currLong = longLeft
        yIndex = 1
        while(currLong <= longRight):
            mapURL = baseUrl + f"center={currLat},{currLong}&zoom={zoom}&size={imgSize}x{imgSize}&maptype={mapType}&key={apiKey}"
            # -----------
            print(mapURL)
            response = requests.get(mapURL)
            
            # writing data into the file
            fileName = os.path.join(dirName, f"img{xIndex}-{yIndex}.png")
            os.makedirs(dirName, exist_ok=True)
            # --------
            print(fileName)
            with open(fileName, 'wb') as file:
                file.write(response.content)
            currLong += 2*longFactor
            yIndex+=1
            
            # ---Logging image and its coordinates into imageDirectory------
            imageKey = f"{xIndex}-{yIndex}";
            imageDirectory["imageIndex"][imageKey] = {
                "lat" : currLat,
                "long": currLong
            }
            
        currLat -= 2*latFactor
        xIndex+=1   
        
    # Storing imageDirectory as a JSON file.
    import json
    fileName = os.path.join(dirName, "imageDirectory")
    with open(fileName, "w") as file:
        json.dump(imageDirectory, file, indent=4)

        
        
        
# Returns length of side of image in metres
def getImageRadius(lat1, lon1, lat2, lon2):
    return acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))*6371*1000 ;




# Joins map-segments together
# This is a generic function, it doesn't assume no. of images, or image size.
# It just needs the image name format(hard coded), and the directory name.
# Below we've used loops, but if we had images in a matrix, we could use reshaping
# However, it might take a lot of space if we try to store all images in a matrix while downloading 
def combineSegmentedMap(dirName): 
    
    combinedImage = [];
    i = 1
    j = 1
    while(1):
        j = 1
        horizontalImage = [];
        while(1):
            filePath = os.path.join(dirName, f"img{i}-{j}.png")
            # checking if it is a file
            if os.path.isfile(filePath):
                image = cv2.imread(filePath)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                if(horizontalImage == []):
                    horizontalImage = image;
                else:
                    horizontalImage = cv2.hconcat([horizontalImage, image]);
            else: 
                break;
            j+=1
        # Implies no image exists with index imgi-1.png => images exhausted.
        if j == 1:
            break;
        if combinedImage == []:
            combinedImage = horizontalImage;
        else:
            combinedImage = cv2.vconcat([combinedImage, horizontalImage]);
        i+=1;
    plt.imshow(combinedImage)
    
