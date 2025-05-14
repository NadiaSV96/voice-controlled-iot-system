import paho.mqtt.client as mqtt
import yaml
from porte import Porte
from eclairage import Eclairage
from temperature import Temperature
from alarme import Alarme
import time 
from gpio_manager import GpioManager
from pir_sensor import PirSensor

class MaisonClient:
    def __init__(self, config_file="config/smart_home_config.yaml"): 
        self.config = self.load_config(config_file)  # Charger la configuration depuis YAML
        self.mqtt_client = mqtt.Client()  # Créer un client MQTT
        self.broker = self.config['mqtt']['broker']  # Récupérer le broker depuis le fichier config
        self.port = self.config['mqtt']['port']      # Récupérer le port depuis le fichier config
        self.topics_subscribe = self.config['mqtt']['topics']['modules_commands']
        self.topics_publish = self.config['mqtt']['topics']['modules_capteurs']
        self.topics_status = self.config['mqtt']['topics']['modules_status']
        self._setup_mqtt()
        self.gpiomanager = GpioManager()
        self.porte = Porte(self.gpiomanager)
        self.eclairage = Eclairage(self.gpiomanager)
        self.temperature = Temperature(self.gpiomanager)
        self.alarme = Alarme(self.gpiomanager)
        self.pir_sensor = PirSensor(self.gpiomanager)
        self.etat_precedent_porte = False
        self.etat_precedent_eclairage = False
        self.chauffage_allume = False
        self.etat_precedent_bouton_chauffage = False
        self.ventilation_allumee = False
        self.etat_precedent_bouton_ventilation = False
        self.etat_precedent_pir_sensor = False

    def load_config(self, config_file):
        """ Charger la configuration depuis un fichier YAML """
        with open(config_file, "r") as file:
            return yaml.safe_load(file)

    def on_connect(self, client, userdata, flags, rc):
        """ Callback appelé lors de la connexion au broker """
        print(f"[MAISON CLIENT] Connecté au broker {self.broker}:{self.port} avec le code de résultat {rc}")

        for command_topic in self.topics_subscribe.values():
            self.mqtt_client.subscribe(command_topic)
            print(f"[MAISON CLIENT] Abonnement au topic: {command_topic}")

    def _setup_mqtt(self):
        """ Configure les abonnements MQTT pour écouter le statut du mode """
        # Connexion au broker
        self.mqtt_client.on_connect = self.on_connect  # Définir la fonction de callback on_connect
        self.mqtt_client.connect(self.broker, self.port, 60)

        self.mqtt_client.on_message = self.on_message  
        # Démarrer la boucle MQTT en arrière-plan
        self.mqtt_client.loop_start()

    def subscribe(self, topic):
        """ S'abonner à un topic MQTT spécifique """
        self.mqtt_client.subscribe(topic)

    def publish(self, topic, payload):
        """ Publier un message MQTT sur un topic spécifique """
        self.mqtt_client.publish(topic, payload)

    def traiter_etat_capteur(self):
        if self.pir_sensor.mouvement_detecte() and self.etat_precedent_pir_sensor == False:
            self.publish(self.topics_publish['pir_sensor'], 'MOTION DETECTED')
            print(f"[MAISON CLIENT] Message envoyé sur {self.topics_publish['pir_sensor']}")
            self.etat_precedent_pir_sensor = True

        elif not self.pir_sensor.mouvement_detecte() and self.etat_precedent_pir_sensor == True:
            self.etat_precedent_pir_sensor = False

        if self.porte.switch_porte_est_active() and self.etat_precedent_porte == False:
            self.publish(self.topics_publish['switch_porte_ouverte'], 'OPEN THE DOOR')
            print(f"[MAISON CLIENT] Message envoyé sur {self.topics_publish['switch_porte_ouverte']}")
            self.etat_precedent_porte = True
        elif not self.porte.switch_porte_est_active() and self.etat_precedent_porte == True:
            self.publish(self.topics_publish['switch_porte_fermer'], 'CLOSE THE DOOR')
            print(f"[MAISON CLIENT] Message envoyé sur {self.topics_publish['switch_porte_fermer']}")
            self.etat_precedent_porte = False
        
        if self.eclairage.switch_lumiere_est_active() and self.etat_precedent_eclairage == False:
            self.publish(self.topics_publish['switch_eclairage_ouverte'], 'OPEN THE LIGHT')
            print(f"[MAISON CLIENT] Message envoyé sur {self.topics_publish['switch_eclairage_ouverte']}")
            self. etat_precedent_eclairage = True
        elif not self.eclairage.switch_lumiere_est_active() and self.etat_precedent_eclairage == True:
            self.publish(self.topics_publish['switch_eclairage_fermer'], 'CLOSE THE LIGHT')
            print(f"[MAISON CLIENT] Message envoyé sur {self.topics_publish['switch_eclairage_fermer']}")
            self.etat_precedent_eclairage = False
        
    
        etat_actuel_bouton_chauffage = self.temperature.bouton_chauffage_est_active()

        if etat_actuel_bouton_chauffage and not self.etat_precedent_bouton_chauffage:
                if not self.chauffage_allume:
                    time.sleep(0.05)
                    self.temperature.active_chauffage()
                    self.publish(self.topics_publish['bouton_chauffage'], 'OPEN THE HEATER')
                    print("[CHAUFFAGE] Chauffage allumé")
                    self.chauffage_allume = True
                else:
                    time.sleep(0.05)
                    self.temperature.desactive_chauffage()
                    self.publish(self.topics_publish['bouton_chauffage_fermer'], 'CLOSE THE HEATER')
                    print("[CHAUFFAGE] Chauffage éteint")
                    self.chauffage_allume = False
        self.etat_precedent_bouton_chauffage = etat_actuel_bouton_chauffage

        
        etat_actuel_bouton_ventilation = self.temperature.bouton_ventilation_est_active()

        if etat_actuel_bouton_ventilation and not self.etat_precedent_bouton_ventilation:
            if not self.ventilation_allumee:
                time.sleep(0.05)
                self.temperature.active_ventilation()
                self.publish(self.topics_publish['bouton_ventilation'], 'OPEN THE VENTILATION')
                print("[VENTILATION] Ventilation allumée")
                self.ventilation_allumee = True
            else:
                time.sleep(0.05)
                self.temperature.desactive_ventilation()
                self.publish(self.topics_publish['bouton_ventilation_fermer'], 'CLOSE THE VENTILATION')
                print("[VENTILATION] Ventilation éteinte")
                self.ventilation_allumee = False

        self.etat_precedent_bouton_ventilation = etat_actuel_bouton_ventilation


    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()
        print(f"[MAISON CLIENT] Message reçu sur {topic}: {payload}")
        self.traiter_message_recu(topic, payload)

    def traiter_message_recu(self, topic, payload):
        if topic == self.topics_subscribe['open_door']:
            self.porte.ouvrir_porte()
            self.publish(self.topics_status["door"], "open")
            print('Porte ouverte')
        elif topic == self.topics_subscribe['close_door']:
            self.porte.ferme_porte()
            self.publish(self.topics_status["door"], "closed")
            print('Porte fermée')
        elif topic == self.topics_subscribe['open_light']:
            self.eclairage.ouvrir_eclairage()
            self.publish(self.topics_status["lighting"], "on")
            print('Lumière ouverte')
        elif topic == self.topics_subscribe['close_light']:
            self.eclairage.ferme_eclairage()
            self.publish(self.topics_status["lighting"], "off")
            print('Lumière éteinte')
        elif topic == self.topics_subscribe['heater_on']:
            self.temperature.active_chauffage()
            self.publish(self.topics_status["heater"], "on")
            print('Chauffage Allumé')
        elif topic == self.topics_subscribe['heater_off']:
            self.temperature.desactive_chauffage()
            self.publish(self.topics_status["heater"], "off")
            print('Chauffage éteint')
        elif topic == self.topics_subscribe['ventilation_on']:
            self.temperature.active_ventilation()
            self.publish(self.topics_status["ventilation"], "on")
            print('Ventilation allumée')
        elif topic == self.topics_subscribe['ventilation_off']:
            self.temperature.desactive_ventilation()
            self.publish(self.topics_status["ventilation"], "off")
            print('Ventilation éteinte')
        elif topic == self.topics_subscribe['buzzer_on']:
            self.alarme.active_buzzer()
            self.publish(self.topics_status["buzzer"], "on")
            print('Buzzer on')
        elif topic == self.topics_subscribe['buzzer_off']:
            self.alarme.desactive_buzzer()
            self.publish(self.topics_status["buzzer"], "off")
            print('Buzzer off')
        elif topic == self.topics_subscribe['alarm_light']:
            if payload == "ALERTE ROUGE":
                self.alarme.active_clignotement()
                self.publish(self.topics_status["alarm_light"], "on")
                print("Clignotement lumineux activé")
            if payload == "STOP ALARM LIGHT":
                self.alarme.desactive_clignotement()
                self.publish(self.topics_status["alarm_light"], "off")
                print("Clignotement lumineux désactivé")
        else:
            print("[MAISON CLIENT] Topic non reconnu.")

    def start(self):
        try:
            print("[MAISON CLIENT] En attente de messages... (Ctrl+C pour quitter)")
            while True:
                self.traiter_etat_capteur()

        except KeyboardInterrupt:
            print("\nArrêt du client...")

        finally:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            print("[MAISON CLIENT] Déconnecté proprement")
            self.gpiomanager.nettoyer()

if __name__ == "__main__":
    client = MaisonClient()
    client.start()
