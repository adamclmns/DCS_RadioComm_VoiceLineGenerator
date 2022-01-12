import pyttsx3
import getpass
import os
import sys
import argparse
from pydub import AudioSegment, generators, silence


# CONFIGURATION - This is per your Local Machine installation of ffmpeg. Try running this in IDLE if it fails. If you cannot read the env variable, you might try rebooting.
_ffmpegHome = os.getenv("FFMPEG_HOME")
AudioSegment.converter = _ffmpegHome+"\\ffmpeg.exe"
AudioSegment.ffmpeg = _ffmpegHome+"\\ffmpeg.exe"
AudioSegment.ffprobe = _ffmpegHome+"\\ffprobe.exe"
# This voice is on 99% of all Windows 10/11 systems
_default_voiceID = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"
# Audio files for 'click in' and 'click out'
_IN_WAV = "In.wav"
_OUT_WAV = "Out.wav"

# Convinient lambdas found on SO
_trim_leading_silence: AudioSegment = lambda x: x[silence.detect_leading_silence(
    x):]
_trim_trailing_silence: AudioSegment = lambda x: _trim_leading_silence(
    x.reverse()).reverse()
_strip_silence: AudioSegment = lambda x: _trim_trailing_silence(
    _trim_leading_silence(x))


# Adds a couple filters, and adds static, and clicks to end/beginning of track
def addRadioNoiseFilters(audio_segment):
    in_Wave = AudioSegment.from_wav(_IN_WAV)-15  # reduce volume
    out_Wave = AudioSegment.from_wav(_OUT_WAV)-15  # reduce volume
    # high and low pass filter, to compress the sound.
    filtered = audio_segment.high_pass_filter(3000).low_pass_filter(4000)
    filtered = filtered + 10  # boost volume
    filtered = _strip_silence(filtered)  # strip leading/trailing silence
    combined = in_Wave + filtered + out_Wave  # concatenate
    whiteNoise = generators.WhiteNoise().to_audio_segment(
        duration=len(combined))  # white noise profile generated
    # overlay white noise, dropping WN volume.
    overlayed = combined.overlay(whiteNoise-25)
    overlayed = overlayed + 10  # bump volume of all audio
    return overlayed

# Converts from MP3 format to OGG for DCS Missions


def convertMP3toOGG(mp3FilenamePath):
    print("Converting "+mp3FilenamePath)
    oggFileNamePath = mp3FilenamePath.replace(".wav", ".ogg")
    # it's a wave, but this works.
    segment = AudioSegment.from_mp3(mp3FilenamePath)
    segment = addRadioNoiseFilters(segment)
    segment.export(oggFileNamePath, format='ogg')
    os.remove(mp3FilenamePath)
    return oggFileNamePath

# Writes speech audio to MP3 format.


def writeSpeechToFile(voiceFileName, voiceText, voiceID, speechEngine):
    speechEngine.setProperty('voice', voiceID)
    username = getpass.getuser()
    print(voiceFileName+" with audio: "+voiceText)
    filePath = "C:\\Users\\" + username + "\\Desktop\\" + voiceFileName + ".wav"
    speechEngine.save_to_file(voiceText, filePath)
    speechEngine.runAndWait()
    return filePath

# Parses the CSV file argument into a dictionary for text.


def parseLinesFromCSV(csvFilePath):
    lines = {}
    for line in open(csvFilePath, 'r').readlines():
        splitParts = line.split(',')
        lines[splitParts[0]] = splitParts[1]
    return lines

# List out all the voices on the system by ID


def enumerateInstalledVoices(speechEngine):
    voices = speechEngine.getProperty('voices')
    print("Currently available System voices:")
    for voice in voices:
        print(voice.id)
    print("You can copy/paste the Voice name from this console view into the code to set the desired voice.")
    input("Press <ENTER> to continue")

# An object just to hold arguments in a namespace.


class MyArgs:
    pass

# parse command line arguments


def parseMyArgs(sysArgsv):
    givenArgs = MyArgs()
    parser = argparse.ArgumentParser(
        description="A voice line generator, for generating radio-comms-like audio files for use with the DCS World Mission Editor.")
    parser.add_argument('--file', help="The absolute or relative path to a CSV file with your desired voice lines typed out in the correct format.",
                        type=str, default=argparse.SUPPRESS)
    parser.add_argument('--voice', help='Copy/Pasted value for Voice as displayed by \'--lsvoices\' flag',
                        type=str, default=_default_voiceID)
    parser.add_argument(
        '--lsvoices', help='list installed voice IDs', action='store_true')
    parser.parse_known_args(sysArgsv, namespace=givenArgs)
    return givenArgs


if __name__ == '__main__':
    givenArgs = parseMyArgs(sys.argv)

    engine = pyttsx3.init()

    if givenArgs.lsvoices == True:
        enumerateInstalledVoices(engine)
    elif givenArgs.file != "":
        textToOutput = parseLinesFromCSV(givenArgs.file)

        print(textToOutput)
        for audioKey in textToOutput.keys():
            filePath = writeSpeechToFile(
                audioKey, textToOutput[audioKey], givenArgs.voice, engine)
            oggFile = convertMP3toOGG(filePath)
            print("Created file: "+oggFile)

    engine.stop()
