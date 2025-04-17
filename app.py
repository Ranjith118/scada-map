from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)

TOPOLOGY_FILE = "topologies.json"

# Load topologies from file
def load_topologies():
    if os.path.exists(TOPOLOGY_FILE):
        with open(TOPOLOGY_FILE, "r") as f:
            return json.load(f)
    return []

# Save topologies to file
def save_topologies(topologies):
    with open(TOPOLOGY_FILE, "w") as f:
        json.dump(topologies, f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/save-topology", methods=["POST"])
def save_topology():
    data = request.json
    topologies = load_topologies()
    topologies.append(data)
    save_topologies(topologies)
    return jsonify({"message": "Topology saved successfully"})

@app.route("/get-topologies", methods=["GET"])
def get_topologies():
    topologies = load_topologies()
    return jsonify(topologies)

@app.route("/get-topology/<int:index>", methods=["GET"])
def get_topology(index):
    topologies = load_topologies()
    if 0 <= index < len(topologies):
        return jsonify(topologies[index])
    return jsonify({"error": "Topology not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
