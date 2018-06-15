import argparse
import json
import os
import tempfile
import requests

import EntityAndSentimentAnalysis as esa

import pickle

figure_eight_api_key=" "

def CreateEntityJob():	
	job_title= "Entity recognition"
	instructions="""
	<h1>Overview</h1>
	<p> You will be asked to watch a 30-seconds extract of video. You will see and hear people talking. Then, you will have to report if the expression indicated below the video and underlined is actually said in the video.</p>
	<hr>
	<h1>Steps</h1>
	<p>1. Read the underlined expression above the video.</p>
	<p>2. Watch the video.</p>
	<p>3. Report is the expression is said in the video.</p>
	<p>4. If the expression was not said in the video, provide what you think is the closest match for the expression. If there is none, leave the field blank. </p>
	<hr>
	<h1>Rules &amp; Tips</h1>
	<p>Try to stay alert and be sure you understand the video clearly. </p>
	"""

	request_url = "https://api.figure-eight.com/v1/jobs.json"
	headers = {'content-type': 'application/json'}

	cml="""
	<h1>Video to watch and expression to verify</h1>
	<p> Check if the expression <u>{{entity}}</u> is present in the following extract of video. </p>
	<iframe width=\"420\" height=\"315\" src=\"{{video_url}}"></iframe>
	<cml:radios validates="required" name="entity_detected" label="Was the expression said in the video?">
		<cml:radio label="Yes" value="yes" />
		<cml:radio label="No" value="no" />
	</cml:radios>"""

	cml += """<cml:text only-if="entity_detected:[yes]" 
	label="If it was not in the video, what expression that you have heard would be the closest you would find? 
	If there is none, leave the field blank." 
	default="..." />
	"""

	payload = {
		'key': figure_eight_api_key,
		'job':{
			'title': job_title,
			'instructions': instructions,
			'cml': cml
		}

	}

	response=requests.post(request_url, data=json.dumps(payload), headers=headers)
	job_id = response.json()['id']
	
	#print(job_id)
	return job_id

def CreateEntitySentimentJob():
	
	job_title= "Entity-Sentiment recognition"
	instructions="""
	<h1>Overview</h1>
	<p> You will be asked to watch a 30-seconds extract of video. You will see and hear people talking. On top of the video, there is an underlined expression that you should notice in the video. Your task is to rate the expression used in the video on
		a scale of sentiment.</p>
	<hr>
	<h1>Steps</h1>
	<p>1. Read the sentence.</p>
	<p>2. Identify the place of the highlighted word in the sentence.</p>
	<p>3. Imagine how the person saying this word in the sentence would feel about this word.</p>
	<p>4. Report the sentiment you associate with the underlined word on the scale from \"very negative\" to \"very positive\".</p>
	<hr>
	<h1>Examples</h1>
	<p>\"We can't reach our <u>goal</u>, it's too difficult.\"
		<p>One can identify sadness, but it doesn't seem absolutely awful.
			<br>Slightly negative</p>
		<p>\"Will this be our last chance to save <u>net neutrality</u>?\"
			<p>It seems like the sentiment behind is urgeness, and the speaker seems to make a great deal of the notion. It seems extremely important and valuable to them.
				<br>Very positive</p>
		<p>\"The meeting between Kim Jung-Un and <u>Donald Trump</u> is scheduled for next Tuesday.\"
			<p>Here it seems like there is only a simple fact without much addition to it.
				<br>Neutral</p>
	<hr>
	<h1>Rules &amp; Tips</h1>
	<p>Try to imagine what the person is thinking. Would they think it is a wonderful statement?, or a horrible one?</p>

	"""

	request_url = "https://api.figure-eight.com/v1/jobs.json"
	headers = {'content-type': 'application/json'}

	cml="""
	<h1>Video to watch and expression to rate</h1>
	<p> Rate the sentiment associated with the expression <u>{{entity}}</u> in the following extract of video. </p>
	<iframe width=\"420\" height=\"315\" src=\"{{video_url}}"></iframe>
	<cml:ratings validates="required" label="Rate the sentiment associated with the expression: {{entity}}:" class="horizontal" points="5">
	<cml:rating label="Very Negative" />
	<cml:rating label="Slightly Negative" />
	<cml:rating label="Neutral" />
	<cml:rating label="Slightly Positive" />
	<cml:rating label="Very Positive" />
	</cml:ratings>

	"""

	payload = {
		'key': figure_eight_api_key,
		'job':{
			'title': job_title,
			'instructions': instructions,
			'cml': cml
		}

	}

	response=requests.post(request_url, data=json.dumps(payload), headers=headers)
	job_id = response.json()['id']
	
	#print(job_id)
	return job_id
	
