// Initialize and add the map
let map;
let directionsRenderers = [];

// API related constants
const API_BASE_URL = 'http://localhost:8080';
const COORD_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json";
const API_KEY = "YOUR_API_KEY";

// Color Map
const colorDict = {
    "mostShaded": "#73B576",
    "shortest": "#A6D4EA",
    "halfHalf": "#8AA7BF",
    "seventyPercentShaded": "#85BF85",
    "seventyPercentShortest": "#3A548D"
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

// Function to clear previous routes from the map
function clearPreviousRoutes() {
    if (directionsRenderers.length > 0) {
        directionsRenderers.forEach(renderer => {
            renderer.setMap(null);
        });
        directionsRenderers = [];
    }
}

function refreshShadedPaths(source, destination, numRoutes, mode) {      

    Promise.all([
        getCoordinates(source),
        getCoordinates(destination)
    ]).then(([coords1, coords2]) => {
        let newCenter = { lat: coords1[0], lng: coords1[1] }; 
        map.setCenter(newCenter);

        getPaths(coords1, coords2, numRoutes, mode)
            .then(pathsData => {
                // Render the paths on the map
                renderPaths(pathsData);
            })
            .catch(error => console.error('Error:', error));
    }).catch(error => console.error('Error:', error));
    
}

// Function to refresh the map and fetch new routes
function refreshMap(source, destination, numRoutes, mode) {
    const directionsService = new google.maps.DirectionsService();

    const request = {
        origin: source,
        destination: destination,
        travelMode: google.maps.TravelMode[mode],
        provideRouteAlternatives: true
    };

    // Clear previous routes by setting them to null
    clearPreviousRoutes();

    directionsService.route(request, (result, status) => {
        if (status === 'OK') {
            const fastestRouteIndex = findFastestRoute(result.routes);

            // Render routes on the map
            result.routes.forEach((route, index) => {
                if (index !== fastestRouteIndex) {
                    renderRoute(route, result, index, fastestRouteIndex); // Render other routes
                }
            });

            // Render the fastest route after rendering other routes
            const fastestRoute = result.routes[fastestRouteIndex];
            if (fastestRoute) {
                renderRoute(fastestRoute, result, fastestRouteIndex, fastestRouteIndex); // Render fastest route
            }
        } else {
            console.error('Directions request failed:', status);
        }
    });
}

// Function to find the fastest route index
function findFastestRoute(routes) {
    let fastestRouteIndex = 0;
    let fastestRouteDuration = Number.MAX_VALUE;

    routes.forEach((route, index) => {
        const duration = route.legs.reduce((acc, leg) => acc + leg.duration.value, 0);
        if (duration < fastestRouteDuration) {
            fastestRouteDuration = duration;
            fastestRouteIndex = index;
        }
    });

    return fastestRouteIndex;
}

// Function to render a route on the map
function renderRoute(route, result, index, fastestRouteIndex) {
    const routeRenderer = new google.maps.DirectionsRenderer({
        map: map,
        directions: result,
        routeIndex: index,
        polylineOptions: {
            strokeColor: index === fastestRouteIndex ? green : colorHues[index % colorHues.length],
            strokeWeight: index === fastestRouteIndex ? 8 : 5
        }
    });

    // Add the renderer to directionsRenderers array
    directionsRenderers.push(routeRenderer);

    // Show route details for the fastest route
    if (index === fastestRouteIndex) {
        const routeDetails = createRouteDetails(route);
        showRouteDetails(routeDetails);
    }
}

// Function to create route details
function createRouteDetails(route) {
    const routeDetails = document.createElement('div');
    routeDetails.classList.add('card', 'mt-3', 'w-50');
    routeDetails.innerHTML = `
        <div class="card-body">
            <h5 class="card-title">Fastest Route: ${route.summary}</h5>
            <p class="card-text">Duration: ${route.legs[0].duration.text}</p>
            <p class="card-text">Distance: ${route.legs[0].distance.text}</p>
            <p class="card-text">Average Speed: ${calculateAverageSpeed(route)}</p>
        </div>
    `;

    // Add Bootstrap classes to the card elements
    routeDetails.querySelector('.card-body').classList.add('bg-success', 'text-white');
    routeDetails.querySelector('.card-title').classList.add('mb-3');
    routeDetails.querySelectorAll('.card-text').forEach(text => text.classList.add('mb-2', 'font-weight-bold'));

    return routeDetails;
}

// Function to show route details on the map
function showRouteDetails(routeDetails) {
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.innerHTML = ''; // Clear previous route details
    resultsContainer.appendChild(routeDetails);
}

// Function to calculate average speed
function calculateAverageSpeed(route) {
    const totalDistance = route.legs[0].distance.value; // in meters
    const totalDuration = route.legs[0].duration.value; // in seconds
    const totalDistanceInMiles = totalDistance * 0.000621371; // convert meters to miles
    const totalDurationInHours = totalDuration / 3600; // convert seconds to hours
    const averageSpeed = totalDistanceInMiles / totalDurationInHours; // miles per hour
    return averageSpeed.toFixed(2) + ' mph';
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
        // refreshMap(sourceValue, destinationValue, numRoutes, travelMode);
        refreshShadedPaths(sourceValue, destinationValue, numRoutes, travelMode);
    });
});

async function initMap(position = { lat: 48.8566, lng: 2.3522 }) { // Default is Paris
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
    pathsData.forEach(pathObj => {
        const formattedPath = pathObj.path.map(coord => ({ lat: coord[0], lng: coord[1] }));
        const path = new google.maps.Polyline({
            path: formattedPath,
            geodesic: true,
            strokeColor: colorDict[pathObj.typeOfPath],
            strokeOpacity: 1,
            strokeWeight: 8
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
    const response = await fetch(`${API_BASE_URL}/getPaths`, {
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

