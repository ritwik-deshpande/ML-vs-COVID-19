import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import re
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB 
from sklearn import metrics
from sklearn import preprocessing
from flask import Flask,render_template
from datetime import date,datetime
import pickle


encodings = dict()
def getSymptomCategory(symptoms):
	index = {
	    'suspect':['fever','cold','flu','dizzyness','strong headache','dehydration'],
	    'high_risk':['dry cough','breathlessness','high fever']
	}


	for word in symptoms.strip(',').split(','):
		word = word.lower()
		if word in index['suspect']:
			return 'Suspect'
		elif word in index['high_risk']:
			return 'High_risk'
	return 'Safe'

def getNotesCategory(notes):
	index = {
	    "suspect":['mumbai','delhi','mh','up','maharastra','kerala','chennai','patient'],
	    "high_risk":['airport','foreign','confirmed','dubai','iran','bahrain','us','covid','wuhan','china','uae','kenya','italy','spain','positive','hospital','saudi','thailand','usa','france','germany','uk','london','qatar','paris','lanka','middle','east','hospital','admitted','turkey','mecca','mexico','japan','indonesian','indonesia','philippines','singapore'],
	}

	for word in notes.strip().split():
		word = word.lower().strip(',')
		if word in index['suspect']:
			return 'suspect'
		elif word in index['high_risk']:
			return 'high_risk'
		else:
			rexp = re.compile(r"P[0-9]+$")
			if rexp.search(word):
				return 'suspect'

	return 'safe'



def encode(df):

	le = preprocessing.LabelEncoder()
	global encodings
	#encodings = dict()

	df['gender'] = le.fit_transform(df['gender'])
	gender_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
	encodings['gender'] = gender_mapping

	df['notes_category'] = le.fit_transform(df['notes_category'])
	notes_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
	encodings['notes'] = notes_mapping

	df['Symptoms_category'] = le.fit_transform(df['Symptoms_category'])
	symptom_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
	encodings['symptoms'] = symptom_mapping

	df['detected_state'] = le.fit_transform(df['detected_state'])
	state_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
	encodings['state'] = state_mapping

	print(encodings)
	print(df.head())
	return


def trainModel():

	global encodings
	df = pd.read_csv('Dataset/dataset.csv')
	df = df.drop(['Symptoms','notes','current_status'], axis = 1)
	df = df[df.days_to_change >= 0]
	
	encode(df)

	

	X = df.loc[:,'gender':'Symptoms_category']
	y = df['category'] 


	# splitting X and y into training and testing sets 
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1) 
	  
	# training the model on training set 
	mnb = MultinomialNB() 
	mnb.fit(X_train, y_train) 
	  
	# making predictions on the testing set 
	print(X_test.shape)

	y_pred = mnb.predict(X_test) 
	  
	# comparing actual response values (y_test) with predicted response values (y_pred) 
	print("Gaussian Naive Bayes model accuracy(in %):", metrics.accuracy_score(y_test, y_pred)*100)

	
	# save the classifier
	with open('my_dumped_classifier.pkl', 'wb') as fid:

		pickle.dump(mnb, fid)

	return


    
def predict(gender,age,notes,detected_state,symptoms,diagnosed_date):


	#fetch the saved trained model from the pickel file
	global encodings
	with open('my_dumped_classifier.pkl', 'rb') as fid:
		mnb = pickle.load(fid)

	current_time = datetime.now()

	current_date = date(current_time.year,current_time.month,current_time.day)


	diagnosed_time = diagnosed_date.split('/')
	diagnosed_date = date(int(diagnosed_time[2]),int(diagnosed_time[1]),int(diagnosed_time[0]))

	age = int(age)//10

	days_to_change = (current_date - diagnosed_date).days//5
	test = [[encodings['gender'][gender], encodings['state'][detected_state],age,days_to_change,encodings['notes'][getNotesCategory(notes)],encodings['symptoms'][getSymptomCategory(symptoms)]]]
	print(test)
	print(mnb.predict(test))

	return mnb.predict(test)
