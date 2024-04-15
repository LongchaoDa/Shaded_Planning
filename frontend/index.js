// Initialize and add the map
let map;
let directionsRenderers = [];

// API related constants
const API_BASE_URL = 'http://localhost:8080';
const COORD_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json";
var API_KEY = null;

// Color Map
const colorDict = {
    "shaded": "#6bb06e",
    "shortest": "#f18c60",
    "50-50": "#8AA7BF",
    "70-30": "#d5a698",
    "30-70": "#c0f3c0"
};

// Legend Mappings
const colorDictLegend = {
    "shaded": "Most Shaded Path",
    "shortest": "Shortest Path",
    "50-50": "50% Distance - 50% Shaded Path Ratio",
    "70-30": "70% Distance - 30% Shaded Path Ratio",
    "30-70": "30% Distance - 70% Shaded Path Ratio"
};

// Map Realted Variables
var mask = null;
var spinner = null;
var polylineData = [];
var markerData = [];
const startMarkerIcon = "http://maps.google.com/mapfiles/ms/icons/green-dot.png";
const stopMarkerIcon = "http://maps.google.com/mapfiles/ms/icons/red-dot.png";


window.callbackFunction = function () {
    window.google.maps.__ib__();
    window.initAutocomplete();
}

function loadGoogleMaps() {
    // Load the Google Maps JavaScript API    
    (g => {
        var h, a, k, p = "The Google Maps JavaScript API",
            c = "google",
            l = "importLibrary",
            q = "__ib__",
            m = document,
            b = window;
        b = b[c] || (b[c] = {});
        var d = b.maps || (b.maps = {}),
            r = new Set,
            e = new URLSearchParams,
            u = () => h || (h = new Promise(async (f, n) => {
                await (a = m.createElement("script"));
                e.set("libraries", [...r] + "");
                for (k in g) e.set(k.replace(/[A-Z]/g, t => "_" + t[0].toLowerCase()), g[k]);
                e.set("callback", "callbackFunction");
                a.src = `https://maps.${c}apis.com/maps/api/js?` + e;
                d[q] = f;
                a.onerror = () => h = n(Error(p + " could not load."));
                a.nonce = m.querySelector("script[nonce]")?.nonce || "";
                m.head.append(a);
            }));
        d[l] ? console.warn(p + " only loads once. Ignoring:", g) : d[l] = (f, ...n) => r.add(f) && u().then(() => d[l](f, ...n))
    })({
        key: API_KEY,
        v: "weekly",
        libraries: "places",
        // Use the 'v' parameter to indicate the version to use (weekly, beta, alpha, etc.).
        // Add other bootstrap parameters as needed, using camel case.
    });
}

// Refresh the shaded paths on the map
function refreshShadedPaths(source, destination, travelMode, numRoutes) {
    removeLegend();

    // Show the spinner
    mask.style.display = 'block';
    spinner.style.display = 'block';

    removeExistingPaths(polylineData);
    Promise.all([
        getCoordinates(source),
        getCoordinates(destination)
    ]).then(([coords1, coords2]) => {
        getPaths(coords1, coords2, travelMode, numRoutes)
            .then(pathsData => {
                // Hide the spinner
                mask.style.display = 'none';
                spinner.style.display = 'none';
                // Render the paths on the map
                renderPaths(pathsData);
                createLegend(pathsData);
            })
            .catch(error => {
                console.error('Error:', error);
                // Hide the spinner
                spinner.style.display = 'none';
            });

    }).catch(error => {
        console.error('Error:', error);
        alert('Please enter a valid Google Maps API key or specify the locations more precisely. Currently, a valid path between the source and destination cannot be found.');

        // Hide the spinner
        spinner.style.display = 'none';
        return;
    });

}

