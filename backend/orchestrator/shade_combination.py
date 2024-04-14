import json
from dijkstra_shade import main
import sys

if __name__ == "__main__":
    # Convert the string arguments back into lists of floats
    origin = list(map(float, sys.argv[1].split(',')))
    destination = list(map(float, sys.argv[2].split(',')))
    travelMode = sys.argv[3]
# Initialize a dictionary to hold all path types and their data

paths_data = {
    "Shortest": main(1, 0, origin, destination, travelMode),
    "Shaded": main(0, 1, origin, destination, travelMode),
    "50-50": main(0.5, 0.5, origin, destination, travelMode),
    "70-30": main(0.7, 0.3, origin, destination, travelMode),
    "30-70": main(0.3, 0.7, origin, destination, travelMode)
}

# Convert the dictionary to a JSON string and print
print(json.dumps(paths_data))
