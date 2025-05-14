from gpio_manager import GpioManager
import RPi.GPIO as GPIO

    
class PirSensor:
    def __init__(self, gpiomanager: GpioManager):
        self.gpio_manager = gpiomanager
        gpiomanager.setup_pir_sensor()

    def mouvement_detecte(self):
        return GPIO.input(self.gpio_manager.pir_sensor) == GPIO.HIGH
