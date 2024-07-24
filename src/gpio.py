import importlib.util
import logging
import time

try:
    importlib.util.find_spec('RPi.GPIO')
    import RPi.GPIO as GPIO
except ImportError:
    """
    import FakeRPi.GPIO as GPIO
    OR
    import FakeRPi.RPiO as RPiO
    """
    import FakeRPi.GPIO as GPIO

TRUE_PIN = 23
FALSE_PIN = 24
MSC_PIN = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRUE_PIN, GPIO.OUT)
GPIO.setup(FALSE_PIN, GPIO.OUT)
GPIO.setup(MSC_PIN, GPIO.IN)


def unlock():
    logging.debug("Sending unlock signal to GPIO channel {}".format(TRUE_PIN))
    GPIO.output(TRUE_PIN, GPIO.HIGH)  # Unlock when it is set to high
    time.sleep(5)  # Wait for 5 seconds before releasing
    GPIO.output(TRUE_PIN, GPIO.LOW)  # Relock after sleep
    GPIO.cleanup()


def lock():
    logging.debug("Sending lock signal to GPIO channel {}".format(FALSE_PIN))
    GPIO.setup(FALSE_PIN, GPIO.OUT)
    time.sleep(5)
    GPIO.output(FALSE_PIN, GPIO.LOW)


def msc_enabled():
    logging.debug("Sending msc enabled signal to GPIO channel {}".format(MSC_PIN))
    GPIO.setup(MSC_PIN, GPIO.IN)
    logging.debug("MSC_PIN: " + str(GPIO.input(MSC_PIN)))
    return GPIO.input(MSC_PIN)
