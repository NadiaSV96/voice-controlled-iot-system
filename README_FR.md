
# 🎙️ Système Embarqué Intelligent avec Reconnaissance Vocale

> Version finale de notre projet de maison intelligente, réalisée dans le cadre de l'AEC en Internet des Objets et Intelligence Artificielle au Collège Ahuntsic (Printemps 2025).  
> Construit sur la base du [Projet 1 : Système Embarqué Distribué de Supervision Domotique].

## 🧠 Résumé du Projet

Ce projet représente la **deuxième phase** du système domotique distribué amorcé au Projet 1. Il améliore le système embarqué en ajoutant la **reconnaissance vocale et la synthèse vocale**, pour enrichir l’interaction utilisateur, la modularité et les fonctionnalités de supervision.

Le système repose sur une **architecture modulaire** avec communication MQTT, comprenant un nœud central, des modules physiques intelligents (capteurs et actionneurs) et une interface graphique distante.

## ⚙️ Résumé des Points d'Entrée

Le système comprend trois points d’exécution distincts :

- Le **nœud central** gère la logique de décision, la communication MQTT et la journalisation vers la base de données.
- Le **client distant** fournit une interface graphique (GUI) pour la surveillance, le contrôle vocal et les commandes manuelles.
- Le **module de maison intelligente** (côté physique) interagit avec les composants matériels et exécute les actions reçues via MQTT.

Chaque composant fonctionne de manière indépendante, mais communique en temps réel via MQTT.

## 🏠 Composants Physiques Contrôlés

Le module de maison intelligente contrôle :

- **Actionneur de porte** : ouverture/fermeture via bouton ou commande vocale
- **Système d’éclairage** : allumage/extinction déclenché par présence ou commande
- **Simulation de chauffage et ventilation** : réagit à la température simulée (boutons ou voix)
- **Système de sécurité** : détection de mouvement déclenchant un buzzer et une alerte

Toutes les interactions GPIO sont prises en charge via Raspberry Pi à l’aide des bibliothèques `gpiozero` et `RPi.GPIO`.

## 🔧 Composants du Système

### 1. 🧠 Nœud Central (point d’entrée : `main.py`)
- Logique de décision et gestion des modes (manuel, automatique, sécurité)
- Routage des messages MQTT et journalisation dans MongoDB

### 2. 🏠 Module Maison Intelligente (point d’entrée : `mqtt_maison_client.py`)
- Gère les composants GPIO : LEDs, capteurs PIR, buzzers, boutons
- Réagit aux commandes MQTT envoyées par le nœud central

### 3. 🖥️ Client Distant (point d’entrée : `interface.py`)
- Interface Tkinter avec commandes vocales
- Affiche l’état du système en temps réel, permet le changement de mode et l’envoi de commandes
- Bouton pour exporter les logs en CSV

## 🗣️ Fonctionnalités Clés

- **Reconnaissance vocale** avec VOSK (hors ligne, local)
- **Synthèse vocale** avec gTTS et `pygame.mixer`
- **Interface graphique en temps réel** : état du système, historique des événements, heure
- **Alertes par courriel** en cas d’intrusion (SMTP)
- **Journalisation structurée** dans MongoDB (`events`, `alerts`, `commands`)
- **Export CSV** des 10 derniers événements
- **Configuration via YAML** : topics MQTT, GPIO, clés API, emails, etc.

## 🔐 Modes de Fonctionnement

| Mode      | Description                                 |
|-----------|---------------------------------------------|
| Auto      | Réagit automatiquement aux capteurs         |
| Manuel    | Majoritairement commandé par l’utilisateur  |
| Sécurité  | Détections = alerte + buzzer                |

## 📡 Technologies Utilisées

- Python 3.11+
- Protocole MQTT (`paho-mqtt`)
- MongoDB
- GPIO sur Raspberry Pi (`gpiozero`, `RPi.GPIO`)
- Tkinter, Pygame
- VOSK, gTTS
- Fichiers de configuration YAML

## 🧱 Architecture du Projet

```
voice-controlled-iot-system/
├── central_node/
│   ├── coordinator.py
│   ├── mqtt_handler.py
│   ├── event_logger.py
│   ├── state_manager.py
│   └── voice_controller_maison.py
│
├── client/
│   ├── interface.py
│   ├── remote_client.py
│   └── voice_controller.py
│
├── modules/
│   ├── door_module.py
│   ├── light_module.py
│   ├── alarm_module.py
│   ├── heating_module.py
│   └── pir_module.py
│
├── sensors_actuators/
│   ├── gpio_manager.py
│   ├── mqtt_maison_client.py
│   ├── porte.py
│   ├── eclairage.py
│   ├── temperature.py
│   ├── alarme.py
│   └── pir_sensor.py
│
├── config/
│   ├── central_config.yaml
│   ├── smart_home_config.yaml
│   └── remote_client_config.yaml
│
├── vosk-model-small-fr-0.22/
├── export_combined.csv
├── Photo du circuit.jpg
├── main.py
├── README_FR.md
└── README_EN.md
```

## 📦 Dépendances

Le projet nécessite les bibliothèques Python suivantes :

- `paho-mqtt` — Communication MQTT
- `gpiozero`, `RPi.GPIO` — Contrôle GPIO pour Raspberry Pi
- `gTTS` — Synthèse vocale
- `vosk` — Reconnaissance vocale hors ligne
- `PyAudio` — Entrée audio via microphone
- `pygame` — Lecture audio
- `pymongo` — Interaction avec MongoDB
- `PyYAML` — Lecture de fichiers YAML
- `pandas` — Export et manipulation de données
- `requests` — Appels HTTP (ex. météo)
- `playsound` — Lecture audio alternative
- `tkinter` — Interface graphique

### 💻 Installation :

```bash
pip install paho-mqtt gpiozero RPi.GPIO gTTS vosk PyAudio pygame pymongo PyYAML pandas requests playsound
```

## 📬 Contact

Projet réalisé par :
- **Nadia Simard Villa** – AEC Internet des Objets et IA  
- **Sophie Mercier** – AEC Internet des Objets et IA  
- Sous la supervision de **Khalil Loghlam**, enseignant, *ing.* en génie électrique et logiciel
