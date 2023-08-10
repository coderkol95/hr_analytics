import os
import re
import uuid
import math
import time
import bcrypt
import pymongo
import warnings
import pandas as pd
import mysql.connector
from dotenv import load_dotenv
warnings.filterwarnings('ignore')
from werkzeug.utils import secure_filename
from email_candidate import EmailCandidate
from improve_jd import JDImprovements
from llm import generate_jd, parseResume, score_candidates
from sentence_transformers import SentenceTransformer, util
from shortlist_candidate import CandidateCredentials , ResumeQnAGenerator ,JDQnAGenerator
from flask import Flask, render_template, request, url_for, redirect, session, jsonify, url_for

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# MySQL configurations
db_config = {
    "host": os.getenv('DB_HOST'),
    "user": os.getenv('DB_USERNAME'),
    "password": os.getenv('DB_PASSWORD'),
    "database": os.getenv('DB_NAME'),
}

## Connecting to the mysql database to store user 
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor(buffered=True)

## getting the mongoDB Collection: DataBase Name : Resume , Collection Name : Resume
collection  = pymongo.MongoClient( os.getenv("MONGO_URI") )['Resume']['Resume']
jd_collection = pymongo.MongoClient( os.getenv("MONGO_URI") )['Resume']['JD']
candidate_qna = pymongo.MongoClient(os.getenv("MONGO_URI") )['Resume']['Candidate_QnA']

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup():
    id = uuid.uuid4().hex[:16]
    email = request.form["email"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    email_pattern = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"

    if not re.match(email_pattern, email):
        return {"success": False, "message": "Please enter a valid email address."}
    
    if not len(password.split())<8:
        print(password)
        return {"success": False, "message": "Length of password shall be between 8 to 20 characters"}

    # Perform validation (you can add more validation checks)
    if password != confirm_password:
        return {"success": False, "message": "Passwords do not match."}
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    cursor.execute("INSERT INTO users (id, email, password) VALUES (%s,%s, %s)", (id, email, hashed_password))
    conn.commit()
    conn.close()

    return {"success": True, "message": "Sign-up successful!"}

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"].encode('utf-8')

        # Perform authentication with MySQL (you should properly hash passwords in a real application)
        cursor.execute(f'SELECT password FROM users WHERE email = "{email}";')
        user = cursor.fetchone()
        if user:
            stored_password = user[0].encode('utf-8')
            if bcrypt.checkpw(password, stored_password):
                session["user_id"] = user[0]  
                return {"success": True}
            else:
                return {"success": False}
        else:
            return {"success": False}
    else:
        return render_template('login.html')
    
@app.route("/home")
def dashboard():
    # Check if the user is logged in
    if "user_id" in session:
        return render_template("home.html")
    else:
        return redirect("/")

@app.route("/available_candidates")
def available_candidates():
    if "user_id" in session:
        global collection
        fetched_data=collection.find({},{'_id':0}) 
        data = pd.DataFrame(fetched_data)
        # parsed_resumes = pd.read_csv("./parsed_resumes.csv") ## Not a best practice , just an alternative
        items_per_page = 4 # Number of pages to appear in the first place
        page = int(request.args.get('page', 1))
        total_pages = (len(data) + items_per_page - 1) // items_per_page
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(data))
        current_page_data = data[start_idx:end_idx].to_dict(orient='records')
        return render_template("available_candidates.html", data=current_page_data, current_page=page, 
                                    total_pages=total_pages, prev_page=page - 1,next_page=page + 1)
    else:
        return redirect("/")
    
