# Reference - StackOverflow :- https://stackoverflow.com/questions/12507274/how-to-get-bounds-of-a-google-static-map?noredirect=1&lq=1

import math

mapHeight = 256
mapWidth = 256

def latLngToPoint(lat, lng):

    x = (lng + 180) * (mapWidth/360)
    y = ((1 - math.log(math.tan(lat * math.pi / 180) + 1 / math.cos(lat * math.pi / 180)) / math.pi) / 2) * mapHeight

    return(x, y)

def pointToLatLng(x, y):

    lng = x / mapWidth * 360 - 180

    n = math.pi - 2 * math.pi * y / mapHeight
    lat = (180 / math.pi * math. atan(0.5 * (math.exp(n) - math.exp(-n))))

    return(lat, lng)

def getImageBounds(imgSize, zoom, lat, lng):
    xScale = math.pow(2, zoom) / (imgSize/mapWidth)
    yScale = math.pow(2, zoom) / (imgSize/mapWidth)

    centreX, centreY = latLngToPoint(lat, lng)

    southWestX = centreX - (mapWidth/2)/ xScale
    southWestY = centreY + (mapHeight/2)/ yScale
    SWlat, SWlng = pointToLatLng(southWestX, southWestY)

    northEastX = centreX + (mapWidth/2)/ xScale
    northEastY = centreY - (mapHeight/2)/ yScale
    NElat, NElng = pointToLatLng(northEastX, northEastY)

    return[SWlat, SWlng, NElat, NElng]