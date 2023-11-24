import os;
import copy;
import imp;
import numpy as np;
import math;
mp = imp.load_source('mercatorUtils.py', '../Utils/mercatorUtils.py');
tm = imp.load_source('totalShadeMask.py', '../Utils/totalShadeMask.py');
imUtils = imp.load_source('imageUtils.py', '../Utils/imageUtils.py');
osmUtils = imp.load_source('osmUtils.py', '../Utils/osmUtils.py');
intersect = imp.load_source('checkIntersection.py', '../Utils/checkIntersection.py');
tm = imp.load_source('totalShadeMask.py', '../Utils/totalShadeMask.py');


# Get a dictionary, with keys images, and values as all links present in that image.
def getImageLinksDict(imgDirPath, nodeFilePath, linkFilePath):
    imgData = imUtils.getImageDirData(imgDirPath);
    numRows = imgData['numRows'];
    numCols = imgData['numCols'];
    
    linkIDToNodePair = osmUtils.getLinkID2EndNodesDict(linkFilePath);
    nodeCoordDict = osmUtils.getNode2CoordinatesDict(nodeFilePath);
    
    imageLinksDir = {};
    for i in range(1, numRows + 1):
        
        for j in range(1, numCols + 1):
            
            linksInImage = {};
            for linkID in linkIDToNodePair:

                nodePair = linkIDToNodePair[linkID]
                isLinkInRoad = checkLinkInImage(nodePair, i, j, nodeCoordDict);
                
                if(isLinkInRoad):
                    linksInImage[linkID] = 1;

            imageLinksDir[(i, j)] = linksInImage;
    return imageLinksDir

# Checks for one link, if it lies in the image or not.
# End nodes of the link are given, along with top, bottom, left, and right coordinates of the image
def checkLinkInImage(nodePair, i, j, nodeCoordDict):

    # Getting coordinates for all 4 edges of the image
    imgLatTop, imgLatBot, imgLongLeft, imgLongRight = imUtils.getImageCornerCoords(i, j);
    
    node0 = nodePair[0];
    node1 = nodePair[1];

    # Getting coordinates for both end nodes from nodeCoordDict.
    node0_Coord = nodeCoordDict[node0];
    node1_Coord = nodeCoordDict[node1];
    
    # Converting the end nodes to Mercator Projections.
    (node0_x, node0_y) = mp.latLngToPoint(node0_Coord[0], node0_Coord[1]);
    (node1_x, node1_y) = mp.latLngToPoint(node1_Coord[0], node1_Coord[1]);
    
    # Converting image corners to Mercator Projections.
    (imgLatTop_, imgLongLeft_) = mp.latLngToPoint(imgLatTop, imgLongLeft);
    (imgLatBot_, imgLongRight_) = mp.latLngToPoint(imgLatBot, imgLongRight);
    
    # Converting the end Mercator nodes to Point objects.
    node0Point = intersect.Point(node0_x, node0_y);
    node1Point = intersect.Point(node1_x, node1_y);
    
    # Converting image Mercator coords to Point Objects.
    pointNW = intersect.Point(imgLatTop_, imgLongLeft_);
    pointNE = intersect.Point(imgLatTop_, imgLongRight_);
    pointSW = intersect.Point(imgLatBot_, imgLongLeft_);
    pointSE = intersect.Point(imgLatBot_, imgLongRight_);
    
    # Checking if the equation of line formed from end nodes of the link
    # intersects with any of the equation of lines from by the 
    
    isLinkInRoad = False;
    # Checking intersection with left edge of the image
    if intersect.doIntersect(node0Point, node1Point, pointNW, pointSW):
        isLinkInRoad = True;
    # Checking intersection with top edge of the image
    elif intersect.doIntersect(node0Point, node1Point, pointNW, pointNE): 
        isLinkInRoad = True;
    # Checking intersection with right edge of the image
    elif intersect.doIntersect(node0Point, node1Point, pointNE, pointSE): 
        isLinkInRoad = True;
        # Checking intersection with bottom edge of the image
    elif intersect.doIntersect(node0Point, node1Point, pointSW, pointSE):
        isLinkInRoad = True;
        
    return isLinkInRoad;


