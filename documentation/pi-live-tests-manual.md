# Milestone 1 — manual live tests (user only)

These tests involve the real microphone, speaker, and/or a downloaded model.
The developer must not run them on your behalf. Run them yourself on the Pi and
report what you observed.

## 0. Prerequisites

- Confirm the Pi is on and you are logged in as `n01ce`.
- No API key is needed for any test below.
- Replace `hw:1,0` with the USB microphone card/device shown by `arecord -l`.
- Replace `hw:0,0` (or `default`) with the 3.5 mm output shown by `aplay -l`.

## 1. Hardware presence (already in the read-only audit)

```sh
arecord -l
aplay -l
cat /proc/asound/cards
lsusb
```

Expected: one USB PnP Sound Device capture device and one `bcm2835`-style
analog playback device.

## 2. Microphone capture and playback

```sh
arecord -D hw:1,0 -f S16_LE -r 16000 -c 1 -d 3 /tmp/hako-mic-test.wav
aplay -D hw:0,0 /tmp/hako-mic-test.wav
```

Speak while recording. Report: did the file get created, and did playback
reproduce your voice clearly?

## 3. 3.5 mm headphone output

```sh
speaker-test -D hw:0,0 -t sine -f 440 -l 1
```

Report whether a 440 Hz tone is audible in the headphones (not HDMI).

## 4. Offline TTS (after eSpeak NG is installed — requires approval)

```sh
espeak-ng -v en-gb 'HAKO audio test' --stdout > /tmp/hako-tts.wav
aplay -D hw:0,0 /tmp/hako-tts.wav
```

or directly:

```sh
espeak-ng -v en-gb 'HAKO audio test' --stdout | aplay -D hw:0,0 -
```

Report: audible speech, correct output device, no dropouts.

## 5. Vosk import on Python 3.13 (after Vosk is installed — requires approval)

```sh
python3 - <<'PY'
import sys
print(sys.version)
import vosk
print('vosk imported:', getattr(vosk, '__version__', 'unknown'))
PY
```

A crash or `OSError` at import means the wheel/binary path must be fixed before
HAKO can use Vosk.

## 6. Vosk offline recognition (after you download the small model yourself)

```sh
mkdir -p models
curl -L -o /tmp/vosk-model-small-en-us-0.15.zip \
  https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip /tmp/vosk-model-small-en-us-0.15.zip -d models/

python3 - <<'PY'
import wave
from vosk import Model, KaldiRecognizer
w = wave.open('/tmp/hako-mic-test.wav', 'rb')
r = KaldiRecognizer(Model('models/vosk-model-small-en-us-0.15'), w.getframerate())
while True:
    data = w.readframes(4000)
    if not data:
        break
    r.AcceptWaveform(data)
print(r.FinalResult())
PY
```

Report the WAV recording content and the JSON transcription. Recognition must
work entirely offline.

## 7. Feedback check for `/talk`

With the USB mic active and audio playing through the 3.5 mm jack, check
whether the microphone picks up the assistant's own speech. Report whether
you hear echo/retriggering. HAKO will later gate capture during playback or
use push-to-talk if needed.

## 8. Stop / restart behaviour

While a long `arecord` or `speaker-test` process is running, press Ctrl-C and
confirm the audio device is released (no lingering process, next command works
immediately). Report the result.

---

Do not run OpenRouter requests or paste API keys during Milestone 1.
