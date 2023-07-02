import os
import pymongo
import pandas as pd
import pinecone as pc
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()

collection  = pymongo.MongoClient( os.getenv("MONGO_URI") )['Resume']['Resume']

class CandidateMatch:
    def __init__(self,job_role):
        global collection
        self.role = job_role
        resume_data = pd.DataFrame(collection.find({},{'_id':0}))
        self.df = resume_data.loc[resume_data['job_role'].isin(job_role)].reset_index(drop=True)
        self.model = SentenceTransformer( model_name_or_path ='sentence-transformers/all-mpnet-base-v2')

    # def filter_candidates_by_job_role(self):
    #     # candidates_to_look_at = parsed_resumes.loc[parsed_resumes['Job_Role'] == selected_roles,['Skillsets','Certifications','Education','YOE']].values
    #     filtered_candidates = self.df.loc[self.df['job_role'].isin(self.role)]
    #     return filtered_candidates

    def recreate_df(self):
        df = self.df.copy()
        df['candidate_feature'] =  'Skills : '+ df['skills']+';'+\
                                        'Experience : '+ df['past_exp']+ ';' +\
                                        'Certifications : '+ df['certifications']+ ';' +\
                                        'Job Role : '+ df['job_role'] + ';'

        return df

    def upsertCandidateFeatures(self):
        pinecone_api_key = os.getenv('PINECONE_KEY')
        environment = os.getenv('PINECONE_ENV')
        pc.init(api_key=pinecone_api_key, environment=environment)
        data =  self.recreate_df()
        data.fillna('Information Unavailable', inplace =True)
        resume_list = []
        for i in range(data.shape[0]):
            id = str(i)
            sentence = data.loc[i]['candidate_feature']
            enc = self.model.encode(sentence)
            metadata = {
                'candidate_features':data.loc[i]['candidate_feature'],
            }
            vector_embedding = enc.tolist()
            resume_list.append((id, vector_embedding, metadata))
        index =  pc.Index('resume-search')
        index.upsert(vectors = resume_list)
        return index
    
    def _find_skill_intersection(self,row):
        existing_skills = row['skills'].split(',')
        desired_skills = row['desired_skills'].split(',')
        existing_skills = [x.lower().replace('\n','').strip() for x in existing_skills]
        desired_skills = [x.lower().replace('\n','').strip() for x in desired_skills]
        matching_skills = set(existing_skills).intersection(set(desired_skills))
        return ",".join(list(matching_skills))

    def fetchSuitableCandidate(self, desired_skills, limit=5):
        index = self.upsertCandidateFeatures()
        encoded_jd_skillsets = self.model.encode(desired_skills).tolist()
        result = index.query(encoded_jd_skillsets, top_k =limit, includeMetaData=True)
        matches = result['matches']
        indices = [int(matches[i]['id']) for i in range(len(matches)) if i in self.df.index.to_list()]
        print(indices)
        print(self.df.shape[0])
        scores = [matches[i]['score'] for i in range(len(matches)) if i in self.df.index.to_list()]
        self.df['desired_skills'] = desired_skills
        ## Filtering by job role + filtering by skill match top 5 
        limit = min(limit, self.df.shape[0])
        result_df  = self.df.iloc[indices[:limit]]  ## To handle out-of-bounds exception
        result_df['matching_skills'] = result_df.apply(self._find_skill_intersection, axis=1)
        ### Normalised relative scoring among top 5 candidates 
        result_df['relative_score'] = scores
        result_df['relative_score'] = ((result_df['relative_score']- result_df['relative_score'].min())/
                                       (result_df['relative_score'].max()- result_df['relative_score'].min()))
        result_df['relative_score'] = result_df['relative_score'].apply(lambda x: round(x*100,2))
        result_df = result_df[['name','phone','email','job_role','skills','desired_skills','matching_skills','relative_score']]

        return result_df.reset_index(drop=True)
    


# resume_path ="parsed_resumes.csv"
# index_name = 'resume-search'
# job_role = ['System Analyst','Operations Engineer']
# obj = CandidateMatch(job_role)
# desired_skillsets  = "PYTHON, Cloud"
# print(os.getenv('PINECONE_KEY'))
# answer  = obj.fetchSuitableCandidate(desired_skillsets)
# print(answer)