def createJobs():
	job_id_entityjob = CreateEntityJob()
	job_id_sentimentjob = CreateEntitySentimentJob()

	job_id = [{'EntityJob id': job_id_entityjob, 'SentimentJob id': job_id_sentimentjob}]
	print(job_id)
	with open('job_idList.txt', 'wb') as fp:
		pickle.dump(job_id, fp)
	return job_id

def getJobIdList():
	# with open('job_idList.txt', 'wb') as fp:
		# if not fp:		
			# pickle.dump("no jobs", fp)
			# print("no jobs")
			# return file
		# else:
			# job_id = pickle.load(fp)
			# return job_id
	with open ('job_idList.txt', 'rb') as fp:
		job_id = pickle.load(fp)
		return job_id
		
def AddData(job_id, video_id, entity_to_verify, time_start, time_stop):
	## Adds some data in the task. (needed)

	request_url = "https://api.figure-eight.com/v1/jobs/{}/units.json".format(job_id)
	headers = {'content-type': 'application/json'}

	video_url = "https://www.youtube.com/embed/"+video_id+"?version=3&start="+str(time_start)+"&end="+str(time_stop)+"&rel=0&controls=0&cc_load_policy=1&disablekb=1"

	data = {'video_url': video_url, 'entity': entity_to_verify,}
	payload = {
		'key': figure_eight_api_key,
			'unit': {
			'data': data
		}
	}

	response = requests.post(request_url, data=json.dumps(payload), headers=headers)
	return response.json
	#print response.json()
	#unit_id = response.json()['id']
	#print unit_id

def AddDataSentimentJob(job_idSentiment, confidentEntityList, text, videoPath, newsVideoLink):
	positions = []

	for entity in confidentEntityList: 
		new_item =  {'entity': entity, 'position': esa.findEntityPlacement(entity, text)}
		positions.append(new_item)

	duration_seconds = esa.getVideoLength(videoPath)
	
	for entity in positions:
		for position in entity['position']:
			[tstart, tstop] = esa.find_entity_in_video(position, text, duration_seconds)
			AddData(job_idSentiment, newsVideoLink, entity['entity'], tstart, tstop)

def AddDataEntityJob(job_idSentiment, confidentEntityList, text, videoPath, newsVideoLink):
	positions = []

	for entity in confidentEntityList: 
		new_item =  {'entity': entity, 'position': esa.findEntityPlacement(entity, text)}
		positions.append(new_item)

	duration_seconds = esa.getVideoLength(videoPath)
	
	for entity in positions:
		for position in entity['position']:
			[tstart, tstop] = esa.find_entity_in_video(position, text, duration_seconds)
			AddData(job_idSentiment, newsVideoLink, entity['entity'], tstart, tstop)

def SetupJob(job_id):
	#strin = "curl -X PUT --data-urlencode job[options][req_ttl_in_seconds]="+str(300)+ "https://api.figure-eight.com/v1/jobs/"+str(job_id)+".json?key="+str(figure_eight_api_key)
	#res = subprocess.Popen(strin)

	request_url = "https://api.figure-eight.com/v1/jobs/{}.json".format(job_id)
	headers = {'content-type': 'application/json'}
	payload = {
		'job': {'options':{'req_ttl_in_seconds':300}},
		'key': figure_eight_api_key
		}
	response = requests.put(request_url, data=json.dumps(payload), headers=headers)
	return response.json()

def LaunchJob(job_id):
	# launch internally: CURL command
	# curl -X POST -d "channels[0]=cf_internal&debit[units_count]={100}" https://api.figure-eight.com/v1/jobs/{job_id}/orders.json?key={api_key}
	request_url = "https://api.figure-eight.com/v1/jobs/{}/orders.json".format(job_id)
	headers = {'content-type': 'application/json'}
	
	payload = {
		'channels':{
			'0': 'cf_internal'},
		'debit': {
			'units_count':'100'},
		'key': figure_eight_api_key
	}

	response = requests.post(request_url, data=json.dumps(payload), headers=headers)
	return response.json()

def GetJudgements(job_id):
	#curl -X GET "https://api.figure-eight.com/v1/jobs/{job_id}/judgments.json?key={api_key}&page={1}"
	request_url = "https://api.figure-eight.com/v1/jobs/{}/judgments.json".format(job_id)
	headers = {'content-type': 'application/json'}
	payload = {
		'key': figure_eight_api_key
		}
	response = requests.get(request_url, data=json.dumps(payload), headers=headers)
	return response.json()
