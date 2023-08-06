import openai
import os
import requests
from parse_resume import Resume
import pandas as pd
import re
import json
from dotenv import load_dotenv
from matchCandidate import CandidateMatch
load_dotenv()

MODEL="gpt-3.5-turbo"
engine="text-davinci-003"
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

def parseResume(pdf_path):
    
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
    print(resume_dict)
    name = resume_dict['name']
    phone = resume_dict['contact_number']
    email = resume_dict['email_id']
    skills = resume_dict['technical_skillsets']
    past_exp = resume_dict['past_job_experience']
    education = resume_dict['educational_background']
    certifications = resume_dict['certifications']
    job_role = resume_dict['identified_job_role']
    years_of_experience = resume_dict['years_of_experience']

    return {'name':name,
            'phone':phone,
            'email':email,
            'skills':skills,
            'past_exp':past_exp,
            'education':education,
            'certifications':certifications,
            'job_role':job_role,
            'yoe':years_of_experience}

def _identify_skillsets_from_jd(jd):

    prompt = f"""
    You are a Specialist Recruiter. \
    Your job is to make a comma seperated string of the technical skillsets  as extracted from the job description written within the # delimiter.\
    Do not write anything out of context and only and only return the answer and nothing extra.
    \n]n #{jd}#"""
    completions = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            max_tokens=2048,
            n=1,
            temperature=0.01,
        )
    answer = completions.choices[0]['text']
    skills=[x.strip('\n') for x in answer.split(',')]
    return ",".join(skills)

def score_candidates(job_desc, job_role):
    '''
        This method shall be used if you do not want to rely on OpenAI while genmerating 
        candidate recommendation rather want to depend on the similarity scores for the match. 
        This method returns the top 5 candidates by default that suits the job role in descending
        order of the semantic similarity score.
    '''
    identified_skillsets_from_jd =_identify_skillsets_from_jd(job_desc)
    candidate_obj = CandidateMatch(job_role)
    best_candidates = candidate_obj.fetchSuitableCandidate(identified_skillsets_from_jd)
    return best_candidates

# def _identify_candidates_by_job_role(parsed_resumes,selected_roles):
#     print(selected_roles)
#     # candidates_to_look_at = parsed_resumes.loc[parsed_resumes['Job_Role'] == selected_roles,['Skillsets','Certifications','Education','YOE']].values
#     candidates_to_look_at = parsed_resumes.loc[parsed_resumes['job_role'].isin(selected_roles)]
#     # candidate_data=""""""
#     # print(candidate_data)
#     # for i, v in enumerate(candidates_to_look_at):
#     #     candidate_data+=str(i+1)+". "+str(v[0])+" :: "+"; ".join(str(x) for x in v[1:])+" \n"
#     return candidates_to_look_at

# def score_candidates(parsed_resumes,job_desc,selected_roles):

#     identified_skillsets_from_jd=_identify_skillsets_from_jd(job_desc)
#     candidate_data = _identify_candidates_by_job_role(parsed_resumes,selected_roles)

#     # job_roles = {",".join(selected_roles)}  # Removed from prompt


#     prompt = f"""
#     You are a professional recruiter for technical companies. You will be given skills in 'skills' to evaluate different candidates given their 
#     names and skillsets. Your job will be to mention only the candidate skills which are there in 'skills' and to assign scores between 1 to 100 
#     against each candidate on the basis of matching skills only. The candidates with the most matching skillsets shall be given the highest score.
#     The details of candidates are given in 'candidates' item-wise. The scores shall be assigned before the list of identified skills for each 
#     candidate. Start only with the answer. Don't justify the reason behind the scoring.

#     skills = [{identified_skillsets_from_jd}]
#     candidates = {candidate_data}

#     Print the name, score and matching skills for each candidate"""

#     response = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "user", "content": prompt,
#         },
#     ],
#     temperature=0,
#     )
#     answer = response.choices[0]['message']['content']

#     # eachline=[x.split('-') for x in answer.split("\n")]
#     # eachline_v2=[[y.split(":") for y in x] for x in eachline]

#     # recom=pd.DataFrame(eachline_v2, columns=["Name","Found skills","Score"])
#     # recom=recom.applymap(lambda x: ''.join(x))
#     # recom['Found skills']=recom['Found skills'].apply(lambda x: "".join(x))
#     # recom['Score']=recom['Score'].apply(lambda x: x[6:])

#     return answer.split("\n")

# pdf_path = ".\\uploads\\Aditya_Soni_Resume.pdf"
# prompt = Resume(pdf_path)._createPrompt()
# print(prompt)
# print(ParseResume().parse(prompt))