from flask import Flask, redirect,render_template


app = Flask(__name__)

@app.route("/")
def home():
    render_template("home.html")

@app.route("/create_JD")
def create_JD():
    render_template("create_JD.html")

@app.route("/recommend_candidate")
def recommend_candidate():
    render_template("recommend_candidate.html")

@app.route("/parse_resume")
def parse_resume():
    render_template("parse_resume.html")

if __name__=="__main__":
    app.run(debug=False, port=5001)