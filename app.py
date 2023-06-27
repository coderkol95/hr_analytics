from flask import Flask, redirect,render_template


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/create_JD")
def create_JD():
    return render_template("create_JD.html")

@app.route("/recommend_candidate")
def recommend_candidate():
    return render_template("recommend_candidate.html")

@app.route("/parse_resume")
def parse_resume():
    return render_template("parse_resume.html")

if __name__=="__main__":

    app.run(debug=True, port=5001)