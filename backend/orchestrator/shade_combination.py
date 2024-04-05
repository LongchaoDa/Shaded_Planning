import json
from backend.orchestrator.dijkstra_shade import main
import sys

if __name__ == "__main__":
    # Convert the string arguments back into lists of floats
    origin = list(map(float, sys.argv[1].split(',')))
    destination = list(map(float, sys.argv[2].split(',')))

# Initialize a dictionary to hold all path types and their data

paths_data = {
    "Shortest": main(1, 0, origin, destination),
    "Shaded": main(0, 1, origin, destination),
    "50-50": main(0.5, 0.5, origin, destination),
    "70-30": main(0.7, 0.3, origin, destination),
    "30-70": main(0.3, 0.7, origin, destination)
}

# Convert the dictionary to a JSON string and print
print(json.dumps(paths_data))
