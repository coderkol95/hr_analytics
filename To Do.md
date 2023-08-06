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
    - When user clicks on save job description button, when it gets stored in the backend then user shall get a pop up like it has been stored to the database:

    
    