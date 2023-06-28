from flask import Flask, render_template, request
from llm import generate_jd

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

@app.route("/recommend_candidate")
def recommend_candidate():
    return render_template("recommend_candidate.html")

@app.route("/parse_resume")
def parse_resume():
    return render_template("parse_resume.html")

@app.route("/save_job_desc", methods=['GET','POST'])
def save_job_desc():

    if request.method=="POST":

        job_desc = request.get_json()
        print(job_desc)
        # Write out to file

        return 'OK', 200

if __name__=="__main__":

    app.run(debug=True, port=5001)