// DOMContentLoaded event listener
document.addEventListener('DOMContentLoaded', () => {
    mask = document.getElementById('mask');
    spinner = document.getElementById('loadingSpinner');
    document.getElementById('apiKey').addEventListener('input', function () {
        API_KEY = this.value;
        validateKey();
    });

    const searchButton = document.getElementById('searchButton');
    searchButton.addEventListener('click', () => {
        let sourceValue = document.getElementById('sourceInput').value;
        let destinationValue = document.getElementById('destinationInput').value;
        let travelMode = document.querySelector('input[name="travelMode"]:checked').value;
        const numRoutes = parseInt(document.getElementById('numRoutesInput').value);

        // Refresh the map and fetch new routes based on input values
        refreshShadedPaths(sourceValue, destinationValue, travelMode, numRoutes);
    });

    const resetButton = document.getElementById('resetButton');
    resetButton.addEventListener('click', () => {
        removeLegend();
        removeExistingPaths();
        mask.style.display = 'none';
        spinner.style.display = 'none';
    });

    document.getElementById('numRoutesInput').addEventListener('input', function (e) {
        var value = parseInt(e.target.value);
        if (value < 1) {
            e.target.value = 1;
        } else if (value > 5) {
            e.target.value = 5;
        }
    });

});

function validateKey() {
    fetch(`${COORD_BASE_URL}?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=${API_KEY}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'REQUEST_DENIED') {
                console.error('Invalid API key');
            } else {
                loadGoogleMaps();
                initMap();
                mask.style.display = 'none';
            }
        })
        .catch(error => console.error('Error:', error));
}

async function initMap(position = {
    lng: -111.9412691,
    lat: 33.4243385
}) { // Default is Paris -111.9412691,33.4243385
    const {
        Map
    } = await google.maps.importLibrary("maps");

    // The map, centered at the provided position or default
    map = new Map(document.getElementById("map"), {
        zoom: 16,
        center: position,
        mapId: "MAIN_MAP_ID",
    });
}

// Mark the start and stop points on the map
function markStartAndStop(map, start, stop) {
    markerData = [];
    let startIcon = new google.maps.Marker({
        position: start,
        map: map,
        title: 'Start',
        icon: {
            url: startMarkerIcon,
            scaledSize: new google.maps.Size(45, 45)
        }
    });

    // Create the stop marker
    let stopIcon = new google.maps.Marker({
        position: stop,
        map: map,
        title: 'Stop',
        icon: {
            url: stopMarkerIcon,
            scaledSize: new google.maps.Size(45, 45)
        }
    });
    markerData.push(startIcon);
    markerData.push(stopIcon);
}

// Function to remove all polyline markers and paths
function removeExistingPaths() {

    markerData.forEach(marker => {
        // Remove the marker
        if (marker && typeof marker.setMap === 'function') {
            marker.setMap(null);
        }
    });

    // Remove the polyline
    polylineData.forEach(polyline => {
        // Remove the polyline
        if (polyline && typeof polyline.setMap === 'function') {
            polyline.setMap(null);
        }
    });
}

// Render the paths on the map
function renderPaths(pathsData) {
    let bounds = new google.maps.LatLngBounds();
    let infoWindow = new google.maps.InfoWindow();

    // Filter out the elements with null paths
    let validPathsData = pathsData.filter(op => op.path !== null && op.path.length > 1);

    // If all paths were null and When no path is found because of city bounds
    if (validPathsData.length === 0 || !validPathsData) {
        alert('Please specify the locations more precisely. Currently, a valid path between the source and destination cannot be found.');
        return;
    }

    let op = validPathsData[0];
    markStartAndStop(map, {
        lat: op.path[0][1],
        lng: op.path[0][0]
    }, {
        lat: op.path[op.path.length - 1][1],
        lng: op.path[op.path.length - 1][0]
    });
    polylineData = [];


    validPathsData.forEach(pathObj => {
        const formattedPath = pathObj.path.map(coord => ({
            lat: coord[1],
            lng: coord[0]
        }));
        const path = new google.maps.Polyline({
            path: formattedPath,
            geodesic: true,
            strokeColor: colorDict[pathObj.typeOfPath],
            strokeOpacity: 1,
            strokeWeight: 8
        });
        polylineData.push(path);

        // Add a listener for the mouseover event
        path.addListener('mouseover', function (event) {
            path.setOptions({
                strokeWeight: 12
            }); // Increase stroke weight

            // Set the content and position of the InfoWindow
            infoWindow.setContent(`
                <div style="font-family: Arial, sans-serif; margin: 10px;">
                    <p style="margin-bottom: 0; font-size: 1rem;">The selected path is <strong style="font-weight: bold;">${colorDictLegend[pathObj.typeOfPath]}</strong>
                    .</p>
                    <p style="margin-bottom: 0; font-size: 1rem;">Total distance is <strong style="font-weight: bold;">${(pathObj.length).toFixed(2)} metres</strong>.</p>
                </div>
            `);
            infoWindow.setPosition(event.latLng);

            // Open the InfoWindow
            infoWindow.open(map);
        });

        // Add a listener for the mouseout event
        path.addListener('mouseout', function () {
            path.setOptions({
                strokeWeight: 8
            }); // Reset stroke weight

            // Close the InfoWindow
            infoWindow.close();
        });

        // Extend the bounds to include each point of the polyline
        formattedPath.forEach(point => {
            bounds.extend(point);
        });

        // Assuming `map` is your Google Map object
        path.setMap(map);
    });

    // Adjust the map's viewport to fit the bounds
    map.fitBounds(bounds);
}

// Fetch the paths from the backend API
async function getPaths(origin, destination, travelMode, numRoutes) {
    const response = await fetch(`${API_BASE_URL}/get-path`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            origin: origin,
            destination: destination,
            travelMode: travelMode,
            numRoutes: numRoutes
        }),
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
}

// Get coordinates of an address from the Geocoding API
async function getCoordinates(address) {
    let url = `${COORD_BASE_URL}?address=${encodeURIComponent(address)}&key=${API_KEY}`
    const response = await fetch(url);
    const data = await response.json();
    if (data.status === 'OK') {
        const {
            lat,
            lng
        } = data.results[0].geometry.location;
        return [lat, lng];
    } else {
        throw new Error('Geocoding API request failed');
    }
}

// Remove the legend from the map
function removeLegend() {
    // Check if the legend already exists
    let oldLegend = document.getElementById('legend');
    if (oldLegend) {
        // If it does, remove it
        oldLegend.remove();
    }
}

// Create the legend and add it to the map
function createLegend(pathsData) {

    // Create main div
    let div = document.createElement('div');
    div.id = 'legend';
    div.style.cssText = 'background-color: #D3D3D3; padding: 5px; text-align: left; font-family: Arial, sans-serif; border-radius: 5px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.15);';

    // Create h3
    let h3 = document.createElement('h3');
    h3.style.cssText = 'margin-top: 0; font-size: 12px; color: #333;';
    h3.textContent = 'Color coding for paths:';
    div.appendChild(h3);

    // Create legend for start marker
    let startLegend = document.createElement('div');
    startLegend.innerHTML = '<img src="' + startMarkerIcon + '" height="20" width="20"> Start';
    startLegend.style.marginBottom = '10px'; // Add some space below the start legend
    div.appendChild(startLegend);

    // Create legend for stop marker
    let stopLegend = document.createElement('div');
    stopLegend.innerHTML = '<img src="' + stopMarkerIcon + '" height="20" width="20"> Stop';
    stopLegend.style.marginBottom = '10px'; // Add some space below the stop legend
    div.appendChild(stopLegend);

    // Filter out the elements with null paths
    let validPathsData = pathsData.filter(op => op.path !== null && op.path.length > 1);

    // If all paths were null and When no path is found because of city bounds
    if (validPathsData.length === 0 || !validPathsData) {
        return;
    }
    
    validPathsData.forEach(pathObj => {
        let p = document.createElement('p');
        p.style.cssText = 'font-size: 12px; margin: 10px 0; line-height: 1.5em; color: #333;';

        let span = document.createElement('span');
        span.style.cssText = 'display: inline-block; width: 12px; height: 12px; margin-right: 10px; vertical-align: middle; background-color: ' + colorDict[pathObj.typeOfPath] + ';';
        span.textContent = '\u00A0\u00A0\u00A0'; // Non-breaking spaces

        p.appendChild(span);
        p.appendChild(document.createTextNode(colorDictLegend[pathObj.typeOfPath]));
        div.appendChild(p);
    });

    // Add the legend to the map
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(div);
}

window.initAutocomplete = function () {
    var sourceInput = document.getElementById('sourceInput');
    var sourceAutocomplete = new google.maps.places.Autocomplete(sourceInput);
    var destinationInput = document.getElementById('destinationInput');
    var destinationAutocomplete = new google.maps.places.Autocomplete(destinationInput);
}
