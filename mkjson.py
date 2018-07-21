# vim: set fileencoding=utf-8 :
import json
import base64
import requests
import sox
from pprint import pprint
import logging

sox_to_asterisk = sox.Transformer()
sox_to_flac = sox.Transformer()
sox_to_asterisk.convert(8000)

def recognize():
    sox_to_flac.build('/tmp/test.wav', '/tmp/audio.flac')

    rec_data = {"config": {
        "encoding":"FLAC",
        "languageCode": "pt-BR",
        "speechContexts": {
            "phrases": ['']
        },
        "maxAlternatives": 1
    },
        "audio": {
            "content":""
        }
    }

    with open('/tmp/audio.flac', 'rb') as infile:
        rec_data['audio']['content'] = base64.b64encode(infile.read())

    rec_req = requests.post(
        'https://speech.googleapis.com/v1/speech:recognize?key=AIzaSyAcQSo8DG-J0I_MxxZqCJGTZXKNVPT2kAc',
        json=rec_data)
    logging.debug('Recognized: {}'.format(rec_req.json()))
    return rec_req.json()

def callchat(message):
    chat_data = {
        'type': 'VOICE',
        'phone': '1199999999',
        'body': message,
    }

    logging.debug('Calling chat: {}'.format(chat_data))
    chat_req = requests.post(
        'https://bot-mec.metasix.solutions/detran-pergunta',
        json=chat_data)
    logging.debug('Chat response: {}'.format(chat_req.json()))

    return chat_req.json()

def tts(message):
    tts_data = {
        'input': {
            'text': message,
        },
        'voice': {
            'languageCode': 'pt-BR',
        },
        'audioConfig': {
            'audioEncoding': 'LINEAR16',
        },
    }

    tts_req = requests.post(
        'https://texttospeech.googleapis.com/v1beta1/text:synthesize?key=AIzaSyAcQSo8DG-J0I_MxxZqCJGTZXKNVPT2kAc',
        json=tts_data)

    with open('/tmp/synthret.wav', 'wb') as outfile:
        outfile.write(base64.b64decode(tts_req.json()['audioContent']))

    sox_to_asterisk.build('/tmp/synthret.wav', '/tmp/synth.wav')

def other():

    chat_data = {
        'type': 'VOICE',
        'phone': '1199999999',
        'body': rec_req.json()['results'][0]['alternatives'][0]['transcript'],
    }

    chat_req = requests.post('https://bot-mec.metasix.solutions/detran-pergunta',
                  json=chat_data)

    chat_json = chat_req.json()
    with open('/tmp/op.json', 'w') as jsonoutfile:
        json.dump(chat_json, jsonoutfile)

    tts = ''
    tts += u'Você falou: ' + rec_req.json()['results'][0]['alternatives'][0]['transcript'] + '.\n'

    tts += chat_json[0]['payload']['message'] + '.\n'
    tts += u'Selecione a opção desejada:\n'
    for idx, b in enumerate(chat_json[0]['payload']['buttons']):
        tts += u'Tecle {} seguido de jogo da velha: para {}.\n'.format(idx, b['label'])

    tts_data = {
        'input': {
    #        'text': u'Você falou: ' + rec_req.json()['results'][0]['alternatives'][0]['transcript'] + '?',
    #        'text': u'Faça sua pergunta depois do beep',
            'text': tts,
        },
        'voice': {
            'languageCode': 'pt-BR',
        },
        'audioConfig': {
            'audioEncoding': 'LINEAR16',
        },
    }

    tts_req = requests.post(
        'https://texttospeech.googleapis.com/v1beta1/text:synthesize?key=AIzaSyAcQSo8DG-J0I_MxxZqCJGTZXKNVPT2kAc',
        json=tts_data)

    with open('synth.b64', 'wb') as outfile:
        outfile.write(tts_req.content)

    with open('synth.wav', 'wb') as outfile:
        outfile.write(base64.b64decode(tts_req.json()['audioContent']))
