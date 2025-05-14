import paho.mqtt.client as mqtt
import yaml
from .state_manager import StateManager
from .event_logger import MongoDBManager
from modules.door_module import DoorModule
from datetime import datetime
from .voice_controler_maison import SyntheseVocale

class MQTTHandler:
    def __init__(self, state_manager: StateManager, config_path="config/central_config.yaml"):


        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        self.broker = config["mqtt"]["broker"]
        self.port = config["mqtt"]["port"]
        self.topics = config["mqtt"]["topics"]

        self.client = mqtt.Client()

        self.state_manager = state_manager
        self.door_module = DoorModule()
        self.mongo_manager = MongoDBManager(config_path)
        self.vocal = SyntheseVocale()
        # Attacher les callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message  # Gère tous les messages ici

    def on_connect(self, client, userdata, flags, rc):
        print(f"[CentralNode] Connecté au broker {self.broker}:{self.port} avec le code de résultat {rc}")
        self.client.subscribe(self.topics["mode_set"])
        print(f"[CentralNode] Abonnement au topic: {self.topics['mode_set']}")
        
        for command_topic in self.topics["client_commands"].values():
            self.client.subscribe(command_topic)
            print(f"[CentralNode] Abonnement au topic: {command_topic}")

        for module_topic in self.topics["modules_capteurs"].values():
            self.client.subscribe(module_topic)
            print(f"[CentralNode] Abonnement au topic: {module_topic}")

        for module_topic in self.topics["modules_status"].values():
            self.client.subscribe(module_topic)
            print(f"[CentralNode] Abonnement au topic: {module_topic}")
    
    def connect(self):
        self.client.connect(self.broker, self.port, 60)
    
    def start(self):
        """ Démarre la connexion et la boucle MQTT """
        self.connect()
        self.client.loop_forever()

    def stop(self):
        """ Arrêt propre de la boucle MQTT """
        self.client.loop_stop()
        self.client.disconnect()
        print("[CentralNode] Déconnecté proprement")
    
    def subscribe(self, topic):
        """ S'abonner à un topic MQTT spécifique """
        self.client.subscribe(topic)

    def publish(self, topic, payload):
        """ Publier un message MQTT sur un topic spécifique """
        self.client.publish(topic, payload)

    def on_message(self, client, userdata, msg):
        """ Gérer les messages reçus via MQTT """
        # Gérer la logique des messages dans MQTTHandler
        if msg.topic == self.topics["client_commands"]["database_export"]:
            self.fichier_csv_exporte(msg)  
        
        if msg.topic == self.topics["mode_set"]:  # Vérifie si le message concerne le changement de mode
            new_mode = msg.payload.decode()
            print(f"Message reçu sur {msg.topic}: {new_mode}")
            if new_mode in ["auto", "manual", "security"]:

                self.publish(self.topics['mode_status'], new_mode)
                self.state_manager.update_mode(new_mode)  # Mettre à jour les états internes
                self.log_event(f"Mode changé vers '{new_mode}'", source="client_remote", action="mode_change")

        if self.state_manager.mode_actif == 'auto':
            self.traiter_mode_auto(msg)

        if self.state_manager.mode_actif == 'manual':
            self.traiter_mode_manual(msg)

        if self.state_manager.mode_actif == 'security':
            self.traiter_mode_securite(msg)

        if msg.topic in self.topics["modules_status"].values():
            payload = msg.payload.decode()
            print(f"Message reçu sur {msg.topic}: {payload}")

    def traiter_mode_auto(self,msg):
        if msg.topic == self.topics["modules_capteurs"]["pir_sensor"]:
            payload = msg.payload.decode()
            print(f"Message reçu sur {msg.topic}: {payload}")
            self.log_event("Mouvement détectée...Ouverture de la porte et la lumière", module="pir_module", source="pir_sensor", action="open_door & open_light")
            self.publish(self.topics['modules_commands']['open_door'], 'OPEN THE DOOR')
            self.door_module.porte_est_active = True
            self.publish(self.topics['modules_commands']['open_light'], 'OPEN THE LIGHT')
        elif msg.topic == self.topics["client_commands"]["client_open_door"]:
            self.publish(self.topics['modules_commands']['open_door'], 'OPEN THE DOOR')
            self.log_event("Porte ouverte par commande client (mode auto).", module="door_module", source="client_remote", action="open_door")
            self.door_module.porte_est_active = True
        elif msg.topic == self.topics["client_commands"]["client_close_door"]:
            self.publish(self.topics['modules_commands']['close_door'], 'CLOSE THE DOOR')
            self.door_module.porte_est_active = False
            self.log_event("Porte fermée par commande client (mode auto).", module="door_module", source="client_remote", action="close_door")
        elif msg.topic == self.topics["client_commands"]["client_open_light"]:
            self.publish(self.topics['modules_commands']['open_light'], 'OPEN THE LIGHT')
            self.log_event("Allumer la lumière par commande client (mode auto).", module="light_module", source="client_remote", action="open_light")
        elif msg.topic == self.topics["client_commands"]["client_close_light"]:
            self.publish(self.topics['modules_commands']['close_light'], 'CLOSE THE LIGHT')
            self.log_event("Éteindre la lumière par commande client (mode auto).", module="light_module", source="client_remote", action="close_light")
        elif msg.topic == self.topics["client_commands"]["client_heater_on"]:
            self.publish(self.topics['modules_commands']['heater_on'], 'OPEN THE HEATER')
            self.log_event("Allumer le chauffage par commande client (mode auto).", module="temperature_module", source="client_remote", action="heater_on")
        elif msg.topic == self.topics["client_commands"]["client_heater_off"]:
            self.publish(self.topics['modules_commands']['heater_off'], 'CLOSE THE HEATER')
            self.log_event("Éteindre le chauffage par commande client (mode auto).", module="temperature_module", source="client_remote", action="heater_off")
        elif msg.topic == self.topics["client_commands"]["client_ventilation_on"]:
            self.publish(self.topics['modules_commands']['ventilation_on'], 'OPEN THE VENTILATION')
            self.log_event("Allumer la ventilation par commande client (mode auto).", module="temperature_module", source="client_remote", action="ventilation_on")
        elif msg.topic == self.topics["client_commands"]["client_ventilation_off"]:
            self.publish(self.topics['modules_commands']['ventilation_off'], 'CLOSE THE VENTILATION')
            self.log_event("Éteindre la ventilation par commande client (mode auto).", module="temperature_module", source="client_remote", action="ventilation_off")
        
        # Partie manuel aussi accepter en auto
        if msg.topic == self.topics["modules_capteurs"]["switch_porte_ouverte"]:
            self.publish(self.topics['modules_commands']['open_door'], 'OPEN THE DOOR')
            self.log_event("Porte ouverte manuellement (mode auto).", module="door_module", source="switch_button", action="open_door")
            self.door_module.porte_est_active = True
            self.vocal.parler("Porte ouverte")
        elif msg.topic == self.topics["modules_capteurs"]["switch_porte_fermer"]:
            self.publish(self.topics['modules_commands']['close_door'], 'CLOSE THE DOOR')
            self.log_event("Porte fermée manuellement (mode auto).", module="door_module", source="switch_button", action="close_door")
            self.door_module.porte_est_active = False
            self.vocal.parler("Porte fermée.")
        elif msg.topic == self.topics["modules_capteurs"]["switch_eclairage_ouverte"]:
            self.publish(self.topics['modules_commands']['open_light'], 'OPEN THE LIGHT')
            self.log_event("Allumer la lumière manuellement (mode auto).", module="light_module", source="switch_button", action="open_light")
            self.vocal.parler("Lumière allumée.")
        elif msg.topic == self.topics["modules_capteurs"]["switch_eclairage_fermer"]:
            self.publish(self.topics['modules_commands']['close_light'], 'CLOSE THE LIGHT')
            self.log_event("Éteindre la lumière manuellement (mode auto).", module="light_module", source="switch_button", action="close_light")
            self.vocal.parler("Lumière éteinte.")
        
        #Pour mode auto, la logique est inversée avec les boutons (température haute active la ventilation et la température basse active le chauffage).
        if msg.topic == self.topics["modules_capteurs"]["bouton_chauffage"] or msg.topic == self.topics["modules_capteurs"]["bouton_chauffage_fermer"]:
            print(f"Message reçu sur {msg.topic}")
            self.publish(self.topics['modules_commands']['ventilation_on'], 'OPEN THE VENTILATION')
            self.publish(self.topics['modules_commands']['heater_off'], 'CLOSE THE HEATER')
            self.log_event("Bouton Temp. Haute -- ON ventilation, OFF chauffage", module="temperature_module", source="hot_button", action="ventilation_on & heater_off")
            self.vocal.parler("Température haute, activation de la ventilation.")

        elif msg.topic == self.topics["modules_capteurs"]["bouton_ventilation"] or msg.topic == self.topics["modules_capteurs"]["bouton_ventilation_fermer"]:
            print(f"Message reçu sur {msg.topic}")
            self.publish(self.topics['modules_commands']['heater_on'], 'OPEN THE HEATER')
            self.publish(self.topics['modules_commands']['ventilation_off'], 'CLOSE THE VENTILATION')
            self.log_event("Bouton Temp. Basse -- ON chauffage, OFF ventilation", module="temperature_module", source="cold_button", action="heater_on & ventilation_off")
            self.vocal.parler("Température basse, activation du chauffage.")

    def traiter_mode_manual(self,msg):
        if msg.topic == self.topics["modules_capteurs"]["pir_sensor"]:
            payload = msg.payload.decode()
            print(f"Message reçu sur {msg.topic}: {payload}")
        elif msg.topic == self.topics["modules_capteurs"]["switch_porte_ouverte"]:
            self.publish(self.topics['modules_commands']['open_door'], 'OPEN THE DOOR')
            self.log_event("Porte ouverte manuellement (mode manuel).", module="door_module", source="switch_button", action="open_door")
            self.door_module.porte_est_active = True
            self.vocal.parler("Porte ouverte.")
        elif msg.topic == self.topics["modules_capteurs"]["switch_porte_fermer"]:
            self.publish(self.topics['modules_commands']['close_door'], 'CLOSE THE DOOR')
            self.log_event("Porte fermée manuellement (mode manuel).", module="door_module", source="switch_button", action="close_door")
            self.door_module.porte_est_active = False
            self.vocal.parler("Porte fermée.")
        elif msg.topic == self.topics["modules_capteurs"]["switch_eclairage_ouverte"]:
            self.publish(self.topics['modules_commands']['open_light'], 'OPEN THE LIGHT')
            self.log_event("Allumer la lumière manuellement (mode manuel).", module="light_module", source="switch_button", action="open_light")
            self.vocal.parler("Lumière allumée.")
        elif msg.topic == self.topics["modules_capteurs"]["switch_eclairage_fermer"]:
            self.publish(self.topics['modules_commands']['close_light'], 'CLOSE THE LIGHT')
            self.log_event("Éteindre la lumière manuellement (mode manuel).", module="light_module", source="switch_button", action="close_light")
            self.vocal.parler("Lumière éteinte.")
        elif msg.topic == self.topics["modules_capteurs"]["bouton_chauffage"]:
            self.publish(self.topics['modules_commands']['heater_on'], 'OPEN THE HEATER')
            self.log_event("Allumer le chauffage manuellement (mode manuel).", module="temperature_module", source="heat_button", action="heater_on")
            self.vocal.parler("Chauffage allumé.")
        elif msg.topic == self.topics["modules_capteurs"]["bouton_chauffage_fermer"]:
            self.publish(self.topics['modules_commands']['heater_off'], 'CLOSE THE HEATER')
            self.log_event("Éteindre le chauffage manuellement (mode manuel).", module="temperature_module", source="heat_button", action="heater_off")
            self.vocal.parler("Chauffage éteint.")
        elif msg.topic == self.topics["modules_capteurs"]["bouton_ventilation"]:
            self.publish(self.topics['modules_commands']['ventilation_on'], 'OPEN THE VENTILATION')
            self.log_event("Allumer la ventilation manuellement (mode manuel).", module="temperature_module", source="vent_button", action="ventilation_on")
            self.vocal.parler("Ventilation allumée.")
        elif msg.topic == self.topics["modules_capteurs"]["bouton_ventilation_fermer"]:
            self.publish(self.topics['modules_commands']['ventilation_off'], 'CLOSE THE VENTILATION')
            self.log_event("Éteindre la ventilation manuellement (mode manuel).", module="temperature_module", source="vent_button", action="ventilation_off")
            self.vocal.parler("Ventilation éteinte.")
        
        # Pour le test d'alarme
        elif msg.topic == self.topics["client_commands"]["client_buzzer_on"]:
            self.publish(self.topics['modules_commands']['buzzer_on'], 'BALANCE TON SON')
            self.log_event("Activation du buzzer par commande client, test alarme (mode manuel).", module="alarm_module", source="client_remote", action="buzzer_on")
        elif msg.topic == self.topics["client_commands"]["client_buzzer_off"]:
            self.publish(self.topics['modules_commands']['buzzer_off'], 'CLOSE THE BUZZER')
            self.log_event("Désactivation du buzzer par commande client (mode manuel).", module="alarm_module", source="client_remote", action="buzzer_off")

        # Partie auto aussi accepter en manual
        elif msg.topic == self.topics["client_commands"]["client_open_door"]:
            self.publish(self.topics['modules_commands']['open_door'], 'OPEN THE DOOR')
            self.log_event("Porte ouverte par commande client (mode manuel).", module="door_module", source="client_remote", action="open_door")
            self.door_module.porte_est_active = True
        elif msg.topic == self.topics["client_commands"]["client_close_door"]:
            self.publish(self.topics['modules_commands']['close_door'], 'CLOSE THE DOOR')
            self.door_module.porte_est_active = False
            self.log_event("Porte fermée par commande client (mode manuel).", module="door_module", source="client_remote", action="close_door")
        elif msg.topic == self.topics["client_commands"]["client_open_light"]:
            self.publish(self.topics['modules_commands']['open_light'], 'OPEN THE LIGHT')
            self.log_event("Allumer la lumière par commande client (mode manuel).", module="light_module", source="client_remote", action="open_light")
        elif msg.topic == self.topics["client_commands"]["client_close_light"]:
            self.publish(self.topics['modules_commands']['close_light'], 'CLOSE THE LIGHT')
            self.log_event("Éteindre la lumière par commande client (mode manuel).", module="light_module", source="client_remote", action="close_light")
        elif msg.topic == self.topics["client_commands"]["client_heater_on"]:
            self.publish(self.topics['modules_commands']['heater_on'], 'OPEN THE HEATER')
            self.log_event("Allumer le chauffage par commande client (mode manuel).", module="temperature_module", source="client_remote", action="heater_on")
        elif msg.topic == self.topics["client_commands"]["client_heater_off"]:
            self.publish(self.topics['modules_commands']['heater_off'], 'CLOSE THE HEATER')
            self.log_event("Éteindre le chauffage par commande client (mode manuel).", module="temperature_module", source="client_remote", action="heater_off")
        elif msg.topic == self.topics["client_commands"]["client_ventilation_on"]:
            self.publish(self.topics['modules_commands']['ventilation_on'], 'OPEN THE VENTILATION')
            self.log_event("Allumer la ventilation par commande client (mode manuel).", module="temperature_module", source="client_remote", action="ventilation_on")
        elif msg.topic == self.topics["client_commands"]["client_ventilation_off"]:
            self.publish(self.topics['modules_commands']['ventilation_off'], 'CLOSE THE VENTILATION')
            self.log_event("Éteindre la ventilation par commande client (mode manuel).", module="temperature_module", source="client_remote", action="ventilation_off")

    def traiter_mode_securite(self,msg):
        
        if msg.topic == self.topics["modules_capteurs"]["pir_sensor"]:
            if not self.door_module.porte_est_active:
                self.publish(self.topics["alert"], "Intrusion détectée")
                self.log_event("Alerte en cours.", module="alarm_module", source="pir_sensor", action="buzzer_on & alarm_light")
                self.publish(self.topics['modules_commands']['buzzer_on'], 'BALANCE TON SON')
                self.publish(self.topics['modules_commands']['alarm_light'], 'ALERTE ROUGE')
                self.vocal.parler("Intrusion détectée. Alerte!")
                self.mongo_manager.envoyer_email(
                    subject="Alerte déclenchée",
                    message=f"Mouvement détecté. Alerte declenchée."
                    )
            else: 
                self.log_event("La porte est ouverte. Fermer la porte avant de déclencher l'alerte", module="alarm_module", source="pir_sensor", action="None")

        if msg.topic == self.topics["client_commands"]["alarm_stop"]:
            self.publish(self.topics['modules_commands']['buzzer_off'], 'CLOSE THE BUZZER')
            self.publish(self.topics['modules_commands']['alarm_light'], 'STOP ALARM LIGHT')
            self.log_event("Commande reçue par commande client pour désactiver le buzzer et l'alerte.", module="alarm_module", source="client_remote", action="buzzer_off & alarm_light off")
            
    def log_event(self, message: str, module=None, source=None, action=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        self.publish(self.topics["log_event"], full_message)
        print(full_message)
        
        if source == "client_remote":
            self.mongo_manager.mongo_commands(
                command=message,
                module=module,
                mode=self.state_manager.mode_actif,
                source=source,
                action=action
            )
        
        # Enregistrer dans les alertes si le mode actif est "security"
        elif self.state_manager.mode_actif == "security" and not action == "mode_change":
            self.mongo_manager.mongo_alerts(
                event_type=message,
                module=module,
                mode=self.state_manager.mode_actif,
                source=source,
                action=action
            )

        else:
            self.mongo_manager.mongo_events(
                event_type=message,
                module=module,
                mode=self.state_manager.mode_actif,
                source=source,
                action=action
            )

    def fichier_csv_exporte(self, msg):
        if msg.topic == self.topics['client_commands']['database_export']:
            print("[MQTT] Commande reçue : export CSV")
            self.mongo_manager.export_csv()  




        
            
                
            