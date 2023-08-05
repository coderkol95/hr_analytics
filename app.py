import os
import re
import uuid
import bcrypt
import pymongo
import warnings
import pandas as pd
import mysql
from dotenv import load_dotenv
warnings.filterwarnings('ignore')
from werkzeug.utils import secure_filename
from llm import generate_jd, parseResume, score_candidates
from shortlist_candidate import CandidateCredentials , DescriptiveQnAGenerator 
from flask import Flask, render_template, request, url_for, redirect, session, jsonify

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
cursor = conn.cursor()

## getting the mongoDB Collection: DataBase Name : Resume , Collection Name : Resume
collection  = pymongo.MongoClient( os.getenv("MONGO_URI") )['Resume']['Resume']

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

            return render_template("create_JD.html", generated_jd=jd_from_openai)
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
        if request.method=="POST":
            job_desc = request.form['job_desc']
            try:
                selected_roles = request.form.getlist('selected_values')
            except:
                selected_roles = job_roles
            
            # Will work when API key is available
            # best_candidates = score_candidates(job_desc, selected_roles)
            best_candidates = pd.DataFrame(data=[['a1','b1','c1','d1','e1','f1','g1','h1'],['a2','b2','c2','d2','e2','f2','g2','h2']], columns=['name','phone','email','job_role','skills','desired_skills','matching_skills','relative_score'])

            return render_template("recommend_candidate.html", job_roles=job_roles, scores=best_candidates.to_dict(orient='records'), flag=True)
    else:
        return redirect("/")

    return render_template("recommend_candidate.html", job_roles=job_roles, flag=False)

@app.route("/parse_resume", methods=['GET','POST'])
def parse_resume():
    if request.method=="POST":
        if "user_id" in session:
            files = request.files.getlist('file')
            response_list=[]
            for file in files:
                filename = secure_filename(file.filename)
                pdf_path = 'uploads/' + filename
                file.save(pdf_path)
                response = parseResume(pdf_path)  ## dictionary
                response_list.append(response)    ## 

            # parsed_resume=pd.read_csv("parsed_resumes.csv")
            # parsed_resume.to_csv('parsed_resumes.csv',index=False)
            
            return render_template("parse_resume.html", responses=response_list)
        else:
            return redirect("/")

    return render_template("parse_resume.html")

@app.route("/save_parsed_resume", methods=["POST"])
def save_parsed_resume():
    if request.method=="POST":
        # Currently just adding a new row every time a resume is parsed
        global collection
        response=request.get_json()
        collection.insert_one(response)
        data=collection.find()   ## will fetch all the parsed resume data
        df = pd.DataFrame(data)
        ### Optional Step: Not recommended for building a scalable solution
        df.to_csv('parsed_resumes.csv')  
        return 'OK', 200
    else:
        return redirect("/")

@app.route("/save_job_desc", methods=['GET','POST'])
def save_job_desc():

    if request.method=="POST":
        if request.method=="POST":

            job_desc = request.get_json()
            print(job_desc)
            # Write out to file
            return 'OK', 200
        else:
            return redirect("/")
        
@app.route("/shortlist_candidates", methods=['GET','POST'])
def shortlist_candidates():
    if request.method=="POST":
        if "user_id" in session:
            ### Hard-coded  as of now : But the logic is to be built where we get a list of emails for shortlisted candidates
            
            emails = request.form.getlist('email_checkbox')
            print(emails)
            for email in emails:
                upsert_candidate = CandidateCredentials(db_config).create_candidate_credentials(email)
                # if upsert_candidate !=None:
                DescriptiveQnAGenerator(email).insertDescriptiveQAforCandidate()
                # else:
                    # return jsonify("Error during candidate credential creation")
                    
    return redirect("/")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id')
    print("Session : ", session)
    return redirect(url_for("login"))

if __name__=="__main__":
    app.run(debug=True, port=5001)