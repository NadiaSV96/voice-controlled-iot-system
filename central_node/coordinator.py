import paho.mqtt.client as mqtt
import yaml
from .mqtt_handler import MQTTHandler
from .state_manager import StateManager

class CentralNode:
    def __init__(self, config_file="config/central_config.yaml"):
        self.config = self.load_config(config_file)  # Charger la configuration YAML
        self.state_manager = StateManager()
        self.mqtt_handler = MQTTHandler(self.state_manager, config_file)  # Crée et configure le client MQTT
        self._setup_mqtt()

    def load_config(self, config_file):
        """ Charger la configuration depuis un fichier YAML """
        with open(config_file, "r") as file:
            return yaml.safe_load(file)
    
    def _setup_mqtt(self):
        """ Configuration du client MQTT, sans abonnement explicite ici """
        print("[CentralNode] Démarrage de la connexion MQTT.")

    def start(self):
        """ Démarre le système via le handler MQTT """
        self.mqtt_handler.start()

    def stop(self):
        """ Arrêt propre du système """
        self.mqtt_handler.stop()