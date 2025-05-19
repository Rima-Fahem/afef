import paho.mqtt.client as mqtt
import time
import json
import random

broker = "broker.emqx.io"
port = 1883
topic = "module"

client = mqtt.Client()
client.connect(broker, port)

# Valeurs de base mises à jour
base_module = {
    "module_id": "bat1.m1",
    "tension": 52,
    "courant": 0.0,
    "soc": 28,  # Peut rester dynamique si souhaité
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

while True:
    module_data = generate_dynamic_module(base_module)
    
    data = module_data
        
    

    payload = json.dumps(data)
    print(f"Taille du message : {len(payload)} bytes")
    result = client.publish(topic, payload, qos=1)
    client.loop()
    status = result[0]
    if status == 0:
        print(f"Message envoyé sur {topic}: {payload}")
    else:
        print("Échec d'envoi")
    time.sleep(60)
