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
                Return the output in JSON format where name, contact_number, email_id, linkedIn_id, educational_background, technical_skillsets, past_job_experience, certifications, projects, publication, awards shall be the key.
                If any of the key information is not found from the context, return Not Mentioned in Resume."""

        prompt+=prompt+"\n\n"+"#"+resume_content+"#"
        return prompt