import os
import logging
import pickle
import numpy as np
import sklearn
import python_speech_features as features
import scipy.io.wavfile as wav
import sklearn.mixture
import noisereduce
from pydub import AudioSegment
import utilities as ut

BASEPATH = os.path.dirname(__file__)

def test_noise_reduction(path, path2):
    logging.debug(path)
    rate, data = wav.read(path)
    # convert stereo to mono if applicable

    if len(data.shape) > 1:
        sound = AudioSegment.from_wav(path)
        sound = sound.set_channels(1)
        sound.export(path, format="wav")

    rate, mono_data = wav.read(path)

    reduced_noise_data = noisereduce.reduce_noise(y=mono_data, sr=rate, n_fft=2048)
    wav.write(path2, rate, reduced_noise_data)


def voice_features(rate, data):
    """ Extracts MFCC features from the given WAV data, also reduces noise
    Parameters:
    rate: int               - sampling rate of WAV file
    data: numpy array       - data from WAV file

    audiodata[[left right]
              [left right]
               ...
              [left right]]

    """
    # convert stereo to mono if applicable
    if len(data.shape) > 1:
        raise ValueError("WAV file is not mono!")

    reduced_noise = noisereduce.reduce_noise(y=data, sr=rate, n_fft=2048)
    mfccs = features.mfcc(reduced_noise, rate, nfft=2048)  # using default parameters except fft size
    mfccs = sklearn.preprocessing.scale(mfccs)
    delta_mfccs = features.delta(mfccs, 2)
    return np.hstack((mfccs, delta_mfccs))


# TODO: improve the scaling and accuracy of the model -> wordlists? better word distribition? bg noise filtering?
def build_model(name, paths):
    """ Builds Gaussian Mixture Model from features of each WAV file in paths collection
    Parameters:
    name: str               - name of model ($USER)
    paths: list[str]        - list of paths of WAV files. WAV files MUST BE MONO NOT STERO
    """
    dest = os.path.join(BASEPATH, '../../audio_models')
    models_dir = os.path.join(BASEPATH, '../../models_parameters')

    ut.check_folder(models_dir)
    ut.check_folder(dest)

    combined_features = np.asarray([])
    logging.debug(dest)
    for path in paths:
        sampling_rate, data = wav.read(path)
        features = voice_features(sampling_rate, data)
        if combined_features.size == 0:
            combined_features = features
        else:
            combined_features = np.vstack([combined_features, features])

    if combined_features.size != 0:
        logging.debug(f"# samples: {len(paths)}")

        # 训练GMM模型
        gmm = sklearn.mixture.GaussianMixture(n_components=len(paths), max_iter=200, covariance_type='diag', n_init=3)
        gmm.fit(combined_features)

        # 保存GMM模型
        pickle.dump(gmm, open(os.path.join(dest, f'{name}.gmm'), 'wb'))

        # 导出模型参数
        weights = gmm.weights_
        means = gmm.means_
        covariances = gmm.covariances_

        np.savetxt(os.path.join(models_dir, f'{name}_weights.txt'), weights)
        np.savetxt(os.path.join(models_dir, f'{name}_means.txt'), means)
        np.savetxt(os.path.join(models_dir, f'{name}_covariances.txt'), covariances.reshape(-1, covariances.shape[-1]))

        # 更新用户列表文件
        users_list_path = os.path.join(models_dir, 'users_list.txt')
        with open(users_list_path, 'a') as f:
            f.write(name + '\n')
            
        return True
    else:
        logging.warning(" NO FEATURES")
        return False


def compare(audio_path, model_path):
    """Compares audio features against a specific model to find the match probability.
    Parameters:
    audio_path: str - path of WAV file to compare
    model_path: str - path of the GMM model file
    """
    # 读取音频文件
    sampling_rate, data = wav.read(audio_path)

    # 加载指定的模型
    model = pickle.load(open(model_path, 'rb'))

    # 计算特征
    features = voice_features(sampling_rate, data)

    # 计算对数似然度
    ll = np.array(model.score(features)).sum()

    # 提取模型名称
    model_name = model_path.split('/')[-1].split('.')[0]

    logging.debug(f"Model: {model_name}, Log Likelihood: {ll}")

    return model_name, ll

