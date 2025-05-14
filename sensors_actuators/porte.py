from gpio_manager import GpioManager
import RPi.GPIO as GPIO

class Porte:
    def __init__(self, gpiomanager: GpioManager):
        self.gpio_manager = gpiomanager
        self.gpio_manager.setup_led_pin_bi_rouge()
        self.gpio_manager.setup_led_pin_bi_verte()
        self.gpio_manager.setup_switch_porte()
        GPIO.output(self.gpio_manager.led_pin_bi_rouge, GPIO.LOW)
        GPIO.output(self.gpio_manager.led_pin_bi_verte, GPIO.LOW)
        self.switch_porte = False

    def ouvrir_porte(self):
        GPIO.output(self.gpio_manager.led_pin_bi_rouge, GPIO.LOW)
        GPIO.output(self.gpio_manager.led_pin_bi_verte, GPIO.HIGH)

    def ferme_porte(self):
        GPIO.output(self.gpio_manager.led_pin_bi_rouge, GPIO.HIGH)
        GPIO.output(self.gpio_manager.led_pin_bi_verte, GPIO.LOW)

    def switch_porte_est_active(self):
        if GPIO.input(self.gpio_manager.switch_porte) == 1:
            self.switch_porte = True
            return self.switch_porte
        else:
            self.switch_porte = False
            return self.switch_porte
        
    

    