'''
Run this code before running the server.
This creates the graphs before hand.
Thus, the code for creating graph in dijkstra_shade.py will just be a safety net.
'''

import yaml
import pandas as pd
import os
import pickle
import time
import sys
def progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar = '█' * int(percent) + '-' * (100 - int(percent))
    sys.stdout.write('\r|%s| %s%%' % (bar, percent))
    sys.stdout.flush()

def read_csv_files(links_file_path, nodes_file_path):
    links_df = pd.read_csv(links_file_path)
    nodes_df = pd.read_csv(nodes_file_path)
    return links_df, nodes_df

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

# --------------------------------------
# Main code
city_config_file = "city_config.yaml"

dijkstraFactors = [(1, 0), (0.7, 0.3), (0.5, 0.5), (0.3, 0.7), (0, 1)];

# Load the city configuration
with open(city_config_file, 'r') as file:
    city_config = yaml.safe_load(file)

# Looping over the city names, and creating graphs.
for city_name in city_config['city_bounds']:
    print("\nCreating graphs for ", city_name, '-------------');
    pkl_filename = f'data/{city_name}/total_road_shade_coverage.pkl'
    with open(pkl_filename, 'rb') as pkl_file:
        totalRoadShadeCoverage = pickle.load(pkl_file)

    links_file_path = f'data/{city_name}/link.csv'  
    nodes_file_path = f'data/{city_name}/node.csv'

    total_factors = len(dijkstraFactors)
    factor_count = 0  # Initialize a counter to track progress through the factors

    for factor in dijkstraFactors:
        directory_path = f'graphData/{city_name}'
        path = f'graphData/{city_name}/graph_{factor[0]}_{factor[1]}.pkl'

        # Ensure the directory exists, if not create it
        os.makedirs(directory_path, exist_ok=True)

        # Check if variables already present.
        if os.path.exists(path) == False:
            links_df, nodes_df = read_csv_files(links_file_path, nodes_file_path)
            graph = build_graph(links_df, nodes_df, totalRoadShadeCoverage, factor[0], factor[1])
            with open(path, 'wb') as f:
                pickle.dump((graph), f)

        factor_count += 1
        progress_bar(factor_count, total_factors)