import tkinter as tk
from tkinter import ttk
from datetime import datetime
from remote_client import RemoteClient
from voice_controller import VoiceController

class RemoteClientGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Client Distant Domotique IoT")
        self.master.protocol("WM_DELETE_WINDOW", self.quit)
        self.client = RemoteClient(config_file="config/remote_client_config.yaml")
        self.voice_controller = VoiceController(
            model_path="vosk-model-small-fr-0.22",
            send_command=self.send_command_key_only,
            send_mode=self.send_mode,
            log=self.afficher_message_log
        )

        # Variable pour affichage dynamique du mode
        self.mode_var = tk.StringVar()
        self.mode_var.set("Mode actuel : manual")

        # Variable pour affichage dynamique de l'heure
        self.heure_var = tk.StringVar()
        self.heure_var.set("")  

        self.update_time()

        # Attribuer le callback pour mise à jour du label
        self.client.status_callback = self.update_mode_label
        # Attribuer le callback pour affichage des messages de log
        self.client.log_callback = self.afficher_message_log

        self._create_widgets()

    def _create_widgets(self):
        # Label du mode actuel
        mode_label = ttk.Label(self.master, textvariable=self.mode_var, font=("Arial", 14, "bold"))
        mode_label.pack(pady=10)

        # Affichage de l'heure actuelle
        heure_label = ttk.Label(self.master, textvariable=self.heure_var, font=("Arial", 12))
        heure_label.pack(pady=(0, 5))

        # Frame pour les modes
        mode_frame = ttk.LabelFrame(self.master, text="Changer de mode")
        mode_frame.pack(padx=10, pady=5, fill="x")

        modes = ["auto", "manual", "security"]
        for mode in modes:
            button = ttk.Button(mode_frame, text=mode.capitalize(),
                                command=lambda m=mode: self.send_mode(m))
            button.pack(side="left", padx=5, pady=5)

        # Frame pour les modules
        module_frame = ttk.LabelFrame(self.master, text="Contrôle des modules")
        module_frame.pack(padx=10, pady=10, fill="x")

        self.module_commands = {
            "Ouvrir porte": "open_door",
            "Fermer porte": "close_door",
            "Allumer lumière": "open_light",
            "Éteindre lumière": "close_light",
            "Allumer chauffage": "heater_on",
            "Éteindre chauffage": "heater_off",
            "Allumer ventilation": "ventilation_on",
            "Éteindre ventilation": "ventilation_off",
            "Activer alarme": "buzzer_on",
            "Désactiver alarme": "buzzer_off"
        }

        self.payloads = {
            "open_door": "1",
            "close_door": "0",
            "open_light": "1",
            "close_light": "0",
            "heater_on": "1",
            "heater_off": "0",
            "ventilation_on": "1",
            "ventilation_off": "0",
            "buzzer_on": "1",
            "buzzer_off": "0"
        }

        for label, key in self.module_commands.items():
            topic = self.client.config['mqtt']['topics'][key]
            payload = self.payloads.get(key, "")
            btn = ttk.Button(module_frame, text=label,
                             command=lambda t=topic, p=payload: self.send_command(t, p))
            btn.pack(fill="x", padx=5, pady=2)
        
        # Ajout du bouton pour désactiver l'alarme avec contour rouge
        alarm_stop_button = tk.Button(module_frame, text="Désactiver l'alerte en cours",
                                       command=self.send_alarm_stop_command,
                                       fg="white", bg="red", activebackground="darkred",
                              highlightthickness=2, highlightbackground="red", relief="raised")
        alarm_stop_button.pack(fill="x", padx=5, pady=2)

        vocal_btn = ttk.Button(self.master, text="🎙️ Maintenir pour parler")
        vocal_btn.bind("<ButtonPress>", lambda e: self.voice_controller.start_listening())
        vocal_btn.bind("<ButtonRelease>", lambda e: self.voice_controller.stop_listening())
        vocal_btn.pack(pady=5)

        # Frame pour l'exportation de la base de données
        export_frame = ttk.LabelFrame(self.master, text="Exportation des 10 derniers événements de la base de données")
        export_frame.pack(padx=10, pady=10, fill="x")

        export_button = ttk.Button(export_frame, text="Exporter",
                                   command=self.send_export_command)
        export_button.pack(padx=5, pady=5)

        # Frame pour afficher les messages de log
        log_frame = ttk.LabelFrame(self.master, text="Messages système (alertes, statuts)")
        log_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.log_text = tk.Text(log_frame, height=10, wrap="word", state="disabled")
        self.log_text.pack(side="left", fill="both", expand=True)

        log_scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scrollbar.pack(side="right", fill="y")

        self.log_text.config(yscrollcommand=log_scrollbar.set)

        # Bouton pour quitter
        quit_btn = ttk.Button(self.master, text="Quitter l'application", command=self.quit)
        quit_btn.pack(pady=10)

    def afficher_message_log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")  # Faire défiler automatiquement
        self.log_text.config(state="disabled")

    def send_alarm_stop_command(self):
            topic = self.client.config['mqtt']['topics']['alarm_stop']
            self.client.send_command(topic, "0")

    def send_mode(self, mode):
        topic = self.client.config['mqtt']['topics']['client_change_mode']
        self.client.send_command(topic, mode)

    def send_command(self, topic, payload):
        self.client.send_command(topic, payload)

    def send_command_key_only(self, key, payload):
        topic = self.client.config['mqtt']['topics'][key]
        self.send_command(topic, payload)

    def send_export_command(self):
        topic = self.client.config['mqtt']['topics']['database_export']
        self.client.send_command(topic, "export")

    def update_mode_label(self, mode):
        self.mode_var.set(f"Mode actuel : {mode}")

    def update_time(self):
        heure_actuelle = datetime.now().strftime("%H:%M:%S")
        self.heure_var.set(f"Heure actuelle : {heure_actuelle}")
        self.master.after(1000, self.update_time)

    def quit(self):
        self.client.mqtt_client.loop_stop()
        self.client.mqtt_client.disconnect()
        print("[REMOTE CLIENT] Déconnecté proprement")
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = RemoteClientGUI(root)
    root.mainloop()
