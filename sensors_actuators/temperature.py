from gpio_manager import GpioManager
import RPi.GPIO as GPIO

class Temperature:
    def __init__(self, gpiomanager: GpioManager):
        self.gpio_manager = gpiomanager
        self.gpio_manager.setup_led_pin_rouge()
        self.gpio_manager.setup_led_pin_bleu()
        self.gpio_manager.setup_bouton_ventilation()
        self.gpio_manager.setup_bouton_chauffage()
        GPIO.output(self.gpio_manager.led_pin_rouge, GPIO.LOW)
        GPIO.output(self.gpio_manager.led_pin_bleu, GPIO.LOW)

    def active_chauffage (self):
        GPIO.output(self.gpio_manager.led_pin_rouge, GPIO.HIGH)
    
    def desactive_chauffage(self):
        GPIO.output(self.gpio_manager.led_pin_rouge, GPIO.LOW)

    def active_ventilation (self):
        GPIO.output(self.gpio_manager.led_pin_bleu, GPIO.HIGH) 
    
    def desactive_ventilation (self):
        GPIO.output(self.gpio_manager.led_pin_bleu, GPIO.LOW)

    def bouton_chauffage_est_active(self):
        if GPIO.input(self.gpio_manager.bouton_chauffage) == 0:
            return True
        else:
            return False 

    def bouton_ventilation_est_active(self):
        if GPIO.input(self.gpio_manager.bouton_ventilation) == 0:
            return True
        else:
            return False       