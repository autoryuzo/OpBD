from flask import Flask, jsonify, request, render_template
from systems.orvd_system.src.orvd_component.src import OrvdComponent
from broker.system_bus import SystemBus  # предположим, что у тебя есть SDK

app = Flask(__name__, template_folder="../../templates/web", static_folder="../../static/web")

# === Инициализация ORVD компонента ===
bus = SystemBus()  # твой внутренний брокер сообщений
orvd = OrvdComponent(component_id="orvd1", name="ORVD Demo", bus=bus)
print("ORVD Component running...")

# === Веб-страницы ===
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/drones")
def drones_page():
    return render_template("partials/pages/drones.html")

@app.route("/missions")
def missions_page():
    return render_template("partials/pages/missions.html")

@app.route("/zones")
def zones_page():
    return render_template("partials/pages/zones.html")

@app.route("/map")
def map_page():
    return render_template("partials/pages/map.html")


# === API для фронтенда ===
@app.route("/api/register_drone", methods=["POST"])
def api_register_drone():
    payload = request.json
    response = orvd._handle_register_drone({"payload": payload})
    return jsonify(response)

@app.route("/api/register_mission", methods=["POST"])
def api_register_mission():
    payload = request.json
    response = orvd._handle_register_mission({"payload": payload})
    return jsonify(response)

@app.route("/api/authorize_mission", methods=["POST"])
def api_authorize_mission():
    payload = request.json
    response = orvd._handle_authorize_mission({"payload": payload})
    return jsonify(response)

@app.route("/api/request_takeoff", methods=["POST"])
def api_request_takeoff():
    payload = request.json
    response = orvd._handle_request_takeoff({"payload": payload})
    return jsonify(response)

@app.route("/api/revoke_takeoff", methods=["POST"])
def api_revoke_takeoff():
    payload = request.json
    response = orvd._handle_revoke_takeoff({"payload": payload})
    return jsonify(response)

@app.route("/api/add_zone", methods=["POST"])
def api_add_zone():
    payload = request.json
    response = orvd._handle_add_zone({"payload": payload})
    return jsonify(response)

@app.route("/api/remove_zone", methods=["POST"])
def api_remove_zone():
    payload = request.json
    response = orvd._handle_remove_zone({"payload": payload})
    return jsonify(response)

@app.route("/api/history")
def api_history():
    response = orvd._handle_get_history({"payload": {}})
    return jsonify(response)


# === Запуск сервера ===
if __name__ == "__main__":
    app.run(debug=True, port=5000)