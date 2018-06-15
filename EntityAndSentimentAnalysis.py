import argparse
import json
import os
import subprocess
import re
import tempfile
import meaningcloud
from rosette.api import API, DocumentParameters, RosetteException

def jsonRosette(text):	
	jsonR = runRosette(text)
	newR = newRjson(jsonR)
	return newR
	
def jsonMC(text):
	jsonMC = runMeaningCloud(text)
	newMC = newMCjson(jsonMC)
	return newMC

def runRosette(text, key, alt_url='https://api.rosette.com/rest/v1/'):
	""" Run the example """
	# Create default file to read from
	temp_file = tempfile.NamedTemporaryFile(suffix=".html")
	sentiment_file_data = "<html><head><title></title></head><body><p>" + text + "</p></body></html>"
	message = sentiment_file_data
	temp_file.write(message if isinstance(message, bytes) else message.encode())
	temp_file.seek(0)

	# Create an API instance
	api = API(user_key=key, service_url=alt_url)

	params = DocumentParameters()
	params["language"] = "eng"
	params["content"] = text

	# Use an HTML file to load data instead of a string
	#params.load_document_file(temp_file.name)
	try:
		result = api.sentiment(params)
		#print (result)
	except RosetteException as exception:
		print(exception)
	finally:
		# Clean up the file
		temp_file.close()

	return result

def runMeaningCloud(text, license_key):
	try:
		sentiment_response = meaningcloud.SentimentResponse(meaningcloud.SentimentRequest(license_key, lang='en', txt=text, txtf='plain').sendReq())
		# If there are no errors in the request, we print the output
		if (sentiment_response.isSuccessful()):
			#print("\nThe request to 'Sentiment Extraction' finished successfully!\n")
			sentiments =  sentiment_response.getResults()
			if (sentiments):
				return sentiments
		
			else:
				print("\nOh no! There was the following error: " + topics_response.getStatusMsg() + "\n")
		else:
			if(sentiment_response.getResponse() is None):
				print("\nOh no! The request sent did not return a Json\n")
			else:
				print("\nOh no! There was the following error: " + topics_response.getStatusMsg() + "\n")
	
	except ValueError:
		e = sys.exc_info()[0]
		print("\nException: " + str(e))

def newMCjson(json):
	newjson = []
	for sent_concept in json['sentimented_concept_list']:
		if sent_concept['score_tag'] == 'P' or sent_concept['score_tag'] == 'P+':
			newTag = 'pos'
		elif sent_concept['score_tag'] == 'N' or sent_concept['score_tag'] == 'N+':
			newTag = 'neg'
		elif sent_concept['score_tag'] == 'NEU':
			newTag = 'neu'
		elif sent_concept['score_tag'] == 'NONE':
			newTag = 'NONE'
		else: 
			newTag = ''
		newItem = {'entity': sent_concept['form'], 'sentiment': newTag, 'confidence': ''}
		newjson.append(newItem)
	for sent_entity in json['sentimented_entity_list']:
		if sent_entity['score_tag'] == 'P' or sent_entity['score_tag'] == 'P+':
			newTag = 'pos'
		elif sent_entity['score_tag'] == 'N' or sent_entity['score_tag'] == 'N+':
			newTag = 'neg'
		elif sent_entity['score_tag'] == 'NEU':
			newTag = 'neu'
		elif sent_entity['score_tag'] == 'NONE':
			newTag = 'NONE'
		else: 
			newTag = ''
		newItem = {'entity': sent_entity['form'], 'sentiment': newTag, 'confidence': ''}
		newjson.append(newItem)
	return newjson
	
def newRjson(json):
	newjson = []
	for entity in json['entities']:
		newItem = {'entity': entity['mention'], 'sentiment': entity['sentiment']['label'], 'confidence': entity['sentiment']['confidence']}
		newjson.append(newItem)
	return newjson

