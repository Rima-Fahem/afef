import threading
from flask import Flask
import paho.mqtt.client as mqtt
import time
import json
import random
import os

# === Flask app pour garder l'app vivante ===
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Service MQTT actif"

def run_flask():
    port = int(os.environ.get("PORT", 10000))  # Support Render
    app.run(host="0.0.0.0", port=port)

# === Configuration MQTT ===
broker = "broker.emqx.io"
port_mqtt = 1883
topic = "module"

client = mqtt.Client()
client.connect(broker, port_mqtt)

# === État initial ===
base_module = {
    "module_id": "bat1.m1",
    "tension": 52.0,
    "courant": 0.0,
    "soc": 100.0,
    "temperature_zone1": 21.0,
    "temperature_zone2": 21.0,
    "temperature_zone3": 21.0,
    "temperature_zone4": 21.0,
    "puissance_consomme": 0.0,
    "cycle_vie": 200
}

# Mode initial
mode = "decharge"

def simulate_module(state, mode):
    if mode == "decharge":
        courant = round(random.uniform(5, 50), 2)
    else:
        courant = round(random.uniform(-50, -5), 2)

    tension = round(state["tension"] + courant * 0.01 + random.uniform(-0.2, 0.2), 2)
    tension = max(48.0, min(54.0, tension))

    puissance = round(abs(tension * courant), 2)

    # Variation SOC : 16% par étape (pour aller de 100% à 20% en 5 pas)
    soc_step = 16.0

    if mode == "decharge":
        nouveau_soc = max(20.0, state["soc"] - soc_step)
    else:
        nouveau_soc = min(100.0, state["soc"] + soc_step)

    temp_base = 21.0 + random.uniform(-0.5, 0.5)
    temp_variation = puissance * 0.0005

    return {
        "module_id": state["module_id"],
        "tension": tension,
        "courant": courant,
        "soc": round(nouveau_soc, 2),
        "temperature_zone1": round(temp_base + temp_variation, 1),
        "temperature_zone2": round(temp_base + temp_variation + random.uniform(-0.3, 0.3), 1),
        "temperature_zone3": round(temp_base + temp_variation + random.uniform(-0.3, 0.3), 1),
        "temperature_zone4": round(temp_base + temp_variation + random.uniform(-0.3, 0.3), 1),
        "puissance_consomme": puissance,
        "cycle_vie": state["cycle_vie"]
    }


def mqtt_loop():
    global mode
    while True:
        module_data = simulate_module(base_module, mode)
        base_module.update(module_data)

        # Passage décharge <-> recharge
        if mode == "decharge" and base_module["soc"] <= 20:
            print("🔋 SOC 20% atteint → RECHARGE")
            mode = "recharge"
        elif mode == "recharge" and base_module["soc"] >= 100:
            print("⚡ SOC 100% atteint → DÉCHARGE")
            mode = "decharge"

        print(f"[{mode.upper()}] SOC: {base_module['soc']}% | Courant: {base_module['courant']}A | Tension: {base_module['tension']}V | Puissance: {base_module['puissance_consomme']}W")

        payload = json.dumps(module_data)
        client.publish(topic, payload, qos=1)
        client.loop()

        time.sleep(1800)

# === Lancement en parallèle ===
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    mqtt_loop()
