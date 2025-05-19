import threading
from flask import Flask
import paho.mqtt.client as mqtt
import time
import json
import random

# === Flask server (pour empêcher mise en veille) ===
app = Flask(__name__)

@app.route("/")
def home():
    return "Service MQTT actif"

def run_flask():
    app.run(host="0.0.0.0", port=10000)  # Port HTTP obligatoire pour Render

# === Script MQTT existant ===
broker = "broker.emqx.io"
port = 1883
topic = "module"

client = mqtt.Client()
client.connect(broker, port)

base_module = {
    "module_id": "bat1.m1",
    "tension": 52,
    "courant": 0.0,
    "soc": 28,
    "temperature_zone1": 21.0,
    "temperature_zone2": 21.0,
    "temperature_zone3": 21.0,
    "temperature_zone4": 21.0,
    "puissance_consomme": 0,
    "cycle_vie": 200
}

def generate_dynamic_module(base):
    return {
        "module_id": base["module_id"],
        "tension": round(base["tension"] + random.uniform(-0.05, 0.05), 2),
        "courant": round(base["courant"] + random.uniform(0, 0), 2),
        "soc": max(0, min(100, base["soc"] + random.randint(0, 0))),
        "temperature_zone1": round(base["temperature_zone1"] + random.uniform(-0.3, 0.3), 1),
        "temperature_zone2": round(base["temperature_zone2"] + random.uniform(-0.3, 0.3), 1),
        "temperature_zone3": round(base["temperature_zone3"] + random.uniform(-0.3, 0.3), 1),
        "temperature_zone4": round(base["temperature_zone4"] + random.uniform(-0.3, 0.3), 1),
        "puissance_consomme": max(0, base["puissance_consomme"] + random.randint(0, 0)),
        "cycle_vie": base["cycle_vie"] + random.randint(0, 0)
    }

def mqtt_loop():
    while True:
        data = generate_dynamic_module(base_module)
        payload = json.dumps(data)
        print(f"Envoi vers MQTT: {payload}")
        client.publish(topic, payload)
        client.loop()
        time.sleep(60)

# === Lancer le serveur Flask et la boucle MQTT en parallèle ===
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    mqtt_loop()
