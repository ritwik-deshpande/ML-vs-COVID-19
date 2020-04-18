from flask import Flask,render_template,request
from Bayes_Classifier import predict


app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html' ,category = "None")
    
@app.route("/handle_data",methods = ['POST'])
def handle_data():

	gender = request.form['gender']
	detected_state =  request.form['detected_state']
	symptoms = ''
	for symptom in request.form.getlist('Symptoms'):
		symptoms = symptoms + ' ' + symptom 

	diagnosed_date = request.form['diagnosed_date']
	notes = request.form['notes'] 
	age = request.form['age']
	category = predict(gender,age,notes,detected_state,symptoms,diagnosed_date)[0]



	return render_template('index.html' ,category = str(category))



    
if __name__ == '__main__':

	app.run(debug=True)