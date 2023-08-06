import re 
import fitz

class Resume:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path 
        self.start_page = 1
        self.end_page = None

    def _preprocess(self,text):
        '''
        preprocess chunks
        1. Replace new line character with whitespace.
        2. Replace redundant whitespace with a single whitespace
        '''
        text = text.replace('\n', ' ')
        text = re.sub('\s+', ' ', text)
        text = re.sub(r'\\u[e-f][0-9a-z]{3}',' ', text)
        return text
    
    def _pdf_to_text(self):
        '''
            convert pdf to a list of words.
        '''
        doc = fitz.open(self.pdf_path)
        total_pages= doc.page_count

        if self.end_page is None:
            self.end_page = total_pages
        text_list=[]

        for i in range(self.start_page-1, self.end_page):
            text= doc.load_page(i).get_text('text')
            text= self._preprocess(text)
            text_list.append(text)
        doc.close()
        return text_list
    
    def _createPrompt(self):
        text_list = self._pdf_to_text()
        resume_content = ".".join(text_list)
        prompt= """Your job is of a Resume Parser. From the resume information given inside the delimiter #,
                you shall find out the details such as Name, contact number, email id and other profile links,phone number, skillsets, past job experience. 
                Once you find them out you need to show them in pointwise manner.  
                Keep it short and precise. 
                Do not generate anything unnecessary and Do not generate anything on your own that is not in the context.
                Return the output in JSON format where name, contact_number, email_id, linkedIn_id, educational_background, years_of_experience, identified_job_role, technical_skillsets, past_job_experience, certifications, projects, publication, awards shall be the key.
                If any of the key information is not found from the context, return Not Mentioned in Resume."""

        prompt+=prompt+"\n\n"+"#"+resume_content+"#"
        return prompt
    
    # def _createPrompt(self):
    #     text_list = self._pdf_to_text()
    #     resume_content = ".".join(text_list)
    #     prompt= f'''
    #             Your job is of a Resume Parser. From the resume information given inside the delimiter #,
    #             you shall find out the details such as Name, contact number, email id and other profile links,phone number, skillsets, past job experience. 
    #             Once you find them out you need to show them in pointwise manner.  
    #             Keep it short and precise. 
    #             Do not generate anything unnecessary and Do not generate anything on your own that is not in the context.
    #             Here is the JSON Schema instance your output must adhere to:
    #             "'json':
    #             [{{
    #             'requisition_id':'99D999S9G9',
    #             'name':'John Doe',
    #             'phone':'+91 0009991111',
    #             'email':'myemail@email.com',
    #             'skills':'python,sql,machine learning, web development, blockchain, cyber security',
    #             'past_exp':'5 years at Google as AI engineer, 5 years at Uber as product manager',
    #             'education':'BE in Computer Science at MIT, ME in AI at Stanford University',
    #             'certifications':'AWS Solution Architect',
    #             'job_role':'Data Scientist',
    #             'yoe':'10'
    #             }}]
    #             "
    #             If any of the key information is not found from the context, return Not Mentioned in Resume.
    #             Resume Content : # {resume_content} #
    #             '''.replace("\n","").replace("  ","")
    #     return prompt