@app.route("/show_jd")
def show_jd():
    if "user_id" in session:
        global jd_collection
        fetched_data=jd_collection.find({},{'_id':0}) 
        data = pd.DataFrame(fetched_data)
        for i in range(data.shape[0]):
            if type(data.loc[i]['jd_improvement'])==float:
                current_req_id = data.loc[i].requisition_id
                current_jd = data.loc[i].job_description
                jd_improvement_obj = JDImprovements(current_jd)
                result = jd_improvement_obj.enhance_jd()
                jd_improvement = result['jd_improvement']
                if jd_improvement == "No Improvement Required":
                    jd_score = '100'
                else:
                    jd_score = result['jd_score']
                jd_collection.update_one({"requisition_id": current_req_id},
                                        {"$set": {"jd_improvement": jd_improvement,"jd_score":jd_score}})
                fetched_data=jd_collection.find({},{'_id':0}) 
                data = pd.DataFrame(fetched_data)
        # parsed_resumes = pd.read_csv("./parsed_resumes.csv") ## Not a best practice , just an alternative
        items_per_page = 4 # Number of pages to appear in the first place
        page = int(request.args.get('page', 1))
        total_pages = (len(data) + items_per_page - 1) // items_per_page
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(data))
        current_page_data = data[start_idx:end_idx].to_dict(orient='records')
        return render_template("show_jd.html", data=current_page_data, current_page=page, 
                                    total_pages=total_pages, prev_page=page - 1,next_page=page + 1)
    else:
        return redirect("/")

@app.route("/create_JD", methods=['GET','POST'])
def create_JD():
    if "user_id" in session:
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

            return render_template("create_JD.html", generated_jd=jd_from_openai, requisition_id = requisition_id)
    else:
        return redirect("/")

    return render_template("create_JD.html", generate_jd=None)

@app.route("/recommend_candidate", methods=['GET','POST'])
def recommend_candidate():
    if "user_id" in session:
        global collection
        data=collection.find({},{'_id':0}) 
        parsed_resumes = pd.DataFrame(data)
        ## parsed_resumes=pd.read_csv('./parsed_resumes.csv') ## Not a best practice , just an alternative
        job_roles=list(parsed_resumes['job_role'].unique())
        fetch = jd_collection.find({},{'requisition_id'})
        requisition_ids=pd.DataFrame(fetch)['requisition_id'].to_list()
        if request.method=="POST":
            job_desc = request.form['job_desc']
            selected_roles = request.form.getlist('optionSelect1')
            selected_requisition_ids=request.form.getlist('optionSelect2')
            # print(selected_roles, selected_requisition_ids, job_desc)
            best_candidates = score_candidates(job_desc, selected_roles)

            return render_template("recommend_candidate.html", job_roles=job_roles, requisition_ids=selected_requisition_ids,
                                   scores=best_candidates.to_dict(orient='records'), flag=True)
    else:
        return redirect("/")

    return render_template("recommend_candidate.html", job_roles=job_roles,requisition_ids=requisition_ids, flag=False)

req_id = None
req_ids = []  ## needed to keep track of the memory of req ids
@app.route("/parse_resume", methods=['GET','POST'])
def parse_resume():
    if "user_id" in session:
        fetch = jd_collection.find({},{'requisition_id'})
        requisition_ids=pd.DataFrame(fetch)['requisition_id'].to_list()
        global req_ids
        global req_id
        if request.method=="POST":
            files = request.files.getlist('file')
            req_id = request.form.get('selected_option', None)
            print(req_id)
            req_ids.append(req_id)
            response_list=[]
            for file in files:
                filename = secure_filename(file.filename)
                ### pdf_path : for Mac
                # pdf_path = 'uploads/' + filename   
                ### pdf_path : for windows
                pdf_path = '.\\uploads\\' + filename   
                # file.save(pdf_path)
                response = parseResume(pdf_path)  ## dictionary
                response.update({'requisition_id':req_ids[0]})
                response_list.append(response)    ## 
                print(response_list)
            
            return render_template("parse_resume.html", requisition_ids = requisition_ids,
                                                        responses=response_list)

        return render_template("parse_resume.html",requisition_ids = requisition_ids,)
    else:
        return redirect("/")


