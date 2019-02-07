from pyaudio import PyAudio, paInt16
import wave
import pygame


def get_language():
    language = input("Please select your native language from the following options: Italian or Polish ").title()
    languages = ['Polish', 'Italian']
    while True:
        if language in languages:
            break
        else:
            print("That is not currently a option in our program, please enter the options provided")
            language = input(
                "Please select your native language from the following options: Italian or Polish\n ").title()
    return language

# TODO Create Activity 2
# TODO Create Activity 3


def record_audio():
    FORMAT = paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "user_audio.wav"

    audio = PyAudio()

    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("recording...")
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("finished recording")

    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    return WAVE_OUTPUT_FILENAME


def play_sound(sound):


    # define stream chunk
    chunk = 1024

    # open a wav format music
    f = wave.open(r"%s" % sound, "rb")
    # instantiate PyAudio
    p = PyAudio()
    # open stream
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(),
                    rate=f.getframerate(),
                    output=True)
    # read data
    data = f.readframes(chunk)

    # play stream
    while data:
        stream.write(data)
        data = f.readframes(chunk)

        # stop stream
    stream.stop_stream()
    stream.close()

    # close PyAudio
    p.terminate()


def record_audio_and_play():
    sound = record_audio()
    play_sound(sound)


def play_mp3(file):
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()





#loop each item in words.keys
#each time the frame needs to be reset
#how to skip the loop with continue command