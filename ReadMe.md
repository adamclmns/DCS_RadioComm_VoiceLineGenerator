# DCS RadioComm VoiceLineGenerator

For lots of reasons, mission editors want to have a radio-like voice for certain triggers and events. For other reasons, a lot of people don't want to record their own voice, and clipping too much out of movies can get you in trouble for copyright. 

This tool aims to provide some barebones audio with a light radio-like filter applied automatically. 

## Installing this Script

* Must have Python 3.9 or higher installed.
* Must have `ffmpeg.exe` and `ffprobe.exe` located at `%FFMPEG_HOME%/bin/`. (Download a windows package from - http://www.ffmpeg.org/download.html#build-windows)
* This script uses [Pyttsx3](https://pypi.org/project/pyttsx3/) and [pydub](https://github.com/jiaaro/pydub). Make sure you `pip install` both of those. You can run `pip install -r requirements.txt` to install dependencies automatically. 


## Running the Script
Once you're setup, just make a CSV file with the audio file names in column 1, and the phrase, with wrapped in `"` or `,` in column 2
___
Generate audio with the default voice, and a csv file of lines with 

    `python ./dcs_speech_generator.py --file csvFilePath.csv`
___
Generate with a specific voice using 

    `python ./dcs_speech_generator.py --file csvFilePath.csv --voice [voiceID from your system]`
___
List all currently installed voice ID's for your system 

    `python ./dcs_speech_generator.py --lsvoices`
___
Specify your FFMPEG home directory manually with the `--ffmpegHome` flag. 
    `python  ./dcs_speech_generator.py --ffmpegHome C:\path\to\ffmpeg\ --file csv\File\Path.csv`

___
Audio files will be dropped in the current users's Desktop folder, unless the `--outputDir` flag is used. the trailing "\" can be included or ommitted, 

    `python  ./dcs_speech_generator.py --file csv\File\Path.csv --outputDir C:\my\custom\path` 

    `python  ./dcs_speech_generator.py --file csv\File\Path.csv --outputDir C:\my\custom\path\` 
___
Boost or reduce the overall volume of the audio generated using the `--volume` flag

    `python  ./dcs_speech_generator.py --file csv\File\Path.csv --volume 5`

    `python  ./dcs_speech_generator.py --file csv\File\Path.csv --volume -5`

___


## Future Features
* Configurable high/low pass filter parameters
* Configurable white-noise generator
* Configurable in/out 'click' tracks
* Ability to control volume 
* PyTest
* An `.exe` Release