@app.route("/save_parsed_resume", methods=["GET","POST"])
def save_parsed_resume():
    if "user_id" in session:
        # Currently just adding a new row every time a resume is parsed
        global collection
        response = request.get_json()
        print(response)
        collection.insert_one(response)
        # data=collection.find()   ## will fetch all the parsed resume data
        # df = pd.DataFrame(data)
        ### Optional Step: Not recommended for building a scalable solution
        ## df.to_csv('parsed_resumes.csv')  
        return {"success": True}
    else:
        return {"success": True}

@app.route("/save_job_desc", methods=['GET','POST'])
def save_job_desc():
    if "user_id" in session:
        if request.method=="POST":
            user_input_jd = request.get_json()
            job_desc = user_input_jd['job_description']
            req_id = str(user_input_jd['requisition_id'])
            #print(job_desc)
            print(req_id)
            record = {"requisition_id":req_id, "job_description":job_desc}
            filter_={"requisition_id":req_id}
            query_result = jd_collection.find(filter_) 
            d = pd.DataFrame(query_result)
            try:
                if len(d) == 0:
                    jd_collection.insert_one(record)
                    return {"success": True}
                else:
                    jd_collection.update_one({"requisition_id": req_id},
                            {"$set": {"job_description": job_desc}})
                    return {"success": True}
            except:
                return {"success": False}
        else:
            return redirect("/")
                
    else:
        return redirect("/")
        
@app.route("/shortlist_candidates", methods=['GET','POST'])
def shortlist_candidates():
    if "user_id" in session:
        if request.method=="POST":
            emails = request.form.getlist('email_checkbox')
            print(emails)
            for email in emails:
                    try:
                        jb_obj =jd_collection.find({'requisition_id': '0987612345'})         
                        candidate_obj = collection.find({'email':email},{'requisition_id'})
                        req_id = None
                        jd = ""
                        for i in candidate_obj:
                            req_id = i['requisition_id']

                        jb_obj = jd_collection.find({'requisition_id': req_id})
                        for j in jb_obj:
                            jd = j['job_description']

                        candidate_credentials_obj = CandidateCredentials(db_config)
                        ## Creating PW for the candidate to login in test portal
                        candidate_credentials_obj.create_candidate_credentials(email)
                        print("Success !!! Candidate's Login Credentials are created")
                        resume_qna_obj = ResumeQnAGenerator(email)
                        resume_objective_question_prompt = resume_qna_obj.promptMCQs()
                        resume_subjective_question_prompt =  resume_qna_obj.promptDescriptiveQuestions()

                        if resume_objective_question_prompt:
                            resume_objective_questions = resume_qna_obj.askGPT(resume_objective_question_prompt)
                            resume_qna_obj.insertMCQAforCandidate(resume_objective_questions)
                            print("Success !!! MCQs are generated")
                        if resume_subjective_question_prompt:
                            resume_subjective_questions = resume_qna_obj.askGPT(resume_subjective_question_prompt)
                            resume_qna_obj.insertDescriptiveQAforCandidate(resume_subjective_questions)
                            print("Success !!! Subjectives are Generated")

                        # To keep the number of questions limited to 10 only, we have not produced the JD based questions
                        
                        # jd_qna_obj = JDQnAGenerator(email, jd)
                        # jd_objective_question_prompt = jd_qna_obj.promptMCQsfromJD()
                        # jd_subjective_question_prompt =  jd_qna_obj.promptDescriptiveQuestionsfromJD()

                        # if jd_objective_question_prompt:
                        #     jd_objective_questions = jd_qna_obj.askGPT(jd_objective_question_prompt)
                        #     jd_qna_obj.insertJDMCQAforCandidate(jd_objective_questions)
                        # if jd_subjective_question_prompt:
                        #     jd_subjective_questions = jd_qna_obj.askGPT(jd_subjective_question_prompt)
                        #     jd_qna_obj.insertJDDescriptiveQAforCandidate(jd_subjective_questions)

                        candidate_qna.update_one({"email": email}, 
                                                 {"$set": {"status": "Round 1 Initiated"}})
                        print("Success !!! Candidate's status is updated")

                        mail_obj = EmailCandidate()
                        mail_obj.inviteCandidateforAssessment(email)
                        print(email)
                        print("Success !!! Candidate's is sent email for assessment")

                        df_data = candidate_qna.find()
                        df_dict = pd.DataFrame(df_data).to_dict(orient='records')

                        return render_template("recruitment_journey.html", data=df_dict)
                    
                    except Exception as e:
                        return jsonify(f"Cannot create Resume questions for {email}", e)
                                     
    return redirect("/")

