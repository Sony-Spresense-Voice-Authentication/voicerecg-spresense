#!/usr/bin/env python3
import argparse
import os
import glob
import sys
from voice_auth import voice_auth
from voice_auth import voice_record
import logging
import utilities as ut
import serial
import time

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

THRESHOLD = -300
SECONDS = 5
BASEPATH = os.path.dirname(__file__)
AUDIOPATH = os.path.join(os.path.join(BASEPATH, '../audio'))
MODELPATH = os.path.join(os.path.join(BASEPATH, '../audio_models'))
THRESHOLDPATH = os.path.join(os.path.join(BASEPATH, '../thresholds'))
NUM_SAMPLE = 6
DEFAULT_PHRASE = 'The quick fox jumps nightly above the wizard'

SERIAL_PORT = 'COM7'  # Change it to the actual serial port number
BAUD_RATE = 115200
SD_CARD_DRIVE = 'E:'  # Change to the actual drive number of the Spresense SD card

ut.check_folder(AUDIOPATH)
ut.check_folder(MODELPATH)
ut.check_folder(THRESHOLDPATH)


# Search the SD card for a file with the name "compare.wav".
def find_compare_file():
    compare_file_path = None
    logging.info(f"SD card {SD_CARD_DRIVE} found. Searching for compare.wav...")
    for root, dirs, files in os.walk(SD_CARD_DRIVE):
        for file in files:
            if file == "compare.wav":
                compare_file_path = os.path.join(root, file)
                logging.info(f"Found compare.wav at: {compare_file_path}")
                break
        if compare_file_path:
            break
    return compare_file_path


def authenticate(ser):
    compare_audio_path = find_compare_file()

    if not compare_audio_path:
        logging.error("No 'compare.wav' file found. Aborting.")
        return False

    logging.info(f"Using file: {compare_audio_path}")

    model_files = glob.glob(os.path.join(MODELPATH, '*.gmm'))
    for model_file in model_files:
        username = os.path.basename(model_file).replace('.gmm', '')
        threshold_file = os.path.join(THRESHOLDPATH, f'{username}.txt')

        try:
            with open(threshold_file, 'r') as f:
                THRESHOLD = float(f.read())
        except Exception as e:
            logging.error(f"Error reading the threshold for {username}: {e}")
            continue

        model, prob = voice_auth.compare(compare_audio_path, model_file)

        logging.debug(f"Model: {model}, Probability: {prob}, Threshold: {THRESHOLD}")

        if prob and prob > THRESHOLD:
            logging.info(f'User {username} verified.')
            # ser.write(b"TRUE\n")
            return True

    logging.info('No user verified.')
    # ser.write(b"FALSE\n")
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--auth', action='store_true', required=False)
    parser.add_argument('-p', '--phrase', required=False, help='Define your own phrase')
    parser.add_argument('-dm', '--delete-model', action='store_true', required=False, help='Delete model files')
    parser.add_argument('-da', '--delete-audio', action='store_true', required=False, help='Delete audio files')
    args = parser.parse_args()

    if not args.auth:
        if args.delete_model:
            files = glob.glob(os.path.join(MODELPATH, '*'))
            for f in files:
                os.remove(f)

        if args.delete_audio:
            files = glob.glob(os.path.join(AUDIOPATH, '*'))
            for f in files:
                os.remove(f)

        phrase = args.phrase if args.phrase else DEFAULT_PHRASE
        username = input('Please input your username: ')

        paths_modelling = []
        if os.path.exists(os.path.join(AUDIOPATH, f'{username}1.wav')):
            logging.info("User " + username + " modeling data exists, skipping recording.")
            for i in range(1, NUM_SAMPLE // 2 + 1):
                path = os.path.join(AUDIOPATH, username + str(i) + '.wav')
                paths_modelling.append(path)
            logging.debug("Path Modeling: " + str(paths_modelling))
        else:
            print("Please say the phrase:", phrase)
            for i in range(1, NUM_SAMPLE // 2 + 1):
                input('Press enter to record... ')
                path = os.path.join(AUDIOPATH, username + str(i) + '.wav')
                voice_record.record(path, SECONDS)
                paths_modelling.append(path)

        paths_training = []
        if os.path.exists(os.path.join(AUDIOPATH, f'{username}4.wav')):
            logging.info("User " + username + " training data exists, skipping recording.")
            for i in range(4, NUM_SAMPLE + 1):
                path = os.path.join(AUDIOPATH, username + str(i) + '.wav')
                paths_training.append(path)
            logging.debug("Path Training: " + str(paths_training))
        else:
            print("Please say the phrase:", phrase)
            for i in range(4, NUM_SAMPLE + 1):
                input('Press enter to record... ')
                path = os.path.join(AUDIOPATH, username + str(i) + '.wav')
                voice_record.record(path, SECONDS)
                paths_training.append(path)

        voice_auth.build_model(username, paths_modelling)
        model_path = os.path.join(MODELPATH, username + '.gmm')

        thresholds = []
        for path in paths_training:
            model, prob = voice_auth.compare(path, model_path)
            thresholds.append(prob)

        THRESHOLD = (sum(thresholds) / len(thresholds)) - 0.5
        logging.debug(THRESHOLD)

        with open(os.path.join(THRESHOLDPATH, f'{username}.txt'), 'w') as f:
            f.write(str(THRESHOLD))
        logging.info("User " + username + " modeling data saved.")
    else:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            logging.info(f"Listening on {SERIAL_PORT} at {BAUD_RATE} baud.")

            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    logging.info(f"Received: {line}")
                    if line == "START":
                        authenticate(ser)
        except serial.SerialException as e:
            logging.error(f"Error: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
