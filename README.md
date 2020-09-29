# Open Assistant
Open Assistant is an open-source voice assistant written in python. It's designed to be easily modified and has support for plugins with additional features. This allows developers and manufactures to add custom support for their hardware easily.

Internally, Open Assistant is designed to unpack, process and understand sentences, instead of simply listening for keywords. This allows it to understand a greater variety of sentences, from simple requests "turn on the lights" to complicated sentences like "John's a guy who loves anime and computers, but I hate people". This improves user experience by allowing complicated actions to be performed, like "turn on the lights and the fan" or "remind me to buy milk when I go to the store", requests that don't work as intended on most voice assistants.

## Installation
Install the required packages (see below) then download `apples.py` and `open_assistant_en_us.apc` from here. Run apples.py and it will download every required plugin automatically. Everything 'should' automatically update as well. Currently, a few smart home devices are supported, and must be installed separately. To install them, copy the specified file to the APPLES directory on your local machine and run the command specified to install necessary addons.
* yeelight `yeelight.apm` `pip install yeelight`


### Required Packages
The following is a list of libraries required for open assistant:
```
stanza - Language processing.
pywin32 - WINDOWS ONLY; Special weird windows fixes.
pyttsx3 - Text to speech.
pyaudio - Audio recording and playback.
numpy - Fast number processing.
deepspeech - Speech to text.
pytorch - Machine learning (required for stanza).
tensorflow - Machine learning (required for deepspeech).
```
First you will need to install PyTorch and Tensorflow. These libraries have different installation instructions depending on your system, such as whether you have an NVIDIA GPU or not. The instructions can be found at [https://pytorch.org/](https://pytorch.org/) and [https://www.tensorflow.org/install](https://www.tensorflow.org/install). Once this is done, the rest of the libraries are fairly easy.
If you have python version 3.__6__ or __older__ run the following command in a command line.
```
python -m pip install stanza pywin32 pyttsx3 pyaudio numpy tensorflow deepspeech -U
```
If you have python version 3.__7__ or 3.__8__ run the following command in the command line.
```
python -m pip install stanza pywin32 pyttsx3 numpy tensorflow deepspeech -U
```
You will then have to install pyaudio manually. First download it from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio), then install it with:
```
python -m pip install <downloaded file path>
```
Python 3.8.0 is the most recent tested version at time of writing. Any later versions may or may not work.

## Usage
Press the trigger button or type `trigger` in the terminal to make the system listen for your speech. (CURRENTLY VERY BUGGY)
Alternatively, type `converse` to begin a text based "conversation" with the assistant.
Then just talk with it. Currently sentences with the following verbs will work. Verbs not listed here will probably not work, and could potentially cause a crash.
```
like, dislike, love, hate - as in 'i like minecraft' or 'do i hate mushrooms'
turn, toggle, switch - as in 'turn on the Lights' or 'switch off the fan'
set - as in 'set the lights to green' or 'set the lights to 50 percent'
```
If you find a bug with any of these verbs, please feel free to copy the full program output into an issue so I can figure out what grammar rules have not been accounted for. Alternatively feel free to add any verbs of your own, then submit a pull request for testing.

## How It Works
Behind the scenes, Open Assistant is a collection of plugins, with each plugin handling a discrete task. In general, any request goes through the following plugins/items:
1. Trigger - Starts the request processing system.
2. Audio Recorder - Actually grabs and records the audio to be processed.
3. Speech to Text (STT) - Convert audio data into text to be interpreted.
4. Actions - Unpack the sentence into parts of speech and perform requested actions.
5. Text to Speech (TTS) - Convert response text into audio data to be played back.

Together, these plugins form the "Request Pipeline".
Let's go through these in detail.

### Trigger
The trigger modules are very simple. They provide an interface that will call the STT trigger() function. From there, the speech to text module will handle the request. The trigger's only job is starting the process.

### Audio Recorder
The Audio Recorder has the job of recording audio and passing recorded audio the the STT plugin. The Audio Recorder is abstracted away to allow it to have different implementations depending on hardware. For example, when adding open assistant to a web interface the Audio Recorder plugin would be replaced with a file reader that would grab audio files that were sent to the server by clients.

### Speech to Text (STT)
The STT plugin's job is turning the raw audio data into usable text. It also listens to the Audio Recorder and will determine when a request has been completed so it can stop listening.

### Actions
The Actions plugin is the core of what makes Open Assistant different. The Actions plugin stores an internal list of "Things" which the assistant is capable of understanding. When unpacking a sentence, it aims to understand "what action is being done to what by what". This differs from the traditional keyword approach that just looks for keywords and guesses about what is intended. This allows complicated behaviors to develop from complicated sentences and makes the assistant feel less like a voice activated form filler.

### Text to Speech (TTS)
The Text to Speech plugin finishes handling the request by generating the audio to be heard by the user. In the future, these plugins will be able to either directly play back the audio or send it off to another plugin, allowing for a separate playback plugin. No separate playback plugin has been created as of yet though, so currently the plugin must handle playback internally. The option will stay to allow for the use of internal text to speech systems that can't give raw audio, like screen readers.