@app.route('/send_round2_email', methods=['POST'])
def send_email():
    data = request.get_json()
    email = data['email']
    mail_obj = EmailCandidate()
    mail_obj.inviteCandidateForInterview(email)
    #print(email)
    print("Success !!! Candidate's is sent email for Round 2")    
    candidate_qna.update_one({"email": email}, 
                                {"$set": {"status": "Round 2 Initiated"}})    
    return {'message': 'Email sent successfully'}

@app.route("/recruitment_journey", methods=['GET','POST'])
def recruitment_journey():
    if "user_id" in session:
        df_data = candidate_qna.find()
        df_dict = pd.DataFrame(df_data).to_dict(orient='records')
        # print(df_dict)
        return render_template("recruitment_journey.html", data=df_dict)
    else:
        return redirect("/")

existing_jd = None
@app.route('/score_jd', methods=['GET','POST'])
def score_jd():
    global existing_jd
    new_jd_info = request.json
    req_id = new_jd_info['req_id']
    new_jd = new_jd_info['jd']
    filter_ = {'requsition_id':req_id}
    jd_obj = jd_collection.find(filter_)
    print(new_jd_info)
    for jd_dict in jd_obj:
        existing_jd = jd_dict['job_description']
    similarity_score = _calculate_semantic_similarity(existing_jd,new_jd)
    if similarity_score>=0.8:
        jd_collection.update_one({'requsition_id':req_id},
                         {"$set": {"job_description": new_jd,"jd_score":jd_score}})
        return jsonify({"message": "JD saved successfully with no change in score as the change in JD is very minimal"})
    else:
        jd_improvement_obj = JDImprovements(new_jd)
        result = jd_improvement_obj.enhance_jd()
        jd_improvement = result['jd_improvement']

        if jd_improvement == "No Improvement Required":
            jd_score = '100'
        else:
            jd_score = result['jd_score']

        jd_collection.update_one({'requsition_id':req_id},
                         {"$set": {"job_description": new_jd,"jd_improvement":jd_improvement,"jd_score":jd_score}})
        return jsonify({"message": "JD saved successfully with  change in score as the change in JD is very significant"})


def _calculate_semantic_similarity(sentence1, sentence2):
    '''
        Calculate Similartity score between GPT answer and candidate answer
    '''
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    embeddings = model.encode([sentence1, sentence2], convert_to_tensor=True)
    cosine_sim = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    return cosine_sim.item()

@app.route('/save_journey', methods=['POST'])
def save_journey():
    global candidate_qna
    new_data = request.json
    data=[]
    data.append(new_data)
    #print(data)
    #candidate_qna.insert_one(new_data)
    candidate_email_id = new_data['email']
    #print(candidate_email_id)
    candidate_qna.update_one({"email": candidate_email_id},
                            {"$set": new_data})
    data.clear()
    return jsonify({"message": "Data saved successfully"})

@app.route('/get_dropdown_result', methods=['POST'])
def get_response():
    selected_req_id = request.json.get('selected_option')
    print(selected_req_id)
    jd_collection = pymongo.MongoClient( os.getenv("MONGO_URI") )['Resume']['JD']
    filter_={"requisition_id":selected_req_id}
    query_result_iterator = jd_collection.find(filter_,{'job_description'}) 
    for query_result in query_result_iterator:
        job_description = query_result['job_description']
    return jsonify(response = job_description)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id')
    print("Session : ", session)
    return redirect(url_for("login"))

if __name__=="__main__":
    app.run(debug=True, port=5001)