def calcShadeRatesForRoadsInAllImages(dirPath, nodeFilePath, linkFilePath, threshold = 70):
    totalRoadShadeCoverage = {};
    totalMasks = {};
    imgDirPath = os.path.join(dirPath, 'imageDirectory');
    imageLinksDir = getImageLinksDict(imgDirPath, nodeFilePath, linkFilePath);
    print(imageLinksDir);
    
    # Useful dicts
    linkIDToNodePair = osmUtils.getLinkID2EndNodesDict(linkFilePath);
    nodeCoordDict = osmUtils.getNode2CoordinatesDict(nodeFilePath);
    
    for imageIndex in imageLinksDir:
        
        print(imageIndex);
        
        xIndex = imageIndex[0];
        yIndex = imageIndex[1];
        
        # Finding total mask of the image
        imgPath = f"img{xIndex}-{yIndex}.png";
        imgPath = os.path.join(dirPath, imgPath);
        totalMask2 = tm.calculateTotalMask(imgPath, threshold);
        totalMask3 = copy.deepcopy(totalMask2);

        # Getting the corners for an image
        imgLatTop, imgLatBot, imgLongLeft, imgLongRight = imUtils.getImageCornerCoords(xIndex, yIndex);

        # Converting image corners to Mercator Projection
        (xl, yt) = mp.latLngToPoint(imgLatTop, imgLongLeft);
        (xr, yb) = mp.latLngToPoint(imgLatBot, imgLongRight);

        # Sampling over the edges of the image, to kind of map the 400 pixels to coordinates
        yRange = np.linspace(yt, yb, 400);
        xRange = np.linspace(xl, xr, 400);

        roadsInImage = imageLinksDir[imageIndex];
        for road in roadsInImage:
            # Converting end-point coordinates of the road to Mercator projection
            nodePair0 = linkIDToNodePair[road]
            path0_node0 = nodeCoordDict[nodePair0[0]];
            path0_node1 = nodeCoordDict[nodePair0[1]];
            (x0, y0) = mp.latLngToPoint(path0_node0[0], path0_node0[1]);
            (x1, y1) = mp.latLngToPoint(path0_node1[0], path0_node1[1]);

            # All points below are Mercator's Projection.
            totalPixelCount = 0;
            shadedPixelCount = 0;
            for y in yRange:
                leftPoint = (xl, y);
                rightPoint = (xr, y);

                # Line parellel to top/bottom edge of the image.
                line1 = (leftPoint, rightPoint);

                # Line joining the endpoints of the pathway.
                # top and bottom no relevance to actual position.
                topPoint = (x0, y0);
                bottomPoint = (x1, y1);
                line2 = (topPoint, bottomPoint);

                # Calculating intersection point of the 2 lines.
                (xIntersect, yIntersect) = intersect.line_intersection(line1, line2);
                # If lines don't intersect
                if(math.isnan(xIntersect)):
                    continue;

                # yIntersect should directly correspond to a pixel, as we mapped yRange to 400 pixels.
                # But it might not, as we our finding intersection using equation of line.
                for i in range(1, len(yRange) - 1):
                    if(yRange[i-1] < yIntersect  and yRange[i + 1] > yIntersect) :
                        yIntersect = yRange[i];
                        break;
                # For xIntersect, we check between which two points in xRange does the xIntersect lies,
                # The point in between those 2 points will be our xIntersect pixel in the image.
                for i in range(1, len(xRange) - 1):
                    if(xRange[i-1] < xIntersect  and xRange[i + 1] > xIntersect) :
                        xIntersect = xRange[i];
                        break;

                # Checking whether (xIntersect, yIntersect) is under shade
                imagePixelX = np.where(xRange == xIntersect);
                if(len(imagePixelX[0]) != 0):
                    imagePixelX = imagePixelX[0][0];
                else:
                    imagePixelX = -1;

                imagePixelY = np.where(yRange == yIntersect);
                if(len(imagePixelY[0]) != 0):
                    imagePixelY = imagePixelY[0][0];
                else:
                    imagePixelY = -1;

                # print(imagePixelX, imagePixelY)

                # Implies that point lies within the image
                if(imagePixelX != -1 and imagePixelY != -1):
                    totalPixelCount += 1;
                    # Checking if the point is also under shade
                    if(totalMask2[imagePixelY, imagePixelX] == True):
                        totalMask3[imagePixelY, imagePixelX] = False;
                        shadedPixelCount += 1;

            if(not(totalRoadShadeCoverage.__contains__(road))):
                totalRoadShadeCoverage[road] = {
                    "totalPixels": 0,
                    "shadedPixels": 0,
                    "percentageCover": 0
                }
            totalRoadShadeCoverage[road]["totalPixels"] += totalPixelCount;
            totalRoadShadeCoverage[road]["shadedPixels"] += shadedPixelCount;
            if(totalRoadShadeCoverage[road]["totalPixels"] == 0):
                percentCover = 0
            else:
                percentCover = (totalRoadShadeCoverage[road]["shadedPixels"] / totalRoadShadeCoverage[road]["totalPixels"]) * 100;
            totalRoadShadeCoverage[road]["percentageCover"] = percentCover
        totalMasks[imageIndex] = totalMask3;
    return (totalRoadShadeCoverage, totalMasks);


def combineShadedMasksWithRoads(totalMasks, xLim, yLim):
    totalMaskWithRoads = [];

    for i in range(1, xLim + 1):

        horizontalMask = [];

        for j in range(1, yLim + 1):

            singleMask = totalMasks[(i, j)];

            if(horizontalMask == []):

                    horizontalMask = singleMask;

            else:

                horizontalMask = np.hstack([horizontalMask, singleMask]);

        if totalMaskWithRoads == []:
            totalMaskWithRoads = horizontalMask;
        else:
            totalMaskWithRoads = np.vstack([totalMaskWithRoads, horizontalMask]);
            
    return totalMaskWithRoads;
    








































    