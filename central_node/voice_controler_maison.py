from gtts import gTTS
from pygame import mixer, time
import os
import threading
from tempfile import NamedTemporaryFile

class SyntheseVocale:
    _verrou = threading.Lock()

    def __init__(self, langue="fr", tld="fr", log_func=None):
        self.langue = langue
        self.tld = tld
        self.log = log_func

    def parler(self, message: str):
        if self.log:
            self.log(f"[Synthèse vocale MAISON] {message}")
        else:
            print(f"[Synthèse vocale MAISON] {message}")

        with SyntheseVocale._verrou:  # Empeche les appels concurrents
            try:
                with NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
                    tts = gTTS(text=message, lang=self.langue, tld=self.tld)
                    tts.save(fp.name)

                    mixer.init()
                    time.delay(400)  # Pause pour éviter la coupure du debut de la phrase
                    mixer.music.load(fp.name)
                    mixer.music.play()

                    while mixer.music.get_busy():
                        time.Clock().tick(10)

                    mixer.music.unload()
                    mixer.quit()

            except Exception as e:
                print(f"[Erreur synthèse vocale MAISON] {e}")