import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB 
from sklearn import metrics
from sklearn import preprocessing
import re
from random import random

def assignCat(row) :
    
    if row['days_to_change'] > 2 and row['current_status'] == "Recovered" : 
        return 2
    elif row['current_status'] == "Deceased":
        return 1
    else :
        return 3

if __name__ == '__main__':
	pop_df = pd.read_csv('population_india_census2011.csv')
	pop_df = pop_df.rename(columns = {"State / Union Territory": "detected_state"})

	individual_df = pd.read_csv('IndividualDetails.csv')
	individual_df["age"] = individual_df['age'].fillna(24)
	#individual_df['age'] = individual_df['age'].astype(str)
	#individual_df['age'] = individual_df['age'].apply(lambda x : 24 if x=="nan" else x)
	individual_df['age'] = individual_df['age'].apply(pd.to_numeric) 
	individual_df = individual_df.assign(age_group = individual_df['age']//10)

	individual_df['gender'] = individual_df['gender'].astype(str)
	individual_df['gender'] = individual_df['gender'].apply(lambda x : "M" if x=="nan" else x)



	individual_df['diagnosed_date'] = pd.to_datetime(individual_df['diagnosed_date'],dayfirst=True)
	individual_df['status_change_date'] = pd.to_datetime(individual_df['status_change_date'], dayfirst=True)
	individual_df = individual_df.assign(days_to_change = individual_df['status_change_date'] - individual_df['diagnosed_date'])
	individual_df["days_to_change"]= individual_df["days_to_change"].apply(lambda x : x.days//5)
	individual_df["days_to_change"] =  individual_df["days_to_change"].fillna(0)

	df = pd.merge(individual_df, pop_df[['detected_state','Density']], how='inner', on='detected_state')

	df = df.drop(['government_id','detected_district','nationality','age','id','Density',
              'government_id','Unnamed: 12','status_change_date','diagnosed_date','detected_city'], axis = 1)
	df.head()
	df.dtypes

	df['category'] = df.apply(lambda row : assignCat(row), axis = 1) 
	df.head()


	df['notes_category'] =  df['notes']
	index = {
	    "suspect":['mumbai','delhi','mh','up','maharastra','kerala','chennai','patient'],
	    "high_risk":['airport','foreign','confirmed','dubai','iran','bahrain','us','covid','wuhan','china','uae','kenya','italy','spain','positive','hospital','saudi','thailand','usa','france','germany','uk','london','qatar','paris','lanka','middle','east','hospital','admitted','turkey','mecca','mexico','japan','indonesian','indonesia','philippines','singapore'],
	}

	for i,note in enumerate(df['notes'].astype('str')):
		df['notes_category'][i] = 'safe'
		words = note.strip().split(' ')
		for word in words:
			word = word.strip(',').lower()
			if word in index['suspect']:
				df['notes_category'][i] = 'suspect'
				break
			elif word in index['high_risk']:
				df['notes_category'][i] = 'high_risk'
				break
			else:
				rexp = re.compile(r"P[0-9]+$")
				if rexp.search(word):
					df['notes_category'][i] = 'suspect'
					break


	print(df.head())

	df['Symptoms'] = df['category']
	df['Symptoms_category'] = df['category']

	index = {
	    'suspect':['mild fever','cold','flu','dizzyness','strong headache','dehydration'],
	    'high_risk':['dry cough','breathlessness','high fever']
	}

	

	for i,symptom in enumerate(df['Symptoms']):
		if df['category'][i] == 1:
			df['Symptoms_category'][i] = 'High_risk'
			no_of_symptoms = int(random()*100%4)
			symptoms = ''
			for j in range(0,no_of_symptoms):
				symptoms = symptoms + index['high_risk'][j] + ','
			    
			symptoms = symptoms[:-1]
			df['Symptoms'][i] = symptoms

		elif df['category'][i] == 2:
	    	df['Symptoms_category'] = 'Suspect'
	    	no_of_symptoms = int(random()*100%7)
	    	symptoms = ''
	    	for j in range(0,no_of_symptoms):
				symptoms = symptoms + index['suspect'][j] + ','
	            
			symptoms = symptoms[:-1]
	        df['Symptoms'][i] = symptoms
	        
	    else:
			df['Symptoms'][i] = 'No flu Symptoms'
			df['Symptoms_category'][i] = 'Safe'
	        
	        
	df.head()
	df.to_csv('dataset.csv') 