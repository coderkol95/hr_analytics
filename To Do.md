# To Do:

[x] Landing page
[x] JD generation
[x] Resume parsing
[x] Candidate recommendation

# JD generation (Anupam)

[x] Accept metadata from user about company and role
[x] Accept user inputs: min experience, job role, experience required in tools and technologies, other tools and technologies, ...
[x] API call to generate JD

# Resume parsing (KD)

[x] Parse these details: candidate name, email, phone number, educational qualifications, experience in technologies, years of experience
[x] Prompt
[x] Store parsed details

# Candidate recommendation 

[x] Accept job role (team lead), tools and technologies, educational experience, min. years of experience, ...
[x] Score resumes as a system
[ ] Match with tick for each matching skill/experience/etc
[ ] Need to prepare a dashboard with graphs, ranking and ticks

Points of Improvements :
1. Create JD Page (Must do): 
    -  When clicked on the Create JD button , it creates the JD but it also resets the input fields. Because of this we are not able to push the requision id in the backend and it returns "": DONE 
    -  When clicked on the save job description button , it shall return the requisition id and the job description both in the flask backend. Then we can store them in mongoDB. We would have to reference the requisition ID later for candidate recommendation and available candidates : DONE 

2. Parse Resume(Must Do):
    - Create a dropdown list of all the requisition ids available and parse the resume of the candidate based on that requisition ID only so that we can get the idea of which candidate applied for which requisition id - DONE
    - Show candidate's resume details on white BG.

3. Candidate DB:
    - Add the Job ID field against each candidate - DONE 

4. Recommend Candidate :
    - Add filters in a better way UI  - Half Done
    - When Req ID is selected the job desc speficif to that req_id must appear in the text box 
    - Better candidate filter and scoring 
    - Remove pinecone and use any inhouse DB
5. General:
    - After every save , there should be one pop up indicating that save to the user.


    
    