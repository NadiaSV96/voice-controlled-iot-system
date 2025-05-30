
# 🎙️ Smart Embedded IoT System with Voice Recognition

> Final version of our smart home system project, completed as part of an AEC in IoT and AI at Collège Ahuntsic (Spring 2025).  
> Built on the foundation of [Project 1: Distributed Embedded IoT Supervision System].

## 🧠 Project Summary

This project is the **second phase** of a distributed smart home system initiated in Project 1. It improves the embedded system by introducing **voice recognition and speech synthesis**, enhancing user interaction, and improving modularity and supervision features.

The system is based on a **modular architecture** with MQTT communication and includes a central controller, smart physical modules (with sensors and actuators), and a remote graphical client interface.

## ⚙️ System Entry Points Summary

This system includes three distinct execution points:

- The **central node** coordinates decision logic, MQTT routing, and database logging.
- The **remote client** provides a GUI for monitoring, voice control, and manual overrides.
- The **smart home node** (physical side) interfaces with hardware components and executes actions based on MQTT commands.

Each component runs independently but communicates via MQTT for real-time coordination.

## 🏠 Smart Home Components Controlled

The physical smart home module manages:

- **Door actuator**: open/close via button or voice command
- **Lighting system**: on/off control triggered by presence or commands
- **Heating & ventilation simulation**: reacts to simulated temperature inputs (buttons or voice)
- **Security system**: motion detection triggering buzzer and alerts

All GPIO interactions are handled through the Raspberry Pi using Python libraries like `gpiozero` and `RPi.GPIO`.

## 🔧 System Components

### 1. 🧠 Central Node (entry point: `main.py`)
- Decision-making logic and mode switching (manual, auto, security)
- Handles MQTT message routing and event logging to MongoDB

### 2. 🏠 Smart Home Module (entry point: `mqtt_maison_client.py`)
- Manages GPIO components: LEDs, PIR sensors, buzzers, buttons
- Reacts to MQTT commands (published by the central node)

### 3. 🖥️ Remote Client (entry point: `interface.py`)
- Tkinter-based interface with voice control
- Displays real-time system status, allows mode switching and command sending
- Provides button to export logs to CSV

## 🗣️ Key Features

- **Voice command recognition** with VOSK (offline, local)
- **Speech synthesis** via gTTS and `pygame.mixer`
- **Real-time GUI** with state display, event history, and time
- **Email alerts** using SMTP when intrusions are detected
- **Structured event logging** to MongoDB (`events`, `alerts`, `commands`)
- **CSV export** of last 10 system events
- **Configuration via YAML**: topics, GPIOs, API keys, email credentials, etc.

## 🔐 Operating Modes

| Mode     | Description                                    |
|----------|------------------------------------------------|
| Auto     | Reacts to sensors automatically               |
| Manual   | Mostly user commands are executed             |
| Security | Intrusions trigger alert & buzzer             |

## 📡 Technologies Used

- Python 3.11+
- MQTT protocol (`paho-mqtt`)
- MongoDB
- GPIO on Raspberry Pi (`gpiozero`, `RPi.GPIO`)
- Tkinter, Pygame
- VOSK, gTTS
- YAML configuration

## 🧱 Project Architecture

```
voice-controlled-iot-system/
├── central_node/                    # Central node: coordination and system logic
│   ├── coordinator.py
│   ├── mqtt_handler.py
│   ├── event_logger.py
│   ├── state_manager.py
│   └── voice_controller_maison.py   # VOSK-based voice control for home node
│
├── client/                          # Remote user interface
│   ├── interface.py                 # Entry point for remote client
│   ├── remote_client.py
│   └── voice_controller.py          # VOSK + gTTS logic for voice commands/synthesis
│
├── modules/                         # Logic of physical modules (door, light, etc.)
│   ├── door_module.py
│   ├── light_module.py
│   ├── alarm_module.py
│   ├── heating_module.py
│   └── pir_module.py
│
├── sensors_actuators/              # GPIO hardware interaction
│   ├── gpio_manager.py
│   ├── mqtt_maison_client.py       # Entry point for smart home module
│   ├── porte.py
│   ├── eclairage.py
│   ├── temperature.py
│   ├── alarme.py
│   └── pir_sensor.py
│
├── config/                          # YAML configuration files
│   ├── central_config.yaml
│   ├── smart_home_config.yaml
│   └── remote_client_config.yaml
│
├── vosk-model-small-fr-0.22/        # VOSK French model (offline speech recognition)
├── export_combined.csv              # Exported log data
├── Photo du circuit.jpg             # Photo of hardware setup
├── main.py                          # Entry point for launching the central node
├── README_FR.md
└── README_EN.md
```

## 📦 Dependencies

The project requires the following Python packages:

- `paho-mqtt` — MQTT communication
- `gpiozero`, `RPi.GPIO` — Raspberry Pi GPIO control
- `gTTS` — Text-to-speech synthesis
- `vosk` — Offline voice recognition
- `PyAudio` — Audio input from microphone
- `pygame` — Audio playback
- `pymongo` — MongoDB interaction
- `PyYAML` — YAML configuration
- `pandas` — Data export and manipulation
- `requests` — HTTP API requests (e.g. weather)
- `playsound` — Optional legacy audio playback (if not using `pygame`)
- `tkinter` — GUI framework

### 💻 Install everything with:

```bash
pip install paho-mqtt gpiozero RPi.GPIO gTTS vosk PyAudio pygame pymongo PyYAML pandas requests playsound
```

## 📬 Contact

Project created by:
- **Nadia Simard Villa** – AEC in IoT & AI  
- **Sophie Mercier** – AEC in IoT & AI  
Under the supervision of **Khalil Loghlam**, teacher, *Eng.* in Electrical and Software Engineering
