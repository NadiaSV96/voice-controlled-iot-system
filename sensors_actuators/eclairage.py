from gpio_manager import GpioManager
import RPi.GPIO as GPIO

class Eclairage:
    def __init__(self, gpiomanager: GpioManager):
        self.gpio_manager = gpiomanager
        self.gpio_manager.setup_led_pin_jaune()
        self.gpio_manager.setup_switch_lumiere()
        GPIO.output(self.gpio_manager.led_pin_jaune, GPIO.LOW)
        self.switch_lumiere = False

    def ouvrir_eclairage(self):
        GPIO.output(self.gpio_manager.led_pin_jaune, GPIO.HIGH)

    def ferme_eclairage(self):
        GPIO.output(self.gpio_manager.led_pin_jaune, GPIO.LOW)

    def switch_lumiere_est_active(self):
        if GPIO.input(self.gpio_manager.switch_lumiere) == 1:
            self.switch_lumiere = True
            return self.switch_lumiere
        else:
            self.switch_lumiere = False
            return self.switch_lumiere     
