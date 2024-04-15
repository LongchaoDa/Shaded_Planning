import pickle
import os
from math import radians, cos, sin, sqrt, atan2
import yaml
import pandas as pd
import heapq

city_config_file = "../orchestrator/city_config.yaml"

# Load the city configuration
with open(city_config_file, 'r') as file:
    city_config = yaml.safe_load(file)

# Step 1: Read CSV files
def read_csv_files(links_file_path, nodes_file_path):
    links_df = pd.read_csv(links_file_path)
    nodes_df = pd.read_csv(nodes_file_path)
    return links_df, nodes_df

# Modified Step 2: Build the graph including percentageCover in the weight
def build_graph(links_df, nodes_df, percentage_cover_data, lengthFactor=1, shadeFactor=1):
    node_coords = {row['node_id']: (row['x_coord'], row['y_coord']) for index, row in nodes_df.iterrows()}
    graph = {node_id: {'coords': node_coords[node_id], 'edges': []} for node_id in node_coords}

    for index, row in links_df.iterrows():
        from_node, to_node, length = row['from_node_id'], row['to_node_id'], row['length']
        link_id = row['link_id']
        
        percentage_cover = percentage_cover_data.get(link_id, {}).get('percentageCover', 0)
        weight = lengthFactor * length + shadeFactor * percentage_cover
        
        # Each edge is stored with (neighbor_node, weight, original_length)
        edge = (to_node, weight, length)
        if edge not in graph[from_node]['edges']:
            graph[from_node]['edges'].append(edge)

        edge = (from_node, weight, length)
        if edge not in graph[to_node]['edges']:
            graph[to_node]['edges'].append(edge)
    
    return graph


import heapq

def dijkstra(graph, start, end):
    queue = [(0, start, 0)]  # (current_distance, current_node, path_length)
    
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0

    prev = {node: None for node in graph}
    path_lengths = {node: 0 for node in graph}  # To store the path length

    while queue:
        current_distance, current_node, current_path_length = heapq.heappop(queue)
        
        if current_node == end:
            break

        for neighbor, weight, original_length in graph[current_node]['edges']:
            distance = current_distance + weight
            path_length = current_path_length + original_length
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                path_lengths[neighbor] = path_length
                prev[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor, path_length))

    path = []
    path_length = path_lengths[end]  # Total length of the path
    while end is not None:
        path.append(graph[end]['coords'])
        end = prev[end]
    path.reverse()
    
    return path, path_length


# Main function adjusted to include percentageCover data
def calculate(graph, start_node, end_node):

    shortest_path, path_length = dijkstra(graph, start_node, end_node)
    
    return (shortest_path, path_length)

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

def find_closest_nodes_using_graph(target_coords, graph) :
    # Traverse each node, calculate distance to the target coordinates, ignore nodes with empty edges, and find the nearest node
    nearest_node_with_edges = 123
    min_distance_with_edges = float('inf')  # Initialize with infinity

    for node, data in graph.items():
        # Skip nodes with empty 'edges' list
        if not data['edges']:
            continue
        
        node_coords = data['coords']
        long, lat = node_coords
        node_coords = (lat, long)
        distance = haversine(node_coords, target_coords)
        if distance < min_distance_with_edges:
            min_distance_with_edges = distance
            nearest_node_with_edges = node
            # print(nearest_node_with_edges)
    return nearest_node_with_edges

def evaluate_city(origin, destination):
    # Extract the city bounds
    for city_name in city_config['city_bounds']:
        lat_top = city_config['city_bounds'][city_name]['lat_top']
        lat_bottom = city_config['city_bounds'][city_name]['lat_bottom']
        lng_left = city_config['city_bounds'][city_name]['lng_left']
        lng_right = city_config['city_bounds'][city_name]['lng_right']

        origin_lat, origin_lng = origin
        destination_lat, destination_lng = destination

        if (lat_bottom <= origin_lat <= lat_top and lng_left <= origin_lng <= lng_right) and \
           (lat_bottom <= destination_lat <= lat_top and lng_left <= destination_lng <= lng_right):
            return city_name

    return None

def main(lengthFactor, shadeFactor, origin, destination, travelMode):

    if(travelMode == "WALKING"):
        travelMode = "walkable";
    elif(travelMode == "BICYCLING"):
        travelMode = "bikeable";

    city_name = evaluate_city(origin, destination)
    
    if city_name is None:
        return None

    path = f'../orchestrator/graphData_{travelMode}/{city_name}/graph_{lengthFactor}_{shadeFactor}.pkl'
    # Check if variables already present.
    try:
        with open(path, 'rb') as f:
            graph = pickle.load(f);
    except:
        print('Relevant graph not created. Create graph first before running server.')

    start_node = find_closest_nodes_using_graph(origin, graph)
    end_node = find_closest_nodes_using_graph(destination, graph)

    # Find the path using Dijkstra's algorithm
    path, total_length = calculate(graph, start_node, end_node)
    
    return {"path": path, "length": total_length}

# Testing

# origin = (48.882210, 2.328871);
# destination = (48.8823998,2.3236082)

# print(main(1, 0, origin, destination, 'WALKING'));