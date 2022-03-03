from doctest import OutputChecker
from email.policy import default
import pyttsx3
import getpass
import os
import sys
import argparse
from pydub import AudioSegment, generators, silence


# CONFIGURATION - This is per your Local Machine installation of ffmpeg. Try running this in IDLE if it fails. If you cannot read the env variable, you might try rebooting.


class RadioCommVoiceGenerator:
    def __init__(self):
        # PARAMS defined as class variables
        self.file = ""
            # This voice is on 99% of all Windows 10/11 systems
        self.voice = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"
        self.lsvoices = False
        self.volume =0
        # END PARAMS
        # Volume mix settings for future customization
        self._click_volume_decrease = 15
        self._filter_boost = 10
        self._overlayed_boost = 10
        self._white_noise_decrease = 25
        self._high_pass_filter_arg = 4000
        self._low_pass_filter_arg = 3000
        # Audio files for 'click in' and 'click out'
        self._IN_WAV = "In.wav"
        self._OUT_WAV = "Out.wav"
        self._ffmpegHome = os.getenv("FFMPEG_HOME")

    # Adds a couple filters, and adds static, and clicks to end/beginning of track
    def addRadioNoiseFilters(self, audio_segment):

        # Convinient lambdas found on SO
        _trim_leading_silence: AudioSegment = lambda x: x[silence.detect_leading_silence(
            x):]
        _trim_trailing_silence: AudioSegment = lambda x: _trim_leading_silence(
            x.reverse()).reverse()
        _strip_silence: AudioSegment = lambda x: _trim_trailing_silence(
            _trim_leading_silence(x))

        in_Wave = AudioSegment.from_wav(
            self._IN_WAV) - self._click_volume_decrease  # reduce volume
        out_Wave = AudioSegment.from_wav(
            self._OUT_WAV)-self._click_volume_decrease  # reduce volume
        # high and low pass filter, to compress the sound.
        filtered = audio_segment.high_pass_filter(self._high_pass_filter_arg).low_pass_filter(self._low_pass_filter_arg)
        filtered = filtered + self._filter_boost  # boost volume
        # strip leading/trailing silence
        filtered = _strip_silence(filtered)
        combined = in_Wave + filtered + out_Wave  # concatenate
        whiteNoise = generators.WhiteNoise().to_audio_segment(
            duration=len(combined))  # white noise profile generated
        # overlay white noise, dropping WN volume.
        overlayed = combined.overlay(whiteNoise - self._white_noise_decrease)
        overlayed = overlayed + self.volume  # bump volume of all audio
        return overlayed 

    def configureFfmpegForPyDub(self):
        AudioSegment.converter = self._ffmpegHome+"\\ffmpeg.exe"
        AudioSegment.ffmpeg = self._ffmpegHome+"\\ffmpeg.exe"
        AudioSegment.ffprobe = self._ffmpegHome+"\\ffprobe.exe"
    # Converts from MP3 format to OGG for DCS Missions

    def convertMP3toOGG(self, mp3FilenamePath):
        print("Converting "+mp3FilenamePath)
        oggFileNamePath = mp3FilenamePath.replace(".wav", ".ogg")
        # it's a wave, but this works.
        segment = AudioSegment.from_mp3(mp3FilenamePath)
        segment = self.addRadioNoiseFilters(segment)
        segment.export(oggFileNamePath, format='ogg')
        os.remove(mp3FilenamePath)
        return oggFileNamePath

    # Writes speech audio to MP3 format.

    def writeSpeechToFile(self, voiceFileName, voiceText, voiceID, speechEngine):
        speechEngine.setProperty('voice', voiceID)

        print(voiceFileName+" with audio: "+voiceText)
        if not self.outputDir.endswith("\\"):
            self.outputDir+="\\"
        filePath = self.outputDir + voiceFileName + ".wav"
        speechEngine.save_to_file(voiceText, filePath)
        speechEngine.runAndWait()
        return filePath

    # Parses the CSV file argument into a dictionary for text.

    def parseLinesFromCSV(self):
        lines = {}
        for line in open(self.file, 'r').readlines():
            splitParts = line.split(',')
            lines[splitParts[0]] = splitParts[1]
        return lines

    # List out all the voices on the system by ID

    def enumerateInstalledVoices(self,speechEngine):
        voices = speechEngine.getProperty('voices')
        print("Currently available System voices:")
        for voice in voices:
            print(voice.id)
        print("You can copy/paste the Voice name from this console view to set the desired voice.")
        input("Press <ENTER> to continue")

    def run(self):
        engine = pyttsx3.init()
        self.configureFfmpegForPyDub()
        if self.lsvoices == True:
            self.enumerateInstalledVoices(engine)
        elif self.file != "":
            textToOutput = self.parseLinesFromCSV()

            print(textToOutput)
            for audioKey in textToOutput.keys():
                filePath = self.writeSpeechToFile(
                    audioKey, textToOutput[audioKey], self.voice, engine)
                oggFile = self.convertMP3toOGG(filePath)
                print("Created file: "+oggFile)

        engine.stop()

    def runWithConfiguration(self, file, voice, outputDir):
        self.file = file
        self.voice = voice
        self.outputDir = outputDir
        self.run()

# END RadioCommsGenerator

# parse command line arguments and configure the class.


def configureCommGeneratorFromCLI(sysArgsv):
    commGeneratorClass = RadioCommVoiceGenerator()  # new instance
    defaultOutputDir = "C:\\Users\\" + getpass.getuser() + "\\Desktop\\"
    defaultVoiceID = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"
    defaultFfmpegHome = os.getenv("FFMPEG_HOME")
    
    parser = argparse.ArgumentParser(
        description="A voice line generator, for generating radio-comms-like audio files for use with the DCS World Mission Editor.")
    parser.add_argument('--file', help="The absolute or relative path to a CSV file with your desired voice lines typed out in the correct format.",
                        type=str, default=argparse.SUPPRESS)
    parser.add_argument('--voice', help='Copy/Pasted value for Voice as displayed by \'--lsvoices\' flag',
                        type=str, default=defaultVoiceID)
    parser.add_argument(
        '--lsvoices', help='list installed voice IDs', action='store_true')
    parser.add_argument("--outputDir", help="Specify the directory to output voice file to. Defaults to 'Desktop' folder. Trailing '\\' is optional",
                        type=str, default=defaultOutputDir)
    parser.add_argument("--ffmpegHome", help="Manually specify the FFMPEG home directory where /bin/ffmpeg.exe exists",
                        type=str, default=defaultFfmpegHome)
    parser.add_argument("--volume",type=int,default=0,help="Set a volume boost or drop for the generated audio")
    parser.parse_known_args(sysArgsv, namespace=commGeneratorClass)
    return commGeneratorClass


# Run when script is executed.
if __name__ == '__main__':
    commGeneratorClass = configureCommGeneratorFromCLI(sys.argv)
    commGeneratorClass.run()
