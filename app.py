from flask import Flask, render_template, request
from llm import generate_jd, parseResume
import os
import pandas as pd

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/create_JD", methods=['GET','POST'])
def create_JD():

    if request.method=="POST":

        metadata=request.form['metadata']
        designation=request.form['designation']
        min_education=request.form['min_education']
        experience=request.form['experience']
        responsibilities=request.form['responsibilities']
        techstack=request.form['techstack']
        other_tools=request.form['other_tools']
        role_type=request.form['role_type']
        role_location=request.form['role_location']
        requisition_id = request.form['requisition_id']
        jd_from_openai = generate_jd(metadata,designation,min_education,experience,responsibilities,techstack,other_tools,role_type,role_location, requisition_id)

        return render_template("create_JD.html", generated_jd=jd_from_openai)

    return render_template("create_JD.html", generate_jd=None)

@app.route("/recommend_candidate", methods=['GET','POST'])
def recommend_candidate():
       
    # if request.method=="POST":
    #     question = request.files['job_desc']
    #     resume_csv_path = ""  ## Specify the path
    #     suitable_candidate_indices = CandidateMatch(resume_csv_path).getSuitableCandidate(question)
        return render_template("recommend_candidate.html")

@app.route("/parse_resume", methods=['GET','POST'])
def parse_resume():
    if request.method=="POST":
        file = request.files['file']
        pdf_path = 'uploads/' + file.filename
        file.save(pdf_path)
        
        response = parseResume(pdf_path)  ## dictionary

        parsed_resume=pd.read_csv("parsed_resumes.csv")
        
        parsed_resume.to_csv('parsed_resumes.csv',index=False)
        
        return render_template("parse_resume.html", response=response)

    return render_template("parse_resume.html")

@app.route("/save_parsed_resume", methods=["POST"])
def save_parsed_resume():

    # Currently just adding a new row every time a resume is parsed
    parsed_resume=pd.read_csv('./parsed_resumes.csv')
    response=request.get_json()
    if response['name'] not in list(parsed_resume['Name'].values):
        parsed_resume.loc[len(parsed_resume),:] = [response['name'], response['phone'], response['email'], response['skills'], response['past_exp'], response['education'], response['certifications'], response['job_role'], response['yoe']]
    else:
        parsed_resume.loc[parsed_resume['Name']==response['name'],:] = [response['name'], response['phone'], response['email'], response['skills'], response['past_exp'], response['education'], response['certifications'], response['job_role'], response['yoe']]
    parsed_resume.to_csv('./parsed_resumes.csv', index=False)
    return 'OK', 200

@app.route("/save_job_desc", methods=['GET','POST'])
def save_job_desc():

    if request.method=="POST":

        job_desc = request.get_json()
        print(job_desc)
        # Write out to file

        return 'OK', 200

if __name__=="__main__":

    app.run(debug=True, port=5001)