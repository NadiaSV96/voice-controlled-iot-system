import os
import pyaudio
from vosk import Model, KaldiRecognizer
from gtts import gTTS
from pygame import mixer, time
import threading

class VoiceController:
    def __init__(self, model_path, send_command, send_mode, log=None):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.send_command = send_command
        self.send_mode = send_mode
        self.log = log
        self.listening = False
        self.stream = None
        self.audio_thread = None
        self.p = None

    def start_listening(self):
        if self.listening:
            print("Écoute déjà active.")
            return
        self.listening = True
        print("🎙️ Enregistrement démarré...")
        self.audio_thread = threading.Thread(target=self._listen)
        self.audio_thread.start()

    def stop_listening(self):
        if not self.listening:
            return
        print("🛑 Enregistrement terminé.")
        self.listening = False

        if self.stream is not None:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                print(f"Erreur lors de la fermeture du flux : {e}")
            self.stream = None

        if self.p is not None:
            try:
                self.p.terminate()
            except Exception as e:
                print(f"Erreur lors de la terminaison de PyAudio : {e}")
            self.p = None

    def _listen(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=16000,
                                  input=True,
                                  frames_per_buffer=8000)
        self.stream.start_stream()

        while self.listening:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                texte = eval(self.recognizer.Result())["text"]
                if texte:
                    print(f"🔊 Reçu : {texte}")
                    self.traiter_commande(texte)
                else:
                    print("Aucun texte détecté.")
                
                self.stop_listening()
                break

    def traiter_commande(self, texte):
        texte = texte.lower()

        def contient(*mots):
            return all(m in texte for m in mots)

        def un_de(mots):
            mots_texte = texte.split()
            return any(m in mots_texte for m in mots)

        if contient("porte", "ouvrir") or contient("porte", "ouvre"):
            self.send_command("open_door", "1")
            self.parler("Commande reçue pour ouvrir la porte.")

        elif "porte" in texte and un_de(["fermer", "ferme", "fermez"]):
            self.send_command("close_door", "0")
            self.parler("Commande reçue pour fermer la porte.")
        
        elif "lumière" in texte and un_de(["allumer", "allume", "allumez", "ouvrir", "ouvre"]):
            self.send_command("open_light", "1")
            self.parler("Commande reçue pour allumer la lumière.")

        elif "lumière" in texte and un_de(["éteindre", "éteins", "éteignez", "fermez", "fermer", "ferme"]):
            self.send_command("close_light", "0")
            self.parler("Commande reçue pour éteindre la lumière.")

        elif "chauffage" in texte and un_de(["allumer", "allume", "allumez"]):
            self.send_command("heater_on", "1")
            self.parler("Commande reçue pour allumer le chauffage.")

        elif "chauffage" in texte and un_de(["éteindre", "éteins", "éteignez", "fermer", "ferme", "fermez"]):
            self.send_command("heater_off", "0")
            self.parler("Commande reçue pour éteindre le chauffage.")

        elif "ventilation" in texte and un_de(["allumer", "allume", "allumez"]):
            self.send_command("ventilation_on", "1")
            self.parler("Commande reçue pour allumer la ventilation.")

        elif "ventilation" in texte and un_de(["éteindre", "éteins", "éteignez", "fermer", "ferme", "fermez"]):
            self.send_command("ventilation_off", "0")
            self.parler("Commande reçue pour éteindre la ventilation.")

        elif "alarme" in texte and un_de(["activer", "active", "activez"]):
            self.send_command("buzzer_on", "1")
            self.parler("Commande reçue pour activer le buzzer.")

        elif "alarme" in texte and un_de(["désactiver", "désactive", "désactivez"]):
            self.send_command("buzzer_off", "0")
            self.parler("Commande reçue pour désactiver le buzzer.")

        elif "alerte" in texte and un_de(["désactiver", "désactive", "désactivez", "arrêter", "arrêtez", "arrête", "arrêté"]):
            self.send_command("alarm_stop", "0")
            self.parler("Commande reçue pour arrêter l'alerte.")

        elif "mode" in texte and "manuel" in texte:
            self.send_mode("manual")
            self.parler("Mode manuel activé")

        elif "mode" in texte and "auto" in texte:
            self.send_mode("auto")
            self.parler("Mode auto activé")

        elif "mode" in texte and un_de(["sécurité", "sécurite", "security"]):
            self.send_mode("security")
            self.parler("Mode sécurité activé")

        else:
            self.parler("Commande non reconnue")

    def parler(self, message):
        if self.log:
            self.log(f"[Synthèse vocale REMOTE CLIENT] {message}")

        # Créer le fichier MP3 dans le dossier Téléchargements temporairement
        try:
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            temp_path = os.path.join(downloads_dir, "tts_temp.mp3")

            
            tts = gTTS(text=message, lang='fr', slow=False, tld='fr')
            tts.save(temp_path)

            mixer.init(frequency=22050, size=-16, channels=1, buffer=4096)
            mixer.music.load(temp_path)
            mixer.music.play()

            while mixer.music.get_busy():
                time.Clock().tick(10)

            mixer.music.unload()
            mixer.quit()

            if os.path.exists(temp_path):
                os.remove(temp_path)
         
        except Exception as e:
            print(f"Erreur pendant la synthèse vocale : {e}")           
            