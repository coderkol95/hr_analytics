import openai
import os
from parse_resume import Resume
import pandas as pd
import re
from dotenv import load_dotenv
load_dotenv()

MODEL="gpt-3.5-turbo"
openai.api_key = os.environ.get("OPENAI_API_KEY")

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
    answer = completions.choices[0]['text'].replace('.','\n\n')
    resume_data=[x.split(':') for x in answer.split("\n\n") if x!='']
    resume_dict=dict(zip([x[0] for x in resume_data],[x[1:] for x in resume_data]))
    name = resume_dict['Name'][0].strip()
    phone = resume_dict['Contact Number'][0].strip()
    email = resume_dict['Email'][0].strip()
    skills = resume_dict['Skills'][0].strip()
    past_exp = resume_dict['Past Job Experience'][0].strip()
    education = [re.sub('\n','', x) for x in resume_dict['Education']]
    certifications = [re.sub('\n','', x) for x in resume_dict['Certifications']]

    return {'name':name,
            'phone':phone,
            'email':email,
            'skills':skills,
            'past_exp':past_exp,
            'education':education,
            'certifications':certifications}