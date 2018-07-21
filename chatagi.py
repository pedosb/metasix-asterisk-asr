#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import asterisk.agi
import logging
import sys

import mkjson

logging.basicConfig(level=logging.DEBUG, filename='/tmp/chatagi.log')

agi = asterisk.agi.AGI(stderr=open('/tmp/chatagi.stderr', 'w'))

def exit():
    say('Tchau!')
    agi.hangup()
    sys.exit(0)

def say(message, read_dtmf=False):
    mkjson.tts(message)
    if read_dtmf:
        agi.appexec('Read', 'OI,/tmp/synth,1')
        try:
            return int(agi.get_variable('OI'))
        except ValueError:
            return None
    else:
        agi.appexec('Playback', '/tmp/synth')

def listen_and_respond():
    agi.appexec('Record', '/tmp/test.wav,3,60')
    rec_json = mkjson.recognize()

    if not 'results' in rec_json:
        exit()

    chat_json = mkjson.callchat(
        rec_json['results'][0]['alternatives'][0]['transcript'])

    proccess_chat(chat_json)

def proccess_chat(chat_json):
    chat_text = ''
    options = []
    for res in chat_json:
        chat_text += res['payload']['message'] + '.\n'
        if len(res['payload']['buttons']) > 0:
            chat_text += u'Selecione a opção desejada:\n'
            for b in res['payload']['buttons']:
                options.append(b['value'])
                chat_text += u'Tecle {} seguido de jogo da velha: para {}.\n'.format(len(options)-1, b['label'])

    dtmf = say(chat_text, len(options) > 0)
    if len(options) > 0 and dtmf is None:
        listen_and_respond()
        #exit()
    elif len(options) > 0 and dtmf is not None:
        try:
            chat_json = mkjson.callchat(options[dtmf])
            proccess_chat(chat_json)
        except KeyError:
            exit()
    elif len(options) == 0:
        listen_and_respond()

logging.info('going to playback')
oi=agi.get_variable('CALLERID(num)')
oi2=agi.get_variable('psbincallerid')
logging.error('var {} {}'.format(oi, oi2))
mkjson.callchat('/Start')
#agi.appexec('Playback', '/home/metasix/asterisk-asr/facasuaperg')
say('Olá, em que posso te ajudar?')
listen_and_respond()
