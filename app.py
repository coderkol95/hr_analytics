import os 
import pandas as pd
from dotenv import load_dotenv
from parse_resume import Resume
from flask import Flask, render_template, request
from llm import _parseResume
load_dotenv()

global parsed_resume
parsed_resume=pd.read_csv("parsed_resumes.csv")

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] ="./uploaded_resume/"
app.config['SAVED_PDF_PATH']= ".\\uploaded_resume\\"

@app.route("/")
def home():
    return render_template("parse_resume.html")

@app.route("/create_JD")
def create_JD():
    render_template("create_JD.html")

@app.route("/recommend_candidate")
def recommend_candidate():
    render_template("recommend_candidate.html")

@app.route('/parse_resume', methods=['POST'])
def upload():
    global parsed_resume
    # Check if a file was uploaded
    if 'pdf_file' in request.files:
        saved_pdf_name = 'uploaded_resume.pdf'
        pdf = request.files['pdf_file']
        # Save the uploaded PDF file
        filepath = os.path.join(app.config["UPLOAD_FOLDER"] , saved_pdf_name)
        pdf.save(filepath)
        
        pdf_path = os.path.join(app.config['SAVED_PDF_PATH'],saved_pdf_name)
        prompt = Resume(pdf_path)._createPrompt().replace('   ','')
        response = _parseResume(prompt)
        parsed_resume.loc[len(parsed_resume),:]=response
        return response

if __name__=="__main__":
    app.run(debug=False, port=5001)