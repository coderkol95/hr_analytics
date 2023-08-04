import os 
import uuid
import openai
import pymongo
import requests
import pandas as pd
import mysql.connector
from dotenv import load_dotenv


load_dotenv()
collection  = pymongo.MongoClient(os.getenv("MONGO_URI") )['Resume']['Resume']
candidate_qna = pymongo.MongoClient(os.getenv("MONGO_URI") )['Resume']['Candidate_QnA']

class CandidateCredentials:
    def __init__(self, db_config):
        self.db_config = db_config

    def create_candidate_credentials(self,candidate_email_id):
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            id = uuid.uuid4().hex[:16]
            email = candidate_email_id
            password = uuid.uuid4().hex[:16]
            cursor.execute("INSERT INTO candidates (id, email, password) VALUES (%s,%s, %s)", 
                           (id, email, password))
            conn.commit()
            conn.close()
        except Exception as e:
            raise(e)

class ResumeQnAGenerator:
    def __init__(self,candidate_email_id):
        self.candidate_email_id = candidate_email_id
        self.chatgtp_api_key = os.getenv('OPENAI_API_KEY')
        self.chatgpt_url = os.getenv('CHATGPT_URL')

    def promptDescriptiveQuestions(self) -> str:
        '''
            Prompt engineeering with fewshots.
        '''
        filter_={"email":self.candidate_email_id}
        projection = {"_id": 0,"phone":0,"job_role":0,"education":0,'name':0,'email':0}
        query_result = collection.find(filter_, projection) 
        d  = pd.DataFrame(query_result)
        candidate_summary = d.to_dict(orient='records')[0]
        del d
        if candidate_summary:
            descriptive_prompt = f'''
                You are an experienced recruiter specialized in technical assessment of the candidates.
                From the given dictionary in the $ delimiter, you need to prepare 2 easy, 2 medium and 1 hard descriptive type question.
                You will also have to write answer for the same. Here is the JSON Schema instance your output must adhere to:
                
                "'json':
                [{{
                'question': 'Which programming language is often used for data analysis and has libraries like Pandas and NumPy?',
                'answer': 'Python'
                }}]
                "
                Prepare the level of question based on candidates years of experience(yoe). 
                The candidate's summary goes here ${candidate_summary}$. 
                Response shall be in JSON Format.Contain no additional information.
                Your output will be parsed and type-checked according to the provided schema instance inside & delimiter, so make sure all fields in your output match exactly!
                '''.replace("\n","").replace("  ","")
            
            return descriptive_prompt
        else:
            return "Candidate information not found!"
        
    def promptMCQs(self) -> str:
        '''
            Prompt engineeering with fewshots.
        '''
        filter_={"email":self.candidate_email_id}
        projection = {"_id": 0,"phone":0,"job_role":0,"education":0,'name':0,'email':0}
        query_result = collection.find(filter_, projection) 
        d  = pd.DataFrame(query_result)
        candidate_summary = d.to_dict(orient='records')[0]
        del d
        if candidate_summary:
            mcq_prompt = f'''
                    You are an experienced recruiter specialized in technical assessment of the candidates.
                    From the given dictionary in the # delimiter, you need to prepare 2 easy, 2 medium and 1 hard MCQ  type purely technical question.
                    You will also have to write answer for the same. Here is the JSON Schema instance your output must adhere to:
                    "'json':
                    [{{
                        "question": "Which programming language is often used for data analysis and has libraries like Pandas and NumPy?",
                        "options": {{
                            "a": "SQL",
                            "b": "Python",
                            "c": "R Programming",
                            "d": "Excel/Google Sheets"
                        }},
                        "answer": "b"
                    }}]".
                    Prepare the level of question based on candidates years of experience(yoe). 
                    The candidate's summary goes here:
                    #{candidate_summary}#.
                    Response shall be in Python dictionary Format with question, options and answer as keys. Contain no additional information. 
                    Do not create seperate labels of easy, medium and hard in the response. Your output will be parsed and type-checked according to the provided schema instance inside & delimiter, so make sure all fields in your output match exactly!
                    '''.replace("\n","").replace("  ","")
            
            return mcq_prompt
        else:
            return "Candidate information not found!"
        
    def askGPT(self, prompt):
        '''
            Making connection to  the chatGPT server to return the response in JSON format always.
        '''
        chatgpt_headers = {
                "content-type": "application/json",
                "Authorization":"Bearer {}".format(self.chatgtp_api_key)}
        
        messages = [
                    {"role": "system", "content": "You are an experienced recruiter specialized in technical assessment of the candidates"},
                    {"role": "user", "content": prompt}
                    ]
        chatgpt_payload = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "temperature": 1.2,
                "max_tokens": 1024,
                "stop": ["###"]
                }
        response = requests.request("POST", self.chatgpt_url, json=chatgpt_payload, headers=chatgpt_headers)
        response = response.json()
        print(response)
        response_content = eval(response['choices'][0]['message']['content'])
        return response_content[list(response_content.keys())[0]]

    def generateQAFromDescriptivePrompt(self) -> list:
        '''
            Crtical step : Generating the QnA output as list of dict using GPT 3.5 Turbo
        '''
        try:
            descriptive_prompt = self.promptDescriptiveQuestions()
            answer = self.askGPT(descriptive_prompt)
            return answer
        except Exception as e :
            raise(e)
        
    def generateQAFromMCQPrompt(self) -> list:
        '''
            Crtical step : Generating the QnA output as list of dict using GPT 3.5 Turbo
        '''
        try:
            mcq_prompt = self.promptMCQs()
            answer = self.askGPT(mcq_prompt)
            return answer
        except Exception as e :
            raise(e)
    
    def insertDescriptiveQAforCandidate(self):
        '''
            Inserting the questions and answers generated based on the resume of the 
            candidate to the mongoDB database. 
        '''
        try:
            filter_= {"email":self.candidate_email_id}
            candidate_name = collection.find(filter_, {'name'}).next()['name']
            res = candidate_qna.find(filter_)
            d = pd.DataFrame(res)
            descriptive_qna_dict = self.generateQAFromDescriptivePrompt()
            if len(d)==0:
                record = {"name":candidate_name, "email":self.candidate_email_id,"resume_descriptive_qna": descriptive_qna_dict}
                candidate_qna.insert_one(record)
            else:
                candidate_qna.update_one({"email": self.candidate_email_id},
                            {"$set": {"resume_descriptive_qna": descriptive_qna_dict}})

        except Exception as e :
            raise(e)
        
    def insertMCQAforCandidate(self):
        '''
            Inserting the questions and answers generated based on the resume of the 
            candidate to the mongoDB database. 
        '''
        try:
            filter_= {"email":self.candidate_email_id}
            candidate_name = collection.find(filter_, {'name'}).next()['name']
            res = candidate_qna.find(filter_)
            d = pd.DataFrame(res)
            mc_qna_dict = self.generateQAFromMCQPrompt()
            
            if len(d)==0:
                record = {"name":candidate_name, "email":self.candidate_email_id,"resume_mcq": mc_qna_dict}
                candidate_qna.insert_one(record)
            else:
                candidate_qna.update_one({"email": self.candidate_email_id},
                            {"$set": {"resume_mcq": mc_qna_dict}})

        except Exception as e :
            raise(e)