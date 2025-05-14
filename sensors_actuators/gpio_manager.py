import yaml
import RPi.GPIO as GPIO
from gpiozero import Buzzer 

class GpioManager :
    def __init__(self,config_file="config/smart_home_config.yaml" ):
        self.config = self.load_config(config_file)  # Charger la configuration YAML
        self.led_pin_rouge = self.config["GPIO"]["led_pin_rouge"]
        self.led_pin_bleu = self.config["GPIO"]["led_pin_bleu"]
        self.led_pin_jaune = self.config["GPIO"]["led_pin_jaune"]
        self.led_pin_bi_rouge = self.config["GPIO"]["led_pin_bi_rouge"]
        self.led_pin_bi_verte = self.config["GPIO"]["led_pin_bi_verte"]
        self.pir_sensor = self.config["GPIO"]["pir_sensor"]
        self.switch_porte = self.config["GPIO"]["switch_porte"]
        self.switch_lumiere = self.config["GPIO"]["switch_lumiere"]
        self.bouton_chauffage = self.config["GPIO"]["bouton_chauffage"]
        self.bouton_ventilation = self.config["GPIO"]["bouton_ventilation"]
        self.buzzer_pin = self.config["GPIO"]["buzzer_pin"]
        GPIO.setmode(GPIO.BCM)

    #LED
    def setup_led_pin_rouge(self):
        GPIO.setup(self.led_pin_rouge, GPIO.OUT)

    def setup_led_pin_bleu(self):
        GPIO.setup(self.led_pin_bleu, GPIO.OUT)

    def setup_led_pin_jaune(self):
        GPIO.setup(self.led_pin_jaune, GPIO.OUT)

    def setup_led_pin_bi_rouge(self):
        GPIO.setup(self.led_pin_bi_rouge, GPIO.OUT)
        
    def setup_led_pin_bi_verte(self):
        GPIO.setup(self.led_pin_bi_verte, GPIO.OUT)
    
    #Pir_sensor
    def setup_pir_sensor (self):
        GPIO.setup(self.pir_sensor, GPIO.IN)

    #Boutons
    def setup_bouton_chauffage(self):
        GPIO.setup(self.bouton_chauffage, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    def setup_bouton_ventilation(self):
        GPIO.setup(self.bouton_ventilation, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    #switch
    def setup_switch_porte(self):
        GPIO.setup(self.switch_porte, GPIO.IN)
    def setup_switch_lumiere(self):
        GPIO.setup(self.switch_lumiere, GPIO.IN)

    #Buzzer
    def setup_buzzer(self):
        GPIO.setup(self.buzzer_pin, GPIO.OUT)

    def nettoyer(self):
        GPIO.cleanup()
        print("[MAISON CLIENT] Nettoyage des GPIO")


    def load_config(self, config_file):
        """ Charger la configuration depuis un fichier YAML """
        with open(config_file, "r") as file:
            return yaml.safe_load(file)