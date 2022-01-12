import pyttsx3, getpass, os, sys, argparse
from pydub import AudioSegment
from pydub import generators
from pydub import silence

## CONFIGURATION - This is per your Local Machine installation of ffmpeg.
ffmpegHome = "C:\\ffmpeg-2022-01-10-git-f37e66b393-full_build\\bin" 
AudioSegment.converter = ffmpegHome+"\\ffmpeg.exe"
AudioSegment.ffmpeg = ffmpegHome+"\\ffmpeg.exe"
AudioSegment.ffprobe = ffmpegHome+"\\ffprobe.exe"

## Audio files for 'click in' and 'click out'
IN_WAV = "In.wav"
OUT_WAV = "Out.wav"

## Convinient lambdas found on SO
trim_leading_silence: AudioSegment = lambda x: x[silence.detect_leading_silence(x) :]
trim_trailing_silence: AudioSegment = lambda x: trim_leading_silence(x.reverse()).reverse()
strip_silence: AudioSegment = lambda x: trim_trailing_silence(trim_leading_silence(x))

default_voiceID = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"
## Adds a couple filters, and adds static, and clicks to end/beginning of track
def addLowPassFilter(audio_segment):
    in_Wave = AudioSegment.from_wav(IN_WAV)-15 # reduce volume
    out_Wave = AudioSegment.from_wav(OUT_WAV)-15 # reduce volume
    filtered =  audio_segment.high_pass_filter(3000).low_pass_filter(4000)  # high and low pass filter, to compress the sound.
    filtered = filtered + 10 # boost volume
    filtered = strip_silence(filtered) # strip leading/trailing silence
    combined =  in_Wave + filtered + out_Wave # concatenate
    whiteNoise = generators.WhiteNoise().to_audio_segment(duration=len(combined)) # white noise profile generated
    overlayed = combined.overlay(whiteNoise-25) # overlay white noise, dropping WN volume. 
    overlayed = overlayed + 10 # bump volume of all audio 
    return overlayed

## Converts from MP3 format to OGG for DCS Missions
def convertMP3toOGG(mp3FilenamePath):
    print("Converting "+mp3FilenamePath)
    oggFileNamePath = mp3FilenamePath.replace(".wav",".ogg")
    segment = AudioSegment.from_mp3(mp3FilenamePath) # it's a wave, but this works.
    segment = addLowPassFilter(segment)
    segment.export(oggFileNamePath, format='ogg')
    os.remove(mp3FilenamePath)
    return oggFileNamePath

## Writes speech audio to MP3 format.
def writeSpeechToFile(voiceFileName, voiceText, voiceID, speechEngine):
    speechEngine.setProperty('voice',voiceID)
    username = getpass.getuser()
    print(voiceFileName+" with audio: "+voiceText)
    filePath = "C:\\Users\\"+ username +"\\Desktop\\"+ voiceFileName +".wav"
    speechEngine.save_to_file(voiceText,filePath)
    speechEngine.runAndWait()
    return filePath

## Parses the CSV file argument into a dictionary for text.
def parseLinesFromCSV(csvFilePath):
    lines = {}
    for line in open(csvFilePath,'r').readlines():
        splitParts = line.split(',')
        lines[splitParts[0]]=splitParts[1]
    return lines
    

def enumerateInstalledVoices(speechEngine):
    voices = speechEngine.getProperty('voices')
    print("Currently available System voices:")
    for voice in voices:
        print(voice.id)
    print("You can copy/paste the Voice name from this console view into the code to set the desired voice.")
    input("Press <ENTER> to continue")

class MyArgs:
    pass


if __name__=='__main__':
    givenArgs = MyArgs();
    parser = argparse.ArgumentParser(description="A voice line generator, for generating radio-comms-like audio files for use with the DCS World Mission Editor.")
    parser.add_argument('--file', help="The absolute or relative path to a CSV file with your desired voice lines typed out in the correct format.",
                        type=str,default=argparse.SUPPRESS)
    parser.add_argument('--voice',help='Copy/Pasted value for Voice as displayed by \'--lsvoices\' flag',
                        type=str,default=default_voiceID)
    parser.add_argument('--lsvoices',help='list installed voice IDs',action='store_true')
    
    parser.parse_known_args(sys.argv,namespace=givenArgs)
    print(givenArgs)
    engine = pyttsx3.init()
    if givenArgs.lsvoices == True:
        enumerateInstalledVoices(engine)
    elif givenArgs.file != "" :
        textToOutput = parseLinesFromCSV(givenArgs.file)

        print(textToOutput)
        for audioKey in textToOutput.keys():
            filePath = writeSpeechToFile(audioKey, textToOutput[audioKey], givenArgs.voice, engine);
            oggFile = convertMP3toOGG(filePath)
            print("Created file: "+oggFile)
    
    engine.stop()