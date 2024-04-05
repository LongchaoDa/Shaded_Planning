import pickle
# import sys
# import json
# from scipy.spatial import distance
import os
from math import radians, cos, sin, sqrt, atan2

pkl_filename = "/Users/rushabh/Documents/Research/Code/ShadingPathServer_Paris/totalRoadShadeCoverage.pkl";

with open(pkl_filename, 'rb') as pkl_file:
    totalRoadShadeCoverage = pickle.load(pkl_file);

# ----------------------------
import pandas as pd
import heapq
# import matplotlib.pyplot as plt

# Step 1: Read CSV files
def read_csv_files(links_file_path, nodes_file_path):
    links_df = pd.read_csv(links_file_path)
    nodes_df = pd.read_csv(nodes_file_path)
    return links_df, nodes_df

# Modified Step 2: Build the graph including percentageCover in the weight
def build_graph(links_df, nodes_df, percentage_cover_data, lengthFactor=1, shadeFactor=1):

    node_coords = {row['node_id']: (row['x_coord'], row['y_coord']) for index, row in nodes_df.iterrows()}
    graph = {node_id: {'coords': node_coords[node_id], 'edges': []} for node_id in node_coords}
    
    # Populate the graph with edges from the links data
    for index, row in links_df.iterrows():
        from_node, to_node, length = row['from_node_id'], row['to_node_id'], row['length']
        link_id = row['link_id']
        
        percentage_cover = percentage_cover_data.get(link_id, {}).get('percentageCover', 0)
        weight = lengthFactor * length + shadeFactor * percentage_cover
        
        # graph[from_node]['edges'].append((to_node, weight))

        # Check if the edge already exists to maintain uniqueness
        # This is required as link.csv has link duplicates, swapping the from and to nodes each time.

        edge = (to_node, weight)
        if edge not in graph[from_node]['edges']:
            graph[from_node]['edges'].append(edge)

        # Doing it for the other way around as well, because link.csv doesn't ensure that always.
        edge = (from_node, weight)
        if edge not in graph[to_node]['edges']:
            graph[to_node]['edges'].append(edge)
    
    return graph


def dijkstra(graph, start, end):
    
    queue = [(0, start)]
    
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0

    prev = {node: None for node in graph}
        
    while queue:
        current_distance, current_node = heapq.heappop(queue)
        if current_node == end:
            break
        # Adjusted to access the 'edges' within each node's dictionary
        for neighbor, weight in graph[current_node]['edges']:
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                prev[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))
    
    path = []
    while end is not None:
        path.append(graph[end]['coords'])
        end = prev[end]
    path.reverse()
    
    return path


# def fetch_node_coordinates(nodes_df, path):
#     # Create a dictionary from nodes_df for quick lookup
#     node_coords = {row['node_id']: (row['x_coord'], row['y_coord']) for index, row in nodes_df.iterrows()}
#     # Retrieve the coordinates for each node in the path
#     path_coords = [node_coords[node_id] for node_id in path]
#     return path_coords

# Main function adjusted to include percentageCover data
def calculate(links_file_path, nodes_file_path, start_node, end_node, percentage_cover_data, lengthFactor, shadeFactor):

    path = f'graph_{lengthFactor}_{shadeFactor}.pkl'
    # Check if variables already present.
    if os.path.exists(path):
        with open(path, 'rb') as f:
            graph = pickle.load(f);
            
    else:
        links_df, nodes_df = read_csv_files(links_file_path, nodes_file_path)
        graph = build_graph(links_df, nodes_df, percentage_cover_data, lengthFactor, shadeFactor)
        with open(path, 'wb') as f:
            pickle.dump((graph), f)

    shortest_path = dijkstra(graph, start_node, end_node)
    # path_coords = fetch_node_coordinates(nodes_df, shortest_path)
    
    return (shortest_path)

def haversine(coord1, coord2):
    """
    Calculate the Haversine distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)    
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    # Radius of Earth in kilometers. Use 6371 for kilometers or 3956 for miles
    R = 6371.0
    distance = R * c
    
    return distance

def find_closest_nodes(nodes_file_path, origin, destination):
    nodes_df = pd.read_csv(nodes_file_path)
    
    # Calculate Haversine distance from each node to the origin and destination
    origin_distances = nodes_df.apply(lambda row: haversine(origin, (row['y_coord'], row['x_coord'])), axis=1)
    destination_distances = nodes_df.apply(lambda row: haversine(destination, (row['y_coord'], row['x_coord'])), axis=1)
    
    # Find the index of the node with the smallest distance to origin and destination
    closest_origin_node_idx = origin_distances.idxmin()
    closest_destination_node_idx = destination_distances.idxmin()
    
    # Retrieve the node_id for the closest nodes
    closest_origin_node_id = nodes_df.iloc[closest_origin_node_idx]['node_id']
    closest_destination_node_id = nodes_df.iloc[closest_destination_node_idx]['node_id']
    
    # print(closest_origin_node_id, closest_destination_node_id)
    return closest_origin_node_id, closest_destination_node_id

def main(lengthFactor, shadeFactor, origin, destination):
    links_file_path = '/Users/rushabh/Documents/Research/Code/ShadingPathServer_Paris/link.csv'  
    nodes_file_path = '/Users/rushabh/Documents/Research/Code/ShadingPathServer_Paris/node.csv'

    start_node, end_node = find_closest_nodes(nodes_file_path, origin, destination)

    return calculate(links_file_path, nodes_file_path, start_node, end_node, totalRoadShadeCoverage, lengthFactor, shadeFactor)

