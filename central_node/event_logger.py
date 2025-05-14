import pymongo
import yaml
from datetime import datetime
from pandas import DataFrame, to_datetime
import smtplib
from email.mime.text import MIMEText


class MongoDBManager:
    def __init__(self, config_path="config/central_config.yaml"):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        mongo_conf = config["mongodb"]
        self.client = pymongo.MongoClient(mongo_conf["uri"])
        self.db = self.client[mongo_conf["database"]]

        self.events_col = self.db[mongo_conf["collections"]["events"]]
        self.alerts_col = self.db[mongo_conf["collections"]["alerts"]]
        self.commands_col = self.db[mongo_conf["collections"]["commands"]]
        self.export_limit = mongo_conf['export_limit']

    def mongo_events(self, event_type, module=None, mode=None, source=None, action=None):
        """Insère un événement dans la collection events"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "module": module,
            "mode": mode,
            "source": source,
            "action": action
        }

        self.events_col.insert_one(entry)
        print("[MongoDB] Événement enregistré :", entry)

    def mongo_alerts(self, event_type, module=None, mode=None, source=None, action=None):
        """Insère une alerte système"""
        entry = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "module": module,
        "mode": mode,
        "source": source,
        "action": action
        }
        self.alerts_col.insert_one(entry)
        print("[MongoDB] Alerte enregistrée :", entry)

    def mongo_commands(self, command, module=None, mode=None, source=None, action=None):
        """Insère une commande reçue"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "module": module,
            "mode": mode,
            "source": source,
            "action": action
        }
        self.commands_col.insert_one(entry)
        print("[MongoDB] Commande enregistrée :", entry)

    def export_csv(self, filepath="export_combined.csv", limit=None):
        if limit is None:
            limit = self.export_limit
        

        # Recuperer les documents
        events = list(self.events_col.find())
        alerts = list(self.alerts_col.find())
        commands = list(self.commands_col.find())

        # Ajouter un champ pour identifier la collection d'origine
        for doc in events:
            doc["collection"] = "events"
        for doc in alerts:
            doc["collection"] = "alerts"
        for doc in commands:
            doc["collection"] = "commands"

        # Supprimer les _id
        for doc in events + alerts + commands:
            doc.pop("_id", None)

        # Fusionner et convertir en DataFrame
        all_docs = events + alerts + commands
        df = DataFrame(all_docs)

        # Convertir les timestamps et trier
        df["timestamp"] = to_datetime(df["timestamp"])
        df = df.sort_values("timestamp", ascending=False).head(limit)

        # Exporter
        df.to_csv(filepath, index=False, encoding="utf-8")
        print(f"[MongoDB] Export combiné terminé ({limit} dernières entrées) -> {filepath}")

    def envoyer_email(self, subject, message, config_path="config/central_config.yaml"):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            email_conf = config['smtp']

        try:
            # Construire le message avec encodage UTF-8
            msg = MIMEText(message, _charset="utf-8")
            msg['Subject'] = subject
            msg['From'] = email_conf['sender']
            msg['To'] = email_conf['recipient']

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
                connection.login(user=email_conf['sender'], password=email_conf['app_password'])
                connection.sendmail(
                    from_addr=email_conf['sender'],
                    to_addrs=[email_conf['recipient']],  
                    msg=msg.as_string()                   
                )
                print("[Email] Message envoyé avec succès.")
        except Exception as e:
            print(f"[Email] Erreur lors de l'envoi : {e}")
