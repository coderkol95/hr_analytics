from flask import Flask, render_template, request
from llm import generate_jd, parseResume, score_candidates
import os
import pymongo
import warnings
warnings.filterwarnings('ignore')
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

## getting the mongoDB Collection: DataBase Name : Resume , Collection Name : Resume
collection  = pymongo.MongoClient( os.getenv("MONGO_URI") )['Resume']['Resume']

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/available_candidates")
def available_candidates():
    global collection
    data=collection.find({},{'_id':0}) 
    parsed_resumes = pd.DataFrame(data)
    # parsed_resumes = pd.read_csv("./parsed_resumes.csv") ## Not a best practice , just an alternative
    return render_template("available_candidates.html", table=parsed_resumes.to_html(index=False))

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
    global collection
    data=collection.find({},{'_id':0}) 
    parsed_resumes = pd.DataFrame(data)
    ## parsed_resumes=pd.read_csv('./parsed_resumes.csv') ## Not a best practice , just an alternative
    job_roles=list(parsed_resumes['job_role'].unique())
    if request.method=="POST":
        job_desc = request.form['job_desc']
        try:
            selected_roles = request.form.getlist('selected_values')
            best_candidates = score_candidates(job_desc, selected_roles)
            return render_template("recommend_candidate.html", job_roles=job_roles, table=best_candidates.to_html(index=False))
        except:
            best_candidates = score_candidates(job_desc, job_roles)
            return render_template("recommend_candidate.html", job_roles=job_roles, table=best_candidates.to_html(index=False))

    return render_template("recommend_candidate.html", job_roles=job_roles)

@app.route("/parse_resume", methods=['GET','POST'])
def parse_resume():
    if request.method=="POST":
        file = request.files['file']
        pdf_path = 'uploads/' + file.filename
        file.save(pdf_path)
        
        response = parseResume(pdf_path)  ## dictionary

        # parsed_resume=pd.read_csv("parsed_resumes.csv")
        # parsed_resume.to_csv('parsed_resumes.csv',index=False)
        
        return render_template("parse_resume.html", response=response)

    return render_template("parse_resume.html")

@app.route("/save_parsed_resume", methods=["POST"])
def save_parsed_resume():
    # Currently just adding a new row every time a resume is parsed
    global collection
    response=request.get_json()
    collection.insert_one(response)
    data=collection.find()   ## will fetch all the parsed resume data
    df = pd.DataFrame(data)
    ### Optional Step: Not recommended for building a scalable solution
    df.to_csv('parsed_resumes.csv')  

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