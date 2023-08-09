import os 
import uuid
import openai
import smtplib
import pymongo
import requests
import pandas as pd
from dotenv import load_dotenv


class JDImprovements:
    def __init__(self, jd):
        self.jd = jd 
        self.chatgtp_api_key = os.getenv('OPENAI_API_KEY')
        self.chatgpt_url = os.getenv('CHATGPT_URL')

    def createPrompt(self):
        prompt = f'''
                You are an experienced recruiter specialized in creating job description for various roles.
                From the given Job Description in the $ delimiter, you need to suggest possible improvement to the JD. 
                If no imprvement is required the simply write "No Improvement Required". You also need to score the JD between 0 to 100.
                Here is the JSON Schema instance of the GPT Response after response['choices'][0]['message']['content'] shall look like:
                "{{
                'jd_improvement': 'The job description has requirements for machine learning but no python libraries are written. Add scikit-learn, keras, tensorflow in required skillset section',
                'jd_score': '80'
                }}
                "
                .The job description goes here ${self.jd}$. 
                Response shall be in JSON Format with jd_improvement and jd_score as the keys.
                Your output will be parsed and type-checked according to the provided schema instance inside & delimiter, so make sure all fields in your output match exactly!
                '''.replace("\n","").replace("  ","")
        
        return prompt
        
    def enhance_jd(self):
        
        chatgpt_headers = {
                    "content-type": "application/json",
                    "Authorization":"Bearer {}".format(self.chatgtp_api_key)}
            
        messages = [
                    {"role": "system", "content": "You are an experienced recruiter specialized in creating job descriptions"},
                    {"role": "user", "content": self.createPrompt()}
                    ]
        chatgpt_payload = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "temperature": 1.2,
                "max_tokens": 2048,
                "stop": ["###"]
                }
        try:
            response = requests.request("POST", self.chatgpt_url, json=chatgpt_payload, headers=chatgpt_headers)
            response = response.json()
            response_content = eval(response['choices'][0]['message']['content'])
            #result = response_content[list(response_content.keys())[0]]
            return response_content
        except Exception as e:
            raise(e)

