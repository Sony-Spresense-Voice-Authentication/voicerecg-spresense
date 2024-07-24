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

GPIO.setmode(GPIO.BCM)


def unlock(channel=23):
    logging.debug("Sending unlock signal to GPIO channel {}".format(channel))
    GPIO.setup(channel, GPIO.OUT)
    GPIO.output(channel, GPIO.HIGH)  # Unlock when it is set to high
    time.sleep(5)  # Wait for 5 seconds before releasing
    GPIO.output(channel, GPIO.LOW)  # Relock after sleep
    GPIO.cleanup()


def lock(channel=24):
    logging.debug("Sending lock signal to GPIO channel {}".format(channel))
    GPIO.setup(channel, GPIO.OUT)
    time.sleep(5)
    GPIO.output(channel, GPIO.LOW)


def msc_enabled(channel=25):
    logging.debug("Sending msc enabled signal to GPIO channel {}".format(channel))
    GPIO.setup(channel, GPIO.IN)
    logging.debug("MSC_PIN: " + str(GPIO.input(channel)))
    return GPIO.input(channel)
