import json
import time
import paho.mqtt.client as mqtt

# Paramètres MQTT
mqtt_broker = "broker.hivemq.com"
mqtt_port = 1883
mqtt_topic = "smartplant/sensor"

# Charger les données depuis le fichier JSON
with open("test_data.json", "r") as f:
    plants_data = json.load(f)

# Créer le client MQTT
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.connect(mqtt_broker, mqtt_port, 60)

# Publier chaque donnée avec un petit délai
for data in plants_data:
    client.publish(mqtt_topic, json.dumps(data))
    print("[MQTT] Envoyé :", data)
    time.sleep(1)  # pause 1 sec pour simuler envoi réel

client.disconnect()
print(" Tous les messages ont été envoyés")
