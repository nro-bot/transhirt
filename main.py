# 12 May 2023
# nrobot

import sys
import argostranslate.package
import argostranslate.translate
import queue
import json

import sounddevice as sd
import wave
from vosk import Model, KaldiRecognizer, SetLogLevel

from_code = "en"
to_code = "es"

def setup_trans():


# Download and install Argos Translate package
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(
            lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
        )
    )
    argostranslate.package.install_from_path(package_to_install.download())

def transl(phrase):
   return argostranslate.translate.translate(phrase, from_code, to_code)

def setup_transcribe():
# You can set log level to -1 to disable debug messages
    SetLogLevel(-1)
    #SetLogLevel(0)

if __name__ == '__main__': 
    setup_trans()
    setup_transcribe()
    '''
    wf = wave.open('test.wav', "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        sys.exit(1)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            print(rec.Result())
        else:
            print(rec.PartialResult())

    print('final result' , rec.FinalResult())
    res = json.loads(result)
    print(res['text'])

    '''
    model = Model(lang="en-us")

    q = queue.Queue()

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))


    device = None
    device_info = sd.query_devices(device, 'input')
    # soundfile expects an int, sounddevice provides a float:
    samplerate = int(device_info['default_samplerate'])

    model = Model(lang="en-us")

    try:
        with sd.RawInputStream(samplerate=samplerate, blocksize = 8000, device=device, dtype='int16',
                               channels=1, callback=callback):
            print('#' * 80)
            print('Press Ctrl+C to stop the recording')
            print('#' * 80)
            print(f'Samplerate: {samplerate}, device: {device}')

            rec = KaldiRecognizer(model, samplerate)
            rec.SetWords(True)
            rec.SetPartialWords(True)

            #translating = False
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    sentence = json.loads(rec.Result())['text']
                    print('\t !------ \n')
                    print('sentence: ', sentence)
                    print('translation: ', transl(sentence))
                    print('listening for input again')
                else:
                    #print('waiting for a full sentence')
                    pass
                    #print('partial result', rec.PartialResult())


    except KeyboardInterrupt:
        print('\nDone')
    except Exception as e:
        print('Exception: ', e)
