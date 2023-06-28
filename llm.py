import openai
import os
from dotenv import load_dotenv
load_dotenv()

def _parseResume(prompt, n=3,engine ='text-davinci-003'):
    openai.api_key= os.getenv('OPENAI_KEY')
    completions = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            max_tokens=2048,
            n=1,
            temperature=0.01,
        )
    answer = completions.choices[0]['text'].replace('.','\n\n')
    return answer(prompt, n=3,engine ='text-davinci-003')