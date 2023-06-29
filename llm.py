import openai
import os
from parse_resume import Resume
import pandas as pd
# import pymongo
import re
import json
from dotenv import load_dotenv
load_dotenv()

MODEL="gpt-3.5-turbo"
openai.api_key = os.environ.get("OPENAI_API_KEY")
# MongoDB_URI = os.environ.get("MONGO_URI")

def generate_jd(metadata,designation,min_education,experience,responsibilities,techstack,other_tools, role_type, role_location, requisition_id):
    
    response = openai.ChatCompletion.create(
    model=MODEL,
    messages=[
        # {"role": "system", "content": "You are an experienced recruiter in a technology company having in-depth knowledge of different technical roles and their responsibilities."},
        {"role": "user", "content": f"""You are a recruiter for a technology company. You have been asked by the team to create a job description with the below details.
            1. About the company and role: {metadata}. Elaborate about these teams in such companies.
            2. Designation: {designation}
            3. Minimum educational qualifications: {min_education}. Be more elaborate.
            4. Minimum years of experience required: {experience} years
            5. Responsibilities:{responsibilities}. Elaborate on these responsibilities as per your knowledge for the role of {designation}
            6. Technology stack experience required: {techstack}. Add one line details for each skill/tool mentioned.
            7. Role type: {role_type}
            8. Role location: {role_location}
            9. Requisition ID: {requisition_id}
            10. Other information to include in the resume: {other_tools}
            Please add other relevant details as you may think relevant. """,
        },
    ],
    temperature=0,
    )

    return response.choices[0]['message']['content']

def parseResume(pdf_path, n=3,engine ='text-davinci-003'):
    
    prompt = Resume(pdf_path)._createPrompt().replace('   ','')
    completions = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            max_tokens=2048,
            n=1,
            temperature=0.01,
        )
    answer = completions.choices[0]['text']
    # resume_data=[x.split(':') for x in answer.split("\n\n") if x!='']
    # resume_dict=dict(zip([x[0] for x in resume_data],[x[1:] for x in resume_data]))
    resume_dict=json.loads(answer[10:])
    name = resume_dict['name']
    phone = resume_dict['contact_number']
    email = resume_dict['email_id']
    skills = resume_dict['technical_skillsets']
    past_exp = resume_dict['past_job_experience']
    education = resume_dict['educational_background']
    certifications = resume_dict['certifications']

    return {'name':name,
            'phone':phone,
            'email':email,
            'skills':skills,
            'past_exp':past_exp,
            'education':education,
            'certifications':certifications}
    
    # ### Mongo db Integration for storing the Data
    # client = pymongo.MongoClient(MongoDB_URI)
    # collection = client['Resume']['Resume']
    # collection.insert_one(output)
    # data=collection.find()   ## will fetch all the data
    # df = pd.DataFrame(data)
    # ### saving all the resume parsed so far in one csv
    # df.to_csv('parsed_csv_mongo.csv')  
    # return output