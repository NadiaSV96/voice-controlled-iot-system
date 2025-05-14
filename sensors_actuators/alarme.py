from gpio_manager import GpioManager
import RPi.GPIO as GPIO
import time
import threading
class Alarme:
    def __init__(self, gpiomanager: GpioManager):
        self.gpio_manager = gpiomanager
        self.gpio_manager.setup_led_pin_bi_rouge()
        self.gpio_manager.setup_buzzer()
        GPIO.output(self.gpio_manager.led_pin_bi_rouge, GPIO.LOW)
        GPIO.output(self.gpio_manager.buzzer_pin, GPIO.LOW)
        self._clignotement_actif = False
        self._thread_clignotement = None

    def _clignoter(self):
        while self._clignotement_actif:
            GPIO.output(self.gpio_manager.led_pin_bi_rouge, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(self.gpio_manager.led_pin_bi_rouge, GPIO.LOW)
            time.sleep(0.1)

    def active_clignotement(self):
        if not self._clignotement_actif:
            self._clignotement_actif = True
            self._thread_clignotement = threading.Thread(target=self._clignoter, daemon=True)
            self._thread_clignotement.start()

    def desactive_clignotement(self):
        self._clignotement_actif = False
        GPIO.output(self.gpio_manager.led_pin_bi_rouge, GPIO.LOW)

    def active_buzzer (self):
        GPIO.output(self.gpio_manager.buzzer_pin, GPIO.HIGH)

    def desactive_buzzer (self):
        GPIO.output(self.gpio_manager.buzzer_pin, GPIO.LOW)