def findEntityPlacement(entity, text):
	start_positions = []
	position = -1

	while True:
		position = text.find(entity, position+1)
		#print position
		if position is -1:
			#print("return")
			return start_positions
		else: 
			start_positions.append(position)
			#print("append")

def find_entity_in_video(entity_placement, text, length_video):
	length_text = len(text)
	percentage = float(entity_placement)/float(length_text)
	#print("percentage: ", percentage)
	middle_of_clip = length_video*percentage

	start = middle_of_clip - 15
	if start < 0:
		start = 0
	stop = middle_of_clip + 15
	if stop > length_video:
		stop = length_video
	
	return int(start), int(stop)

def compareDeviantEntities(jsonR, jsonMC):
	entityListR = []
	for item in jsonR:
		entity = item["entity"]
		entityListR.append(entity) 
		#print entityListR

	entityListMC = []
	for item in jsonMC:
		entity = item["entity"]
		entityListMC.append(entity)  
		#print entityListMC

	intersectionList = set(entityListR).intersection(entityListMC)
	#print intersectionList

	differenceListRfromMC = set(entityListR).difference(entityListMC)
	#print differenceListRfromMC

	differenceListMCfromR = set(entityListMC).difference(entityListR)
	#print differenceListMCfromR

	return list(differenceListRfromMC.union(differenceListMCfromR))

def remove_duplicates(values):
	output = []
	seen = set()
	for value in values:
		if value not in seen:
			output.append(value)
			seen.add(value)
	return output

def compareDeviantSentiments(jsonR, jsonMC):
	entities = []
	for entityR in jsonR:  
		for entityMC in jsonMC:
			if entityR['entity'] == entityMC['entity']: 
			#print("Match: " + entityR['entity'])
				if entityR['sentiment'] != entityMC['sentiment']:
					entities.append(entityR['entity'])
					#print(entityR['entity'] + ": Sentiments do not match")
				elif (entityR['entity'] == entityMC['entity']) & (entityR['confidence'] < 0.6):
					entities.append(entityR['entity'])
					#print(entityR['entity'] + ": Confidence is less than 0.6")
				#else:
					#print("OK: " + entityR['entity'])

	entities = remove_duplicates(entities)

	return entities
	
def compareConfidentEntities(jsonR, jsonMC):
	entityListR = []
	for item in jsonR:
		entity = item["entity"]
		entityListR.append(entity) 
		#print entityListR

	entityListMC = []
	for item in jsonMC:
		entity = item["entity"]
		entityListMC.append(entity)  
		#print entityListMC

	return set(entityListR).intersection(entityListMC)

def compareConfidentSentiments(jsonR, jsonMC):
	entities = []
	for entityR in jsonR:  
		for entityMC in jsonMC:
			if entityR['entity'] == entityMC['entity']: 
			#print("Match: " + entityR['entity'])
				if entityR['sentiment'] == entityMC['sentiment']:
					#if entityR['confidence'] > 0.6:
					entities.append(entityR['entity'])
						#print(entityR['entity'] + ": Sentiments do match")
				#else:
					#print("No match")

	entities = remove_duplicates(entities)

	return entities


def getListOfDeviantEntitiesAndSentiments(text, newR, newMC):

	ce = compareDeviantEntities(newR, newMC)
	cs = compareDeviantSentiments(newR, newMC)
	result = ce + cs
	
	return result

def getListOfConfidentEntitiesButDeviantSentiments(text, newR, newMC):
	
	cs = compareDeviantSentiments(newR, newMC)

	return cs

def getListOfConfidentEntitiesAndConfidentSentiments(text, newR, newMC):
	cs = compareConfidentSentiments(newR, newMC)
	
	return cs	

def getVideoLength(filePath):
	process = subprocess.Popen(['ffmpeg',  '-i', filePath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	stdout, stderr = process.communicate()
	matches = re.search(b"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),", stdout, re.DOTALL).groupdict()
	#print process.pid
	process.kill()
	duration = float(matches['seconds']) + 60 * float(matches['minutes']) + 3600 * float(matches['hours'])
	return duration
