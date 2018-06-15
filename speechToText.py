import os
import io
import google.auth.transport.requests
import subprocess
import math
from pytube import YouTube
from pytube import Playlist
from os import listdir
from os.path import isfile, join
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.auth.transport import requests

import EntityAndSentimentAnalysis as esa

# Save the Youtube files
def saveVideo():
	import codecs
	datapath = 'C:/Users/Michiel/Documents/Crowd Computing/VideoData/'
	videotxts = [f for f in listdir(datapath) if isfile(join(datapath, f))]
	videocount = 1
	os.chdir("Video")
	for i in range(0,len(videotxts)):
		with open(datapath + videotxts[i], 'r') as f:
			
			for line in f:
				yt = YouTube(line) 
				videoname = 'video' + str(videocount)
				print (videoname)
				yt.streams.filter(subtype='mp4',res='360p').first().download(filename=videoname)
				videocount = videocount + 1
				
def extractAudio():
	path = 'C:/Users/Michiel/Documents/Crowd Computing/Video'
	videos = [f for f in listdir(path) if isfile(join(path, f))]
	videocount = len([name for name in os.listdir(path)])
	print(videocount)
	print(os.getcwd())
	os.chdir("..")
	for i in range(1,videocount + 1):
		command_video_audio = 'ffmpeg -i Video/video' + str(i) + '.mp4 Audio/audio' + str(i) + '.mp3'		
		print(command_video_audio)
		os.system(command_video_audio)
		command_audio_split = 'ffmpeg -i Audio/audio' + str(i) + '.mp3 -f segment -segment_time 50 -c copy Audio/audio' + str(i) + '_out%03d.mp3'
		print(command_audio_split)
		os.system(command_audio_split)
		for j in range(0, 1 + math.ceil(esa.getVideoLength('Audio/audio' + str(i) + '.mp3') / 60)):
			command_audio_audio = 'ffmpeg -i Audio/audio' + str(i) + '_out00' + str(j) + '.mp3 -ac 1 Audio/audio' + str(i) + '_out00' + str(j) + '.flac'
			print(command_audio_audio)
			os.system(command_audio_audio)
			
def googleSpeech():
	#now upload to google speech
	os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="Crowd Computing-ffea40c14587.json"
	path = 'C:/Users/Michiel/Documents/Crowd Computing'
	
	outputName = "audio1.flac"
	
	for i in range(0, math.ceil(esa.getVideoLength('Audio/audio1.mp3') / 60)):
		audioFileName = "audio1_out00" + str(i) + ".flac"
		audio_path = path + "/Audio/" + audioFileName
		print (audioFileName)
		with open(path + '/SpeechAPI.txt') as f:
			Aapie = f.read()
			
			# Instantiates a client
			client = speech.SpeechClient()
		
			# Loads the audio into memory
			print(audio_path)
			with io.open(audio_path, 'rb') as audio_file:
				content = audio_file.read()
				audio = types.RecognitionAudio(content=content)
		
			config = types.RecognitionConfig(
			   encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
			   sample_rate_hertz=44100,
			   language_code='en-US')
		
			# Detects speech in the audio file
			response = client.recognize(config, audio)
			
			transcriptFile = open("Transcripts/transcript" + outputName + ".txt","a") 
			for result in response.results:
				transcriptFile.write(result.alternatives[0].transcript)
				print('Transcript: {}'.format(result.alternatives[0].transcript))
			transcriptFile.close()

#saveVideo()
#extractAudio()
#googleSpeech()

