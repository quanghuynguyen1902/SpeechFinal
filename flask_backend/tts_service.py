import numpy as np
from scipy.io.wavfile import write
import sys
sys.path.append('waveglow/')
import torch
from hparams import create_hparams
from model import Tacotron2
from layers import TacotronSTFT, STFT
from audio_processing import griffin_lim
from train import load_model
from text import text_to_sequence
from denoiser import Denoiser
from flask import Flask, request
import re
from unicodedata import normalize
from pydub import AudioSegment
import ffmpy
from flask_cors import CORS

url = 'http://26724b23b50e.ngrok.io/'
sps = 22050
file_name = 'output.mp3'
hparams = create_hparams()
hparams.sampling_rate = 22050

checkpoint_path = "models/checkpoint_8000"

model = load_model(hparams)
model.load_state_dict(torch.load(checkpoint_path)['state_dict'])
_ = model.cuda().eval().half()



waveglow_path = 'models/waveglow_256channels_ljs_v2.pt'
# waveglow_path = 'waveglow_8000'
waveglow = torch.load(waveglow_path)['model']
waveglow.cuda().eval().half()
for k in waveglow.convinv:
    k.float()
denoiser=Denoiser(waveglow)


def tts(text):    
    text = normalize("NFC", text).lower()
    sequence = np.array(text_to_sequence(text, ['basic_cleaners']))[None, :]
    sequence = torch.autograd.Variable(
        torch.from_numpy(sequence)).cuda().long()

    with torch.no_grad():
        mel_outputs, mel_outputs_postnet, _, alignments = model.inference(sequence)
        audio = waveglow.infer(mel_outputs_postnet, sigma=0.666)
    audio_denoised = denoiser(audio, strength=0.005)[:, 0].cpu().numpy()

    return audio_denoised

def pts(para):
    audio = np.zeros((1,0))
    sentence_ls = para.split(".")

    for sen in sentence_ls:
        sub_stn_ls = re.split(",|;|-|:", sen)
        for sub_stn in sub_stn_ls:
            audio = np.append(audio, tts(sub_stn), axis=1)
            audio = np.append(audio, np.zeros((1, int(hparams.sampling_rate/8)), dtype=np.uint8) , axis=1)
        audio = np.append(audio, np.zeros((1, int(hparams.sampling_rate/4)), dtype=np.uint8) , axis=1)
    return audio



app = Flask(__name__)
CORS(app)

@app.route('/tts', methods=['POST'])
def text_to_speech():
	text = request.json['text']
	print(text)
	try:
		audio = pts(text)
		other = '_' + file_name
		write(other, sps, audio.T)
		write(file_name, sps, audio.T)
		# sound = AudioSegment.from_file(file_name)
		sound = AudioSegment(data=audio.astype("float32").tobytes(), sample_width=4, frame_rate=sps, channels=1)
		sound.export(file_name, format="mp3", bitrate="320k")
		audio_url = url + file_name
		return {"status": "OK", "audio": audio_url}
	except:
		return {"status": "Error"}


if __name__ == '__main__':
    app.run(debug=True, port = 5555)