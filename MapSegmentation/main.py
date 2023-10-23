import requests
import os.path
from MercatorProjection import *

apiKey = "AIzaSyBYPwYOvF-GhIF8jBFJ06adOp_2z4wlhyM"
baseUrl = "https://maps.googleapis.com/maps/api/staticmap?"

def segmentMap(latTop, latBottom, longLeft, longRight, zoom, imgSize):

    mapType = 'satellite'

    # For first image, find lat,long of the edges, to estimate center for the next image.
    [SWlat, SWlng, NElat, NElng] = getImageBounds(imgSize, zoom, latTop, longLeft)

    # Factors with which to increase lat and long for each image
    latFactor = latTop - SWlat
    longFactor = longLeft - SWlng

    # Looping over all centre coordinates, and retrieving images.

    currLat = latTop
    xIndex = 1

    while(currLat >= latBottom):
        currLong = longLeft
        yIndex = 1
        while(currLong <= longRight):
            mapURL = baseUrl + f"center={currLat},{currLong}&zoom={zoom}&size={imgSize}x{imgSize}&maptype={mapType}&key={apiKey}"
            # -----------
            print(mapURL)
            response = requests.get(mapURL)
            # writing data into the file
            fileName = os.path.join("DataSet1", f"img{xIndex}-{yIndex}.png")
            # --------
            print(fileName)
            with open(fileName, 'wb') as file:
                file.write(response.content)
            currLong += 2*longFactor
            yIndex+=1
        currLat -= 2*latFactor
        xIndex+=1    