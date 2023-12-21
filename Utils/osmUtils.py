import osm2gmns as og
import pandas as pd


def outputNetToCSV(net):
    og.outputNetToCSV(net)
    
# At the end, saves the link and node csv files.
def getOsmNodeLinksUsingMapCode(mapCode):
    og.downloadOSMData(mapCode, 'map.osm');
    net = og.getNetFromFile(input_file, network_type='walk');
    og.outputNetToCSV(net)
    return net;
    
def getOsmNodeLinksUsingExistingMap(fileName):
    input_file = fileName;
    net = og.getNetFromFile(input_file, network_type='walk')
    og.outputNetToCSV(net);
    return net;

def showNet(net):
    og.show(net);
    
def readLinkCSVFile(filePath):
    link_dataframe = pd.read_csv(filePath);
    links = link_dataframe.to_numpy();
    
    # Converting LineString coordinates to float.
    for link in links:
        coords = link[12][12:-1].split(',');
        for i in range(len(coords)):
            coords[i] = coords[i].split();
            coords[i] = [float(coords[i][1]), float(coords[i][0])];
            link[12] = coords
    return links;

def getNode2CoordinatesDict(nodeFilePath):
    node_dataframe = pd.read_csv(nodeFilePath);
    nodes = node_dataframe.to_numpy();
    # Creating a dictionary of nodes and their coordinates
    nodeCoordDict = {}
    for node in nodes:
        nodeNum = node[1];
        nodeXCoord = node[10];
        nodeYCoord= node[9];
        nodeCoordDict[nodeNum] = [nodeXCoord, nodeYCoord];

    return nodeCoordDict;


# Creating a dictionary of end nodes to linkID.
def getEndNodes2LinkIDDict(filePath):
    links = readLinkCSVFile(filePath);
    endNodesOfLinkID = {};
    for link in links:
        nodeTuple = (link[3], link[4]);
        nodeTuple = tuple(sorted(nodeTuple))
        linkID = link[1];
        endNodesOfLinkID[nodeTuple] = linkID;
        
    return endNodesOfLinkID;


# Creating a dictionary of linkID, and the nodePair.
def getLinkID2EndNodesDict(filePath):
    links = readLinkCSVFile(filePath);
    linkIDToNodePair = {};
    for link in links:
        nodeTuple = (link[3], link[4]);
        nodeTuple = tuple(sorted(nodeTuple))
        linkID = link[1];
        linkIDToNodePair[linkID] = nodeTuple;
    
    return linkIDToNodePair;

def getNodes2LinkCoordsDict(filePath):
    links = readLinkCSVFile(filePath);
    nodes2LinkCoordsDict = {};
    for link in links:
        # Will make nodePair key
        node0 = link[3];
        node1 = link[4];
        nodeKey = [node0, node1];
        nodeKey.sort();
        nodeKey = tuple(nodeKey);
        linkCoords = link[12];
        nodes2LinkCoordsDict[nodeKey] = linkCoords;
    return nodes2LinkCoordsDict;


    
    
