import { getEnvironmentVariable } from './util.js';

/**
 * @license
 * Copyright 2019 Google LLC. All Rights Reserved.
 * SPDX-License-Identifier: Apache-2.0
 */
// Initialize and add the map
let map;
let directionsRenderers = [];

function loadGoogleMaps() {
    (g => {
        var h, a, k, p = "The Google Maps JavaScript API", c = "google", l = "importLibrary", q = "__ib__", m = document, b = window; b = b[c] || (b[c] = {}); var d = b.maps || (b.maps = {}), r = new Set, e = new URLSearchParams, u = () => h || (h = new Promise(async (f, n) => { await (a = m.createElement("script")); e.set("libraries", [...r] + ""); for (k in g) e.set(k.replace(/[A-Z]/g, t => "_" + t[0].toLowerCase()), g[k]); e.set("callback", c + ".maps." + q); a.src = `https://maps.${c}apis.com/maps/api/js?` + e; d[q] = f; a.onerror = () => h = n(Error(p + " could not load.")); a.nonce = m.querySelector("script[nonce]")?.nonce || ""; m.head.append(a) })); d[l] ? console.warn(p + " only loads once. Ignoring:", g) : d[l] = (f, ...n) => r.add(f) && u().then(() => d[l](f, ...n))
    })({
        key: "",
        v: "weekly",
        // Use the 'v' parameter to indicate the version to use (weekly, beta, alpha, etc.).
        // Add other bootstrap parameters as needed, using camel case.
    });
}

// Function to clear previous routes from the map
function clearPreviousRoutes() {
    if (directionsRenderers.length > 0) {
        directionsRenderers.forEach(renderer => {
            renderer.setMap(null); // Set the map to null to remove the route from the map
        });
        directionsRenderers = []; // Clear the array of DirectionsRenderers
    }
}

// Function to refresh the map and fetch new routes
function refreshMap(source, destination, numRoutes, mode) {
    const directionsService = new google.maps.DirectionsService();

    const request = {
        origin: source,
        destination: destination,
        travelMode: google.maps.TravelMode[mode],
        provideRouteAlternatives: true // Request multiple route alternatives
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
            strokeColor: index === fastestRouteIndex ? '#28A745' : '#87CEEB', // Dark green for fastest route, light blue for others
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
    // You can add code here to display the route details wherever you want on your HTML page
    // For example, you can append the routeDetails to a specific div element
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

        console.log('Source:', sourceValue);
        console.log('Destination:', destinationValue);
        console.log('Number of Routes:', numRoutes);
        console.log('Travel Mode:', travelMode);

        // Refresh the map and fetch new routes based on input values
        refreshMap(sourceValue, destinationValue, numRoutes, travelMode);
    });
});

async function initMap() {
    // [START maps_add_map_instantiate_map]
    // The location of Uluru
    const position = { lat: 33.42365263050725, lng: -111.93938982730594 };
    // Request needed libraries.
    //@ts-ignore
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

    // The map, centered at Uluru
    map = new Map(document.getElementById("map"), {
        zoom: 16,
        center: position,
        mapId: "DEMO_MAP_ID",
    });

    // [END maps_add_map_instantiate_map]
    // [START maps_add_map_instantiate_marker]
    // The marker, positioned at Uluru
    const marker = new AdvancedMarkerElement({
        map: map,
        position: position,
        title: "Uluru",
    });

    markLines(map);
    // [END maps_add_map_instantiate_marker]
}

function markLines(map) {



    // Define the coordinates for the path
    const pathCoords1 = [
        // { lat: 33.42365263050725, lng: -111.93938982730594 },
        // { lat: 33.32365263050725, lng: -111.83938982730594 },
        // { lat: 33.22365263050725, lng: -111.73938982730594 },
        // { lat: 33.12365263050725, lng: -111.63938982730594 },
        // { lat: 33.02365263050725, lng: -111.53938982730594 },
        // { lat: 33.42365263050725, lng: -111.93938982730594 },
        { lat: 33.42435443897127, lng: -111.93666280025651 },
        { lat: 33.42200992035623, lng: -111.93665490961563 },
    ];

    const pathCoords2 = [
        // { lat: 33.42365263050725, lng: -111.93938982730594 },
        // { lat: 33.32365263050725, lng: -111.83938982730594 },
        // { lat: 33.22365263050725, lng: -111.73938982730594 },
        // { lat: 33.12365263050725, lng: -111.63938982730594 },
        // { lat: 33.02365263050725, lng: -111.53938982730594 },
        // { lat: 33.42365263050725, lng: -111.93938982730594 },
        { lat: 33.4243215107774, lng: -111.93498998439345 },
        { lat: 33.42202967780008, lng: -111.93496631247086 },
    ];

    // Construct the polyline
    const path1 = new google.maps.Polyline({
        path: pathCoords1,
        geodesic: true,
        strokeColor: "#FF0000",
        strokeOpacity: 0.8,
        strokeWeight: 4
    });
    const path2 = new google.maps.Polyline({
        path: pathCoords2,
        geodesic: true,
        strokeColor: "#FF0000",
        strokeOpacity: 0.8,
        strokeWeight: 4
    });

    // Set the polyline on the map
    path1.setMap(map);
    path2.setMap(map);
}
// async function getPathBetweenLocations(location1, location2) {
//     const geocoder = new google.maps.Geocoder();
//     const geocode1 = await geocodeAddress(location1, geocoder);
//     if (!geocode1) return null; // Handle error if geocoding fails

//     const geocode2 = await geocodeAddress(location2, geocoder);
//     if (!geocode2) return null; // Handle error if geocoding fails

//     // Calculate path between the two locations
//     const path = [
//         { lat: geocode1.lat, lng: geocode1.lng },
//         { lat: geocode2.lat, lng: geocode2.lng }
//     ];

//     return path;
// }


// async function geocodeAddress(address, geocoder) {
//     return new Promise((resolve, reject) => {
//         geocoder.geocode({ address: address }, (results, status) => {
//             if (status === "OK" && results && results.length > 0) {
//                 const location = results[0].geometry.location;
//                 resolve({ lat: location.lat(), lng: location.lng() });
//             } else {
//                 console.error("Geocode was not successful for the following reason:", status);
//                 resolve(null);
//             }
//         });
//     });
// }

// async function getAllPathsBetweenLocations(location1, location2) {
//     // Initialize Google Maps Directions Service
//     const directionsService = new google.maps.DirectionsService();

//     // Request directions between location1 and location2
//     const request = {
//         origin: location1,
//         destination: location2,
//         travelMode: google.maps.TravelMode.DRIVING, 
//         provideRouteAlternatives: true 
//     };

//     return new Promise((resolve, reject) => {
//         directionsService.route(request, (response, status) => {
//             if (status === "OK") {
//                 const paths = [];
//                 response.routes.forEach(route => {
//                     const path = [];
//                     route.overview_path.forEach(point => {
//                         path.push({ lat: point.lat(), lng: point.lng() });
//                     });
//                     paths.push(path);
//                 });
//                 resolve(paths);
//             } else {
//                 console.error("Directions request failed:", status);
//                 resolve(null);
//             }
//         });
//     });
// }

window.onload = function () {
    loadGoogleMaps();
    initMap();
    const location1 = "75001 Paris, France";
    const location2 = "75006 Paris, France";
    // getAllPathsBetweenLocations(location1, location2)
    //     .then(paths => console.log(paths))
    //     .catch(err => console.error(err));

};
// [END maps_add_map]