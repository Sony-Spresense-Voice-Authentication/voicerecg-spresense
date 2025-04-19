#!/usr/bin/env python3
import argparse
import os
import glob
import random
import sys
import numpy as np
from typing import Optional
from voice_auth import voice_auth
from voice_auth import voice_record
import logging
from utilities import *

# logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)

# Set up constants
THRESHOLD = -300
SECONDS = 4
BASEPATH = os.path.dirname(__file__)
AUDIOPATH = os.path.join(BASEPATH, '../audio')
MODELPATH = os.path.join(BASEPATH, '../audio_models')
THRESHOLDPATH = os.path.join(BASEPATH, '../thresholds')
# NUM_SAMPLE = 6

# Check if folders exist and create them if not
check_folder(AUDIOPATH)
check_folder(MODELPATH)
check_folder(THRESHOLDPATH)


# phrase = 'The quick fox jumps nightly above the wizard'
# Create a list of phrases for preventing overfitting to a single phrase
# The phrases should be similar in length and phonetic structure
# If you are able to speak Cantonese, you can use Cantonese phrases, for example:
# '三九四零五二八九'
# '三九四零五二八九' is a Cantonese phrase that is similar in length and phonetic structure
# to the English phrase 'The quick fox jumps nightly above the wizard'
# '三碗半牛腩飯一百碟' is also a Cantonese phrase that is similar in length and phonetic structure
# to the English phrase 'The quick fox jumps nightly above the wizard'
# These two phrases contains 9 tones and 6 modes of pronunciation,
# which can provide a much better sample for the model to learn from
# You can use one in the modeling list and the other in the training list
phrase_list = [
    'The quick fox jumps nightly above the wizard',
    'The quick brown fox jumps over the lazy dog',
    'The five boxing wizards jump quickly',
    'Pack my box with five dozen liquor jugs',
    'How vexingly quick daft zebras jump',
    'Bright vixens jump; dozy fowl quack',
    'Jinxed wizards pluck ivy from the big quilt',
    'Sphinx of black quartz, judge my vow',
    'Amazingly few discords in the spelling of words',
    'The five boxing wizards jump quickly',
    'The quick onyx goblin jumps over the lazy dwarf',
    'The quick brown fox jumps over the lazy dog',
    'The five boxing wizards jump quickly',
    'Pack my box with five dozen liquor jugs'
]
# shuffle the phrases to create a random order every time
random.shuffle(phrase_list)
phrase_stack = phrase_list
NUM_SAMPLE = len(phrase_list)
logging.debug(f"Number of samples: {NUM_SAMPLE}")
logging.debug(f"Phrase stack created (shuffled original list): {phrase_stack}")



