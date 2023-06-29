import os
import pandas as pd
import pinecone as pc
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()

class CandidateMatch:
    def __init__(self,csv_path):
        self.df=pd.read_csv(csv_path)
        self.model = SentenceTransformer( model_name_or_path ='sentence-transformers/all-mpnet-base-v2')

    def recreate_df(self):
        df=self.df.copy()
        for row in range(df.shape[0]):
            candidate_feature = ""
            for col in df.columns[3:]:
                candidate_feature += str(col).strip() + ":" + str(df.loc[row,col]).strip()+";"
            df.loc[row,'candidate_feature'] = candidate_feature

        return df

    def upserCandidateFeatures(self):
        pinecone_api_key = os.getenv('PINECONE_KEY')
        environment = os.getenv('PINECONE_ENV')
        pc.init(api_key=pinecone_api_key, environment=environment)
        data =  self.recreate_df()
        resume_list = []
        for i in range(data.shape[0]):
            id = str(i)
            sentence = data.loc[i].candidate_feature
            enc = self.model.encode(sentence)
            metadata = {
                'candidate_features':data.loc[i].candidate_feature,
            }
            vector_embedding = enc.tolist()
            resume_list.append((id, vector_embedding, metadata))
        index =  pc.Index('resume-search')
        index.upsert(vectors = resume_list)
        return index

    def getSuitableCandidate(self, question, limit=5):
        index = self.upserCandidateFeatures()
        encoded_question = self.model.encode(question).tolist()
        result = index.query(encoded_question, top_k =limit, includeMetaData=True)
        matches = result['matches']
        indices = [int(matches[i]['id']) for i in range(len(matches))]
        return indices
    

# resume_path ="parsed_resumes.csv"
# index_name = 'resume-search'
# obj = CandidateMatch(resume_path)
# question  = "Find me the candidate with experties in Machine Learning"
# print(os.getenv('PINECONE_KEY'))
# answer  = obj.getSuitableCandidate(question)
# print(answer)