import pandas as pd
import figureEight as f8
from IPython.display import display, HTML
from IPython.display import Image,display
from IPython.core.display import HTML 
import ipywidgets as widgets

def convert_more(l):

	ent = []
	sen = []
	for unit in l:
		sentiment = l[unit]['rate_the_sentiment_associated_with_the_expression_entity']['avg']
		# Do some more advanced stuff here
		if sentiment > 0:
			s = 'pos'
		elif sentiment < 0:
			s = 'neg'
		else:
			s = 'neu'
		ent.append(l[unit]['entity'])
		sen.append(s)	

	df = pd.DataFrame({"Entity": ent, "Sentiment": sen})
	#print(df)
	return df

def pos(s):
	is_pos = s == 'pos'
	return ['background-color: green' if v else '' for v in is_pos]

def neg(s):
	is_neg = s == 'neg'
	return ['background-color: red' if v else '' for v in is_neg]
	
def makeHtmlFile(f8Response, mLConfidentList):
	b = convert_more(f8Response)
	print(b)
	print(mLConfidentList)
	frames = [b, mLConfidentList]
	result = pd.concat(frames)
	result.reset_index(drop=True, inplace=True)
	print (result)

	d = {"1": "a", "2": "b"}
	dropdown = '\n<select name="mymenu">\n	<option value="1">BBC</option>\n	<option value="2">CNN</option>\n 	<option value="3">Fox</option>\n</select>\n'
	htmlString = HTML('<h1>How Biased is News</h1>' + dropdown + result.style.apply(pos).apply(neg).render()).data

	htmlFile = open("filename.html","w")
	htmlFile.write(htmlString)
	htmlFile.close()


# import webbrowser, os
# webbrowser.open('file://' + os.path.realpath('filename.html'))
