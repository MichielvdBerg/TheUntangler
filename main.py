import speechToText as stt
import EntityAndSentimentAnalysis as esa
import figureEight as f8
import GUI as gui
import subprocess
import re
import os
import pandas as pd

# """ ###Speech to text part###
# # Retrieve and save the youtube video's from the txt files in the folder VideoData """
# print('Saving video from Youtube')
# stt.saveVideo()

# """ Extract audio from the video's in the Video folder. Audio is extracted in a flac file in the Audio folder """
# print('Extracting audio from video')
# stt.extractAudio()


# """ Use the google speech-to-text with an audio file (for now you have to put the name of the file manualy the googleSpeech funtion)
# # Don't use this method too much with big files for testing, we only have a limited amount of free money
# ### You need to manually give the path in this method ### """
# print('Apply speech to text on extracted audio')
#stt.googleSpeech()

videoPath = "Video/video1.mp4"
transcriptPath = "Transcripts/transcriptaudio1.flac.txt"
newsVideoLink = "9mYVi7WHyiU"

def getTranscriptText():
	transcriptFile = open(transcriptPath, "r")
	text = transcriptFile.read()
	transcriptFile.close()
	return text

def getMLConfidentList(confidentEntityAndSentimentList):
	e = []
	s = []
	for entitysen in newR:
		for entity in confidentEntityAndSentimentList:
			if entitysen['entity'] == entity:
				e.append(entity)
				s.append(entitysen['sentiment'])
	mLConfidentList = pd.DataFrame({"Entity": e, "Sentiment": s})
	return mLConfidentList
	
newR = esa.jsonRosette(getTranscriptText())
newMC = esa.jsonMC(getTranscriptText())
	
""" ### E&S analysis part ###
 Analyse the text with entity and sentiment analysis and return a list of "not sure" entities and "not sure" sentiments 
### List used for entity job ### """
notConfidentEntityList = esa.getListOfDeviantEntitiesAndSentiments(getTranscriptText(), newR, newMC)
print('List of entities which are not confident:')
print(notConfidentEntityList)

""" Analyse the text with entity and sentiment analysis and return a list of confident entities, but not confident sentiment
### List used for sentiment job ### """
confidentEntityList = esa.getListOfConfidentEntitiesButDeviantSentiments(getTranscriptText(), newR, newMC)
print('List of entities which confident, but which sentiments are not:')
print(confidentEntityList)

""" Analyse the text with entity and sentiment analysis and return a list of confident entities and sentiment """
confidentEntityAndSentimentList = esa.getListOfConfidentEntitiesAndConfidentSentiments(getTranscriptText(), newR, newMC)
print('List of entities and sentiments which are confident:')
print(confidentEntityAndSentimentList)

#mLConfidentList = getMLConfidentList(confidentEntityAndSentimentList)

# """ Get the job id's or create the jobs """
job_idList = f8.getJobIdList()

#job_idList = f8.createJobs()
""" Adding data to the jobs """
f8.AddDataSentimentJob(job_idList[0]['SentimentJob id'], confidentEntityList, getTranscriptText(), videoPath, newsVideoLink)
f8.AddDataSentimentJob(job_idList[0]['EntityJob id'], notConfidentEntityList, getTranscriptText(), videoPath, newsVideoLink)
f8.SetupJob(job_idList[0]['SentimentJob id'])
f8.SetupJob(job_idList[0]['EntityJob id'])
f8.LaunchJob(job_idList[0]['SentimentJob id'])
f8.LaunchJob(job_idList[0]['EntityJob id'])



""" Get results """
res_entity_sentim = f8.GetJudgements(job_idList[0]['SentimentJob id'])
res_entity_detect = f8.GetJudgements(job_idList[0]['EntityJob id'])

#print (res_entity_sentim)
gui.makeHtmlFile(res_entity_sentim, mLConfidentList)