def authenticate():
    # 定位比较用的音频文件
    compare_audio_path = os.path.join(AUDIOPATH, 'compare.wav')
    recorded_path = voice_record.record(compare_audio_path, SECONDS)

    # 遍历所有模型文件
    model_files = glob.glob(os.path.join(MODELPATH, '*.gmm'))
    over_threshold_list = []
    over_threshold_dict = {}
    
    for model_file in model_files:
        username = os.path.basename(model_file).replace('.gmm', '')
        threshold_file = os.path.join(THRESHOLDPATH, f'{username}.txt')

        try:
            with open(threshold_file, 'r') as f:
                THRESHOLD = float(f.read())
        except Exception as e:
            logging.error(f"Error reading the threshold for {username}: {e}")
            continue

        model, prob = voice_auth.compare(recorded_path, model_file)

        # logging.debug(f"Model: {model}, Probability: {prob}, Threshold: {THRESHOLD}")
        
        
        if prob and prob > THRESHOLD:
            over_threshold_list.append(prob)
            over_threshold_dict[username] = prob
            # logging.debug(f"User {username} recognized with probability {prob}.")
    
    if len(over_threshold_dict) > 0:
        # Sort the dictionary by value in descending order
        sorted_dict = dict(sorted(over_threshold_dict.items(), key=lambda item: item[1], reverse=True))
        # for key, value in sorted_dict.items():
        #     logging.debug(f"User: {key}, Probability: {value}")
        # Get the first key (username) from the sorted dictionary
        logging.debug(f"Sorted recognized users: {sorted_dict}")
        recognized_user = next(iter(sorted_dict))
        logging.debug(f"Recognized user: {recognized_user} with probability {sorted_dict[recognized_user]}.")
        logging.info(f"Recognized user: {recognized_user}")
        return True
            

    print('No user recognized.')
    return False



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--auth', action='store_true', required=False)
    parser.add_argument('-p', '--phrase', type=str, required=False, help='Define your own phrase')
    parser.add_argument('-d', '--delete-all', action='store_true', required=False, help='Delete both model and audio files')
    parser.add_argument('-dm', '--delete-model', action='store_true', required=False, help='Delete model files')
    parser.add_argument('-da', '--delete-audio', action='store_true', required=False, help='Delete audio files')
    parser.add_argument('-n', '--num-sample', type=int, default=NUM_SAMPLE, required=False, help='Number of samples to record')
    args = parser.parse_args()

    NUM_SAMPLE = args.num_sample if args.num_sample else NUM_SAMPLE


    if not args.auth:
        # Disable audio deletion when training
        if args.delete_all:
            # Delete all files in the audio and model directorie
            delete_files_in_directory(AUDIOPATH)
            delete_files_in_directory(MODELPATH)
            exit(0)
        elif args.delete_model:
            # Delete all model files
            delete_files_in_directory(MODELPATH)
            exit(0)
        elif args.delete_audio:
            delete_files_in_directory(AUDIOPATH)
            exit(0)

        phrase = args.phrase
        username = input('Please input your username: ')

        paths_modelling = []
        paths_training = []

        if os.path.exists(os.path.join(AUDIOPATH, f'{username}1.wav')):
            NUM_SAMPLE = len(glob.glob(os.path.join(AUDIOPATH, f'{username}*.wav')))
            logging.info(f"User {username} has {NUM_SAMPLE} samples.")
            logging.info("User " + username + " modeling data exists, skipping recording.")
            for i in range(1, NUM_SAMPLE//2 + 1):
                path = os.path.join(AUDIOPATH, username + str(i) + '.wav')
                paths_modelling.append(path)
            logging.debug("Path Modeling: " + str(paths_modelling))
            for i in range(NUM_SAMPLE//2, int(NUM_SAMPLE) + 1):
                path = os.path.join(AUDIOPATH, username + str(i) + '.wav')
                paths_training.append(path)
            logging.debug("Path Training: " + str(paths_training))
        else:
            # print("Please say the phrase:", phrase)
            logging.debug(f"Init phrases: {phrase_stack}")
            for i in range(1, NUM_SAMPLE//2 + 1):
                try:
                    # phrase = phrase_stack.pop_phrase()
                    phrase = phrase_stack.pop()
                    logging.debug(f"reminaing phrases: {phrase_stack}")
                except Exception as e:
                    logging.error(f"Error when loading phrase stack: {e}")
                    raise e
                print("Please say the phrase:", phrase)
                promp = input('Press enter to record... ')
                path = os.path.join(AUDIOPATH, username + str(i) + '.wav')
                voice_record.record(path, SECONDS)
                paths_modelling.append(path)
            
            for i in range(NUM_SAMPLE//2 + 1, NUM_SAMPLE + 1):
                try:
                    # phrase = phrase_stack.pop_phrase()
                    phrase = phrase_stack.pop()
                    logging.debug(f"reminaing phrases: {phrase_stack}")
                except Exception as e:
                    logging.error(f"Error when loading phrase stack: {e}")
                    raise e
                print("Please say the phrase:", phrase)
                promp = input('Press enter to record... ')
                path = os.path.join(AUDIOPATH, username + str(i) + '.wav')
                voice_record.record(path, SECONDS)
                paths_training.append(path)
            logging.debug("Path Modeling: " + str(paths_modelling))
            logging.debug("Path Training: " + str(paths_training))

        # if os.path.exists(os.path.join(AUDIOPATH, f'{username}{NUM_SAMPLE//2}.wav')):
        #     logging.info("User " + username + " training data exists, skipping recording.")
        #     for i in range(NUM_SAMPLE//2, int(NUM_SAMPLE) + 1):
        #         path = os.path.join(AUDIOPATH, username + str(i) + '.wav')
        #         paths_training.append(path)
        #     logging.debug("Path Training: " + str(paths_training))
        # else:
        #     # print("Please say the phrase:", phrase)
        #     for i in range(NUM_SAMPLE//2, int(NUM_SAMPLE) + 1):
        #         phrase = phrase_stack.pop_phrase() if phrase_stack.phrase_stack else phrase
        #         print("Please say the phrase:", phrase)
        #         promp = input('Press enter to record... ')
        #         path = os.path.join(AUDIOPATH, username + str(i) + '.wav')
        #         voice_record.record(path, SECONDS)
        #         paths_training.append(path)

        voice_auth.build_model(username, paths_modelling)
        model_path = os.path.join(MODELPATH, username + '.gmm')

        thresholds = []
        for path in paths_training:
            model, prob = voice_auth.compare(path, model_path)
            thresholds.append(prob)

        # Calculate the standard deviation of the thresholds
        std_dev = np.std(thresholds)
        logging.debug(f"Standard Deviation of the threshold: {std_dev}")
        if std_dev > 0.5: logging.warning("Threshold standard deviation is too high.")

        # THRESHOLD = (sum(thresholds) / len(thresholds)) - 0.5 # Simple mean
        # THRESHOLD = remove_high_low_average(thresholds) # Trimmed mean
        THRESHOLD = np.mean(thresholds) - 1.5 * std_dev #k-sigma thresholding
        logging.debug(f"Threadshold: {THRESHOLD}")

        f = open(os.path.join(THRESHOLDPATH, f'{username}.txt'), 'w')
        f.write(str(THRESHOLD))
        f.close()
        logging.info("User " + username + " modeling data saved.")

    else:
        sys.exit(1 if authenticate() else 0)
