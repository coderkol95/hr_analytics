import os 
import smtplib
import pymongo
import mysql.connector
from dotenv import load_dotenv
from email.mime.text import MIMEText
load_dotenv()

candidate_qna = pymongo.MongoClient(os.getenv("MONGO_URI") )['Resume']['Candidate_QnA']

class EmailCandidate:
    def __init__(self, db_config):
        self.db_config = db_config
        self.sender_email = os.getenv('sender_mail_id')
        self.sender_password = os.getenv('sender_password')

    def inviteCandidateforAssessment(self,candidate_email_id='krishnendudey21@gmail.com'):
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        recipient_email = candidate_email_id
        recipient_name = cursor.execute(f"SELECT name FROM users WHERE email = '{candidate_email_id}';")
        recipient_password = cursor.execute(f"SELECT password FROM users WHERE email = '{candidate_email_id}';")
        test_url = f'http://localhost:5000/'

        subject = 'Congratulations! Invitation to Complete Technical Assessment'
        message_body = f'''Dear {recipient_name},

                        We appreciate your enthusiasm for the opportunity and your interest in joining our team.

                        As part of the our hiring process, we have initiated a Technical Assessment specifically designed to evaluate the skills we are seeking for this position.
                        We kindly request you to complete the assessment within the next 48 hours.

                        Kindly use the following credentials to log into the Assessment portal. 
                        email id : {candidate_email_id} , password : {recipient_password}

                        You can click on below link and you will be redirected to the assessment page to take the test. 
                        Test Link : {test_url}

                        Best of luck!

                        Warm regards, 
                        Talent Acquisition Team
                        '''
        try:
            smtp_server = 'smtp.office365.com'  # For Outlook/Office 365
            smtp_port = 587                     # For TLS
            smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
            status_code , response = smtp_connection.ehlo()
            print(f"Status = {status_code}, response = {response}")
            status_code , response = smtp_connection.starttls()
            print(f"Status = {status_code}, response = {response}")

            # Set a longer timeout to handle potential connection delays
            smtp_connection.timeout = 30
            # Log in to your Outlook email account
            smtp_connection.login(self.sender_email, self.sender_password)

            # Create the email message
            message = MIMEText(message_body)
            message['From'] = self.sender_email
            message['To'] = recipient_email
            message['Subject'] = subject

            # Send the email
            smtp_connection.sendmail(self.sender_email, recipient_email, message.as_string())
            print("Email sent successfully!")

            # Close the SMTP connection
            smtp_connection.quit()
        except Exception as e:
            print(e)


    def inviteCandidateForInterview(self,candidate_email_id):
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        recipient_email = candidate_email_id
        recipient_name = cursor.execute(f"SELECT name FROM users WHERE email = '{candidate_email_id}';")
        recipient_password = cursor.execute(f"SELECT password FROM users WHERE email = '{candidate_email_id}';")
        test_url = f'http://localhost:5000/'

        subject = 'Congratulations! Invitation for Interview with the Hiring Manager'
        message_body = f'''Dear {recipient_name},

                        Congratulations!!!
                        You have aced the technical assessment round. You are one step closer to join in our team.

                        As part of the second round of our hiring process, you will have an interview with the hiring manager.
                        The details of the interview is as follows.

                        Kindly use the following credentials to log into the Assessment portal. 
                        email id : {candidate_email_id} , password : {recipient_password}

                        You can click on below link and you will be redirected to the assessment page to take the test. 
                        Test Link : {test_url}

                        Best of luck!

                        Warm regards, 
                        Talent Acquisition Team
                        '''
        try:
            smtp_server = 'smtp.office365.com'  # For Outlook/Office 365
            smtp_port = 587                     # For TLS
            smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
            status_code , response = smtp_connection.ehlo()
            print(f"Status = {status_code}, response = {response}")
            status_code , response = smtp_connection.starttls()
            print(f"Status = {status_code}, response = {response}")

            # Set a longer timeout to handle potential connection delays
            smtp_connection.timeout = 30
            # Log in to your Outlook email account
            smtp_connection.login(self.sender_email, self.sender_password)

            # Create the email message
            message = MIMEText(message_body)
            message['From'] = self.sender_email
            message['To'] = recipient_email
            message['Subject'] = subject

            # Send the email
            smtp_connection.sendmail(self.sender_email, recipient_email, message.as_string())
            print("Email sent successfully!")

            # Close the SMTP connection
            smtp_connection.quit()
        except Exception as e:
            print(e)
