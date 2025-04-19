# Voicereg-spresense
![License](https://img.shields.io/github/license/Sony-Spresense-Voice-Authentication/voicerecg-spresense)
![Language count](https://img.shields.io/github/languages/count/Sony-Spresense-Voice-Authentication/voicerecg-spresense)
![Top language](https://img.shields.io/github/languages/top/Sony-Spresense-Voice-Authentication/voicerecg-spresense)
![Last commit](https://img.shields.io/github/last-commit/Sony-Spresense-Voice-Authentication/voicerecg-spresense)
![Maintenance](https://img.shields.io/maintenance/yes/2024)
[![python](https://img.shields.io/badge/Python-3.10-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)

[//]: # (![GH Pages deployment]&#40;https://img.shields.io/github/deployments/Raymo111/voiceprint/github-pages?label=gh-pages%20deployment&logo=github&#41;)
[//]: # (![Site status]&#40;https://img.shields.io/website?down_message=offline&label=site%20status&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjA5IiBoZWlnaHQ9IjQ1MiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgb3ZlcmZsb3c9ImhpZGRlbiI+PGRlZnM+PGNsaXBQYXRoIGlkPSJjbGlwMCI+PHBhdGggZD0iTTE4OCAxNzAgNzk3IDE3MCA3OTcgNjIyIDE4OCA2MjJaIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGNsaXAtcnVsZT0iZXZlbm9kZCIvPjwvY2xpcFBhdGg+PC9kZWZzPjxnIGNsaXAtcGF0aD0idXJsKCNjbGlwMCkiIHRyYW5zZm9ybT0idHJhbnNsYXRlKC0xODggLTE3MCkiPjxwYXRoIGQ9Ik01NzguOTE2IDM2Ny45MzQgNjI2LjM5MyAzODUuOTI2IDU5NC40NzcgNDY5Ljk0NyA1NDcgNDUxLjk1NVpNNzAyLjQ5MyAxODIuOTUxIDcwMi43MjUgMTgzLjAzNkM3NTcuNTM5IDIwNi4zNDEgNzk2IDI2MC44OTggNzk2IDMyNC40ODYgNzk2IDQwOS4yNyA3MjcuNjI1IDQ3OCA2NDMuMjggNDc4IDYyNy40NjUgNDc4IDYxMi4yMTIgNDc1LjU4NCA1OTcuODY1IDQ3MS4wOThMNTk0LjUwOSA0NjkuODY0IDYyNi40MTggMzg1Ljg2MSA2MzAuNTY3IDM4Ny4xNjdDNjM0LjY3MyAzODguMDE5IDYzOC45MjUgMzg4LjQ2NyA2NDMuMjggMzg4LjQ2NyA2NzguMTE5IDM4OC40NjcgNzA2LjM2MiAzNTkuODIyIDcwNi4zNjIgMzI0LjQ4NiA3MDYuMzYyIDMwMS4yOTcgNjk0LjE5OSAyODAuOTg5IDY3NS45OSAyNjkuNzY4TDY3MC41ODMgMjY2Ljk2Wk02NjguNjcyIDE3MCA3MDIuNTM4IDE4Mi44MzQgNjcwLjY5NyAyNjYuNjU4IDYzNi44MzEgMjUzLjgyNFoiIGZpbGw9IiNGRjAwMDAiIGZpbGwtcnVsZT0iZXZlbm9kZCIvPjxwYXRoIGQ9Ik00ODEgMCAzNjcuMzc1IDAgMjQwLjUgMzI5LjEyMSAxMTMuNjI1IDAgMCAwIDE3MS4xOTUgNDUxIDE4MC45ODUgNDUxIDMwMC4wMTUgNDUxIDMwOS44MDUgNDUxWiIgZmlsbD0iIzAwQUEwMCIgZmlsbC1ydWxlPSJldmVub2RkIiB0cmFuc2Zvcm09Im1hdHJpeCgtMSAtOC43NDIyOGUtMDggLTguNzQyMjhlLTA4IDEgNjY5IDE3MCkiLz48L2c+PC9zdmc+&up_message=online&url=https%3A%2F%2Fvoiceprint.ml&#41;)


Voice biometric authentication with multi user support. Based on https://github.com/Raymo111/voiceprint 

# Usage

## Preparation
If you are using conda:
```shell
conda create -n voicereg python=3.10 setuptools=59.8.0
conda activate voicereg
pip install -r requirements.txt
pip install pyaudio
```
If you are using MacOS, You need to install an additional package to run PyAudio:
```shell
brew install portaudio
LDFLAGS="-L/{opt/homebrew/}lib" CFLAGS="-I/{opt/homebrew}/include" pip install --no-cache-dir pyaudio
```

## Training 
```shell
python src/cli.py
```
If you have existing audios or models and would like to delete them when training:
### Delete Audios
```shell
python src/cli.py -da 
```

### Delete Models
```shell
python src/cli.py -dm
```

## Authentication
```shell
python src/cli.py -a
```