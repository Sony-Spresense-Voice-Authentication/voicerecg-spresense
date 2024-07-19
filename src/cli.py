#!/usr/bin/env python3
import argparse
import os
import glob
import sys
from typing import Optional
from voice_auth import voice_auth
from voice_auth import voice_record
import logging
import scipy.io.wavfile as wav
import utilities as ut

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

THRESHOLD = -300
SECONDS = 4
BASEPATH = os.path.dirname(__file__)
AUDIOPATH = os.path.join(os.path.join(BASEPATH, '../audio'))
MODELPATH = os.path.join(os.path.join(BASEPATH, '../audio_models'))
THRESHOLDPATH = os.path.join(os.path.join(BASEPATH, '../thresholds'))
NUM_SAMPLE = 6
phrase = 'The quick fox jumps nightly above the wizard'

ut.check_folder(AUDIOPATH)
ut.check_folder(MODELPATH)
ut.check_folder(THRESHOLDPATH)

def authenticate():
    # 定位比较用的音频文件
    compare_audio_path = os.path.join(AUDIOPATH, 'compare.wav')
    recorded_path = voice_record.record(compare_audio_path, SECONDS)

    # 遍历所有模型文件
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

        sampling_rate: int
        sampling_rate, data = wav.read(recorded_path)

        #生成 mfcc_features.txt
        voice_auth.voice_features_a(sampling_rate, data)
        #
        model, prob = voice_auth.compare_a(model_file)

        logging.info(f"Model: {model}, Probability: {prob}, Threshold: {THRESHOLD}")

        if prob and prob > THRESHOLD:
            print(f'User {username} verified.')
            return True

    print('No user verified.')
    return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--auth', action='store_true', required=False)
    parser.add_argument('-p', '--phrase', required=False)
    args = parser.parse_args()

    if not args.auth:
        files = glob.glob(os.path.join(BASEPATH, '../audio_models/*'))
        for f in files:
            os.remove(f)

        phrase = args.phrase if args.phrase else phrase
        username = input('Please input your username: ')

        paths_modelling = []
        print("Please say the phrase:", phrase)
        for i in range(1, NUM_SAMPLE//2 + 1):
            promp = input('Press enter to record... ')
            path = os.path.join(AUDIOPATH, username + str(i) + '.wav')
            voice_record.record(path, SECONDS)
            paths_modelling.append(path)

        paths_training = []
        print("Please say the phrase:", phrase)
        for i in range(4, int(NUM_SAMPLE) + 1):
            promp = input('Press enter to record... ')
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

        f = open(os.path.join(THRESHOLDPATH, f'{username}.txt'), 'w')
        f.write(str(THRESHOLD))
        f.close()

    else:
        sys.exit(1 if authenticate() else 0)
