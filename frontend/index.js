// Initialize and add the map
let map;
let directionsRenderers = [];

// API related constants
const API_BASE_URL = 'http://localhost:8080';
const COORD_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json";
const API_KEY = "key";

// Color Map
const colorDict = {
    "shaded": "#6bb06e",
    "shortest": "#f18c60",
    "50-50": "#8AA7BF",
    "70-30": "#d5a698",
    "30-70": "#c0f3c0"
};

const colorDictLegend = {
    "shaded": "Most Shaded Path",
    "shortest": "Shortest Path",
    "50-50": "50% Distance - 50% Shaded Path Ratio",
    "70-30": "70% Distance - 30% Shaded Path Ratio",
    "30-70": "30% Distance - 70% Shaded Path Ratio"
};
const colorHues = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#8B00FF', '#FF00FF'];
const green = '#28A745';

function loadGoogleMaps() {
    (g => {
        var h, a, k, p = "The Google Maps JavaScript API", c = "google", l = "importLibrary", q = "__ib__", m = document, b = window; b = b[c] || (b[c] = {}); var d = b.maps || (b.maps = {}), r = new Set, e = new URLSearchParams, u = () => h || (h = new Promise(async (f, n) => { await (a = m.createElement("script")); e.set("libraries", [...r] + ""); for (k in g) e.set(k.replace(/[A-Z]/g, t => "_" + t[0].toLowerCase()), g[k]); e.set("callback", c + ".maps." + q); a.src = `https://maps.${c}apis.com/maps/api/js?` + e; d[q] = f; a.onerror = () => h = n(Error(p + " could not load.")); a.nonce = m.querySelector("script[nonce]")?.nonce || ""; m.head.append(a) })); d[l] ? console.warn(p + " only loads once. Ignoring:", g) : d[l] = (f, ...n) => r.add(f) && u().then(() => d[l](f, ...n))
    })({
        key: API_KEY,
        v: "weekly",
        // Use the 'v' parameter to indicate the version to use (weekly, beta, alpha, etc.).
        // Add other bootstrap parameters as needed, using camel case.
    });
}

function refreshShadedPaths(source, destination, numRoutes, mode) {

    removeLegend();
    Promise.all([
        getCoordinates(source),
        getCoordinates(destination)
    ]).then(([coords1, coords2]) => {
        getPaths(coords1, coords2, numRoutes, mode)
            .then(pathsData => {
                // Render the paths on the map
                renderPaths(pathsData);
            })
            .catch(error => console.error('Error:', error));
        createLegend();
    }).catch(error => console.error('Error:', error));

}

// DOMContentLoaded event listener
document.addEventListener('DOMContentLoaded', () => {
    loadGoogleMaps();

    const searchButton = document.getElementById('searchButton');
    searchButton.addEventListener('click', () => {
        const sourceValue = document.getElementById('sourceInput').value;
        const destinationValue = document.getElementById('destinationInput').value;
        const numRoutes = parseInt(document.getElementById('numRoutesInput').value);
        const travelMode = document.querySelector('input[name="travelMode"]:checked').value;

        // Refresh the map and fetch new routes based on input values
        refreshShadedPaths(sourceValue, destinationValue, numRoutes, travelMode);
    });
});

async function initMap(position = { lng: -111.9412691, lat: 33.4243385 }) { // Default is Paris -111.9412691,33.4243385
    const { Map } = await google.maps.importLibrary("maps");

    // The map, centered at the provided position or default
    map = new Map(document.getElementById("map"), {
        zoom: 16,
        center: position,
        mapId: "MAIN_MAP_ID",
    });
}

function renderPaths(pathsData) {
    let bounds = new google.maps.LatLngBounds();
    let infoWindow = new google.maps.InfoWindow();

    pathsData.forEach(pathObj => {
        const formattedPath = pathObj.path.map(coord => ({ lat: coord[1], lng: coord[0] }));
        const path = new google.maps.Polyline({
            path: formattedPath,
            geodesic: true,
            strokeColor: colorDict[pathObj.typeOfPath],
            strokeOpacity: 1,
            strokeWeight: 8
        });

        // Add a listener for the mouseover event
        path.addListener('mouseover', function (event) {
            path.setOptions({ strokeWeight: 10 });  // Increase stroke weight

            // Set the content and position of the InfoWindow
            infoWindow.setContent(`The selected path is ${pathObj.typeOfPath} path.`);
            infoWindow.setPosition(event.latLng);

            // Open the InfoWindow
            infoWindow.open(map);
        });

        // Add a listener for the mouseout event
        path.addListener('mouseout', function () {
            path.setOptions({ strokeWeight: 8 });  // Reset stroke weight

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

window.onload = function () {
    loadGoogleMaps();
    initMap();
};

async function getPaths(origin, destination, numRoutes, mode) {
    const response = await fetch(`${API_BASE_URL}/get-path`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            origin: origin,
            destination: destination,
            travelMode: google.maps.TravelMode[mode],
            numRoutes: numRoutes
        }),
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
}

async function getCoordinates(address) {
    let url = `${COORD_BASE_URL}?address=${encodeURIComponent(address)}&key=${API_KEY}`
    const response = await fetch(url);
    const data = await response.json();
    if (data.status === 'OK') {
        const { lat, lng } = data.results[0].geometry.location;
        return [lat, lng];
    } else {
        throw new Error('Geocoding API request failed');
    }
}

function removeLegend() {
    // Check if the legend already exists
    let oldLegend = document.getElementById('legend');
    if (oldLegend) {
        // If it does, remove it
        oldLegend.remove();
    }
}

function createLegend() {

    // Create main div
    let div = document.createElement('div');
    div.id = 'legend';
    div.style.cssText = 'background-color: #D3D3D3; padding: 10px; text-align: left; font-family: Arial, sans-serif; border-radius: 5px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.15);';

    // Create h3
    let h3 = document.createElement('h3');
    h3.style.cssText = 'margin-top: 0; font-size: 18px; color: #333;';
    h3.textContent = 'Color Coding';
    div.appendChild(h3);

    // Create p elements
    for (let key in colorDict) {
        let p = document.createElement('p');
        p.style.cssText = 'font-size: 12px; margin: 10px 0; line-height: 1.5em; color: #333;';

        let span = document.createElement('span');
        span.style.cssText = 'display: inline-block; width: 18px; height: 18px; margin-right: 10px; vertical-align: middle; background-color: ' + colorDict[key] + ';';
        span.textContent = '\u00A0\u00A0\u00A0'; // Non-breaking spaces

        p.appendChild(span);
        p.appendChild(document.createTextNode(colorDictLegend[key]));
        div.appendChild(p);
    }

    // Add the legend to the map
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(div);
}