import paho.mqtt.client as mqtt
import yaml

class RemoteClient:
    def __init__(self, config_file="config/remote_client_config.yaml"):
        self.config = self.load_config(config_file)  # Charger la configuration depuis YAML
        self.mqtt_client = mqtt.Client()  # Créer un client MQTT
        self.broker = self.config['mqtt']['broker']  # Récupérer le broker depuis le fichier config
        self.port = self.config['mqtt']['port']      # Récupérer le port depuis le fichier config
        self.status_callback = None
        self.log_callback = None
        self._setup_mqtt()

    def load_config(self, config_file):
        """ Charger la configuration depuis un fichier YAML """
        with open(config_file, "r") as file:
            return yaml.safe_load(file)

    def on_connect(self, client, userdata, flags, rc):
        """ Callback appelé lors de la connexion au broker """
        print(f"[REMOTE CLIENT] Connecté au broker {self.broker}:{self.port} avec le code de résultat {rc}")

    def _setup_mqtt(self):
        """ Configure les abonnements MQTT pour écouter le statut du mode """
        # Connexion au broker
        self.mqtt_client.on_connect = self.on_connect  # Définir la fonction de callback on_connect
        self.mqtt_client.connect(self.broker, self.port, 60)

        # S'abonner au topic de statut du mode
        self.mqtt_client.subscribe(self.config['mqtt']['topics']['client_status'])
        
        # S'abonner au topic d'alerte
        self.mqtt_client.subscribe(self.config['mqtt']['topics']['alert'])

        # S'abonner au topic des logs
        self.mqtt_client.subscribe(self.config['mqtt']['topics']['log_event'])

        # Abonnement aux modules individuels
        for topic in self.config['mqtt']['topics']['modules_status'].values():
            self.mqtt_client.subscribe(topic)
            print(f"[REMOTE CLIENT] Abonnement au topic: {topic}")
            self.mqtt_client.on_message = self.on_message  # Callback pour traiter les messages entrants

            # Démarrer la boucle MQTT en arrière-plan
            self.mqtt_client.loop_start()

    def on_message(self, client, userdata, msg):
        """ Gérer les messages reçus, par exemple l'état actuel du mode """
        decoded_msg = msg.payload.decode()
        if msg.topic == self.config['mqtt']['topics']['client_status']:
            print(f"\nMode actuel: {decoded_msg}")
            if self.status_callback:
                self.status_callback(decoded_msg)

        modules_status_config = self.config['mqtt']['topics']['modules_status']
        excluded_keys = ['bouton_chauffage', 'bouton_ventilation']
        excluded_topics = [modules_status_config[k] for k in excluded_keys]

        if msg.topic in modules_status_config.values():
            if msg.topic in excluded_topics:
                print(f"Message reçu sur {msg.topic}") 
            else:
                print(f"Message reçu sur {msg.topic}: {decoded_msg}")

        if msg.topic in self.config['mqtt']['topics']['alert'] :
            print(f"Message reçu sur {msg.topic}: {decoded_msg}")
        
        if msg.topic in self.config['mqtt']['topics']['log_event'] :
            print(f"Message reçu sur {msg.topic}: {decoded_msg}")

        if self.log_callback:
            self.log_callback(f"[{msg.topic}] {msg.payload.decode()}")

    def send_command(self, topic, payload):
        """ Envoie une commande au nœud central """
        self.mqtt_client.publish(topic, payload)
        print(f"Commande envoyée: {topic} avec payload: {payload}")

    def start(self):
        """ Interface utilisateur avec menu numéroté pour envoyer des commandes """
        print("Bienvenue dans l'interface client.\n")

        # Modes disponibles
        mode_commands = ["auto", "manual", "security"]

        # Commandes vers les modules avec leur clé de topic YAML
        module_commands = {
            1: ("Ouvrir porte", "open_door"),
            2: ("Fermer porte", "close_door"),
            3: ("Allumer lumière", "open_light"),
            4: ("Éteindre lumière", "close_light"),
            5: ("Allumer chauffage", "heater_on"),
            6: ("Éteindre chauffage", "heater_off"),
            7: ("Allumer ventilation", "ventilation_on"),
            8: ("Éteindre ventilation", "ventilation_off"),
            9: ("Activer buzzer", "buzzer_on"),
            10: ("Désactiver buzzer", "buzzer_off"),
            11: ("Désactiver l'alarme", "alarm_stop")
        }

        # Payloads associés aux commandes (0 = off / 1 = on)
        payloads = {
            "open_door": "1",
            "close_door": "0",
            "open_light": "1",
            "close_light": "0",
            "heater_on": "1",
            "heater_off": "0",
            "ventilation_on": "1",
            "ventilation_off": "0",
            "buzzer_on": "1",
            "buzzer_off": "0",
            "alarm_stop": "0"
        }

        try:
            while True:
                # Affichage du menu
                print("\n=== MENU PRINCIPAL ===")
                print("Modes disponibles :")
                for m in mode_commands:
                    print(f" - {m}")
                print("\nCommandes modules :")
                for num, (label, _) in module_commands.items():
                    print(f"{num}: {label}")
                print("0: Quitter")

                # Saisie utilisateur
                choix = input("\nEntrez un mode (auto/manual/security) ou un numéro de commande : ").strip()

                if choix == "0" or choix.lower() == "exit":
                    break
                elif choix in mode_commands:
                    # Envoi du changement de mode
                    self.send_command(self.config['mqtt']['topics']['client_change_mode'], choix)
                elif choix.isdigit() and int(choix) in module_commands:
                    # Envoi de commande module
                    label, key = module_commands[int(choix)]
                    topic = self.config['mqtt']['topics'][key]
                    payload = payloads.get(key, "")
                    if payload != "":
                        self.send_command(topic, payload)
                    else:
                        print("Erreur : payload manquant pour la commande.")
                else:
                    print("Entrée non reconnue. Veuillez réessayer.")

        except KeyboardInterrupt:
            print("\nArrêt du client...")

        finally:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            print("[REMOTE CLIENT] Déconnecté proprement")

# à décommenter au besoin si on veut l'interface client au terminal
###########
#remote_client = RemoteClient(config_file="config/remote_client_config.yaml")  # Charger config spécifique
#remote_client.start()  # Lancer l'interface utilisateur
