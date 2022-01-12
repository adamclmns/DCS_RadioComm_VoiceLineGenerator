# DCS RadioComm VoiceLineGenerator

For lots of reasons, mission editors want to have a radio-like voice for certain triggers and events. For other reasons, a lot of people don't want to record their own voice, and clipping too much out of movies can get you in trouble for copyright. 

This tool aims to provide some barebones audio with a light radio-like filter applied automatically. 

## Using this Script

* Must have Python 3.9 or higher installed.
* Must have `ffmpeg.exe` and `ffprobe.exe` located at `%FFMPEG_HOME%/bin/`. (Download a windows package from - http://www.ffmpeg.org/download.html#build-windows)
* This script uses [Pyttsx3](https://pypi.org/project/pyttsx3/) and [pydub](https://github.com/jiaaro/pydub). Make sure you `pip install` both of those.


## Running the Script
Once you're setup, just make a CSV file with the audio file names in column 1, and the phrase, with wrapped in `"` or `,` in column 2

generate audio with the default voice, and a csv file of lines with 

`python ./dcs_speech_generator.py --file csvFilePath.csv`

generate with a specific voice using 

`python ./dcs_speech_generator.py --file csvFilePath.csv --voice [voiceID from your system]`

To list all currently installed voice ID's for your system 

`python ./dcs_speech_generator.py --lsvoices`


Currently, the audio files will be dropped in the current users's Desktop folder. 

## Future Features
* Configurable high/low pass filter parameters
* Configurable white-noise generator
* Configurable in/out 'click' tracks
* Ability to control volume 
* PEP8 Compliance
* PyTest
* Proper Documentation
* An `.exe` Release

