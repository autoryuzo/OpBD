let map;
let dronesLayer = L.layerGroup();
let missionsLayer = L.layerGroup();
let zonesLayer = L.layerGroup();
let activeZones = []; // сюда сохраняем зоны для проверки

function initMap() {
    map = L.map('map').setView([55.7558, 37.6173], 10);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);

    dronesLayer.addTo(map);
    missionsLayer.addTo(map);
    zonesLayer.addTo(map);

    fetchZones();
    fetchMissions();
    fetchDrones();

    setInterval(() => {
        fetchZones();
        fetchMissions();
        fetchDrones();
    }, 5000);
}

// ==========================
// Зоны
// ==========================
function fetchZones() {
    fetch('/api/zones')
        .then(res => res.json())
        .then(data => {
            zonesLayer.clearLayers();
            activeZones = [];
            data.zones.forEach(zone => {
                if (!zone.active) return;
                const bounds = zone.bounds;
                const rectangle = L.rectangle([
                    [bounds.min_lat, bounds.min_lon],
                    [bounds.max_lat, bounds.max_lon]
                ], {color: 'red', weight: 1, fillOpacity: 0.2});
                rectangle.addTo(zonesLayer);
                activeZones.push(bounds); // сохраняем для проверки маршрутов
            });
        });
}

// ==========================
// Проверка точки на пересечение с зоной
// ==========================
function pointInZone(point, bounds) {
    return point.lat >= bounds.min_lat &&
           point.lat <= bounds.max_lat &&
           point.lon >= bounds.min_lon &&
           point.lon <= bounds.max_lon;
}

function routeViolatesZone(route) {
    for (let p of route) {
        for (let zone of activeZones) {
            if (pointInZone(p, zone)) return true;
        }
    }
    return false;
}

// ==========================
// Миссии
// ==========================
function fetchMissions() {
    fetch('/api/missions')
        .then(res => res.json())
        .then(data => {
            missionsLayer.clearLayers();
            data.missions.forEach(mission => {
                if (!mission.route) return;
                const latlngs = mission.route.map(p => [p.lat, p.lon]);
                const violates = routeViolatesZone(mission.route);
                const color = violates ? 'red' : 'blue';
                const polyline = L.polyline(latlngs, {color: color, weight: 2});
                polyline.addTo(missionsLayer);
                if (violates) {
                    polyline.bindPopup(`<b>${mission.mission_id}</b><br>⚠ Конфликт с запретной зоной`);
                } else {
                    polyline.bindPopup(`<b>${mission.mission_id}</b><br>Маршрут разрешен`);
                }
            });
        });
}

// ==========================
// Дроны
// ==========================
function fetchDrones() {
    fetch('/api/drones')
        .then(res => res.json())
        .then(data => {
            dronesLayer.clearLayers();
            data.drones.forEach(drone => {
                if (!drone.coords) return;
                const marker = L.circleMarker([drone.coords.lat, drone.coords.lon], {
                    radius: 6,
                    color: 'green',
                    fillOpacity: 1
                }).bindPopup(`<b>${drone.drone_id}</b><br>Status: ${drone.status}`);
                marker.addTo(dronesLayer);
            });
        });
}

document.addEventListener('DOMContentLoaded', () => {
    initMap();
});