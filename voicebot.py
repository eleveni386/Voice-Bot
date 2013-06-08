#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   eleven.i386
#   E-mail  :   eleven.i386@gmail.com
#   WebSite :   eleveni386.7axu.com
#   Date    :   13/06/03 21:21:42
#   Desc    :   语音控制
#
import pyaudio
import urllib2
import wave
import os
import jieba
import sqlite3

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "output.wav"
FLAC_OUTPUT_FILENAME = "output.flc"

p = pyaudio.PyAudio()
sql = sqlite3.connect("./voicebot.db")
sql_cur = sql.cursor()

def search_and_cmd(keywd):
    grep = lambda x, y: x in y and x
    print "请稍等,正在分析你的指令..."
    sql_cur.execute("select question, command from voicebot where question = '%s'"%(keywd))
    result = sql_cur.fetchall()[0]
    print result
    print "你的指令是:", ','.join(jieba.cut(keywd))
    cmd = [ grep(i, result) for i in jieba.cut(keywd) ]
    if len(cmd) > 0:
        for i in cmd:
            print i
            if i: os.popen(result[1]);print "已经完成你的指令"
    else:print "我无法理解你的指令,或者数据库内没有这个指令的记录"

def VoicetoString(upfile):
    url = 'http://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=zh-CN'
    audio = open(upfile,'rb').read()
    headers = {'Content-Type' : 'audio/x-flac; rate=%s'%RATE}
    req = urllib2.Request(url, audio, headers)
    response = urllib2.urlopen(req)
    a = eval(response.read())
    try:
        #print a['hypotheses'][0]['utterance']
        return a['hypotheses'][0]['utterance']
    except:
        print "我不知道你说什么!"
        return None

def save_wave_file(filename, data):
    wf = wave.open(filename,"wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(''.join(data))
    wf.close()

def wavtoflac(inputfile,outputfile):
    cmd = 'flac %s -f -o %s'%(inputfile,outputfile)
    os.popen(cmd)
    return outputfile

def player(filename):

    fp = wave.open(filename,'rb')
    stream = p.open(format = p.get_format_from_width(fp.getsampwidth()),\
                    channels = fp.getnchannels(),\
                    rate = fp.getframerate(),\
                    output = True)
    data = fp.readframes(CHUNK)
    while data != '':
        stream.write(data)
        data = fp.readframes(CHUNK)
    stream.stop_stream()
    stream.close()

def record():

    frames = []
    print "开始录音,你请说..."
    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)


    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        frames.append(stream.read(CHUNK))

    stream.stop_stream()
    stream.close()
    save_wave_file(WAVE_OUTPUT_FILENAME,frames)

    print("录音完毕,正在分析你说的什么意思..")
    #player(WAVE_OUTPUT_FILENAME)
    return VoicetoString(wavtoflac(WAVE_OUTPUT_FILENAME,FLAC_OUTPUT_FILENAME))


#while 1:
search_and_cmd(record())
p.terminate()
os.remove("output.wav")
os.remove("output.flc")
