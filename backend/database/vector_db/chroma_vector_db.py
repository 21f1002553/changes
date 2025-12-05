import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
from utils import TextUtility
from langchain_text_splitters import RecursiveCharacterTextSplitter
from genai.schema import rag_engine
from langchain_huggingface import HuggingFaceEmbeddings

Embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

class ChromaVectorDBService:
    def __init__(self, persist_dir: str = './chroma-db' , model_name: str = 'all-MiniLM-L6-v2',):
        self.client = chromadb.PersistentClient(path="chroma_db")
        self.model = SentenceTransformer(model_name)

    ## Get Embeddings
    def get_embedding(self,text:str) -> List[float]:
        return self.model.encode(text).tolist()

    ## get_collections
    def get_collection(self,collection_name: str):
        return self.client.get_or_create_collection(name=collection_name)

    ## Load Data into vector store
    def load_data(self, doc_id, meta_data, collection_name: str, text: str):
        collection = self.get_collection(collection_name)
        embeddings = self.get_embedding(text)
        collection.add(documents=[text], embeddings=[embeddings], metadatas=[meta_data], ids=[doc_id])

        return {
            "id": doc_id,
            "text": text,
            "meta_data": meta_data,
            "embeddings": embeddings,
            "collection_name": collection_name,
            "status":"success"
        }

    ## clear collection
    def clear_collection(self, collection_name: str):
        """Delete all documents from a collection"""
        try:
            collection = self.get_collection(collection_name)
            existing_ids = collection.get()["ids"]
            
            if existing_ids:
                collection.delete(ids=existing_ids)
                print(f"✅ Cleared {len(existing_ids)} documents from collection '{collection_name}'")
                return {"status": "success", "deleted_count": len(existing_ids)}
            else:
                print(f"ℹ️ Collection '{collection_name}' is already empty")
                return {"status": "success", "deleted_count": 0}
                
        except Exception as e:
            print(f"❌ Error clearing collection '{collection_name}': {str(e)}")
            return {"status": "error", "message": str(e)}

    ## ✅ NEW: Delete entire collection
    def delete_collection(self, collection_name: str):
        """Completely delete a collection"""
        try:
            self.client.delete_collection(name=collection_name)
            print(f"✅ Deleted collection '{collection_name}'")
            return {"status": "success", "message": f"Collection '{collection_name}' deleted"}
        except Exception as e:
            print(f"❌ Error deleting collection '{collection_name}': {str(e)}")
            return {"status": "error", "message": str(e)}

    ## add resume
    def add_resume(self, resume_id: str, text: str, metadata, clear_first: bool = False):
        """Add a resume to the collection
        
        Args:
            resume_id: Unique identifier for the resume
            text: Resume text content
            metadata: Additional metadata
            clear_first: If True, clear collection before adding (use for first resume)
        """
        
        return self.load_data(
            collection_name="resume", 
            doc_id=str(resume_id), 
            meta_data=metadata, 
            text=text
        )

    ## add JobPost - ✅ UPDATED: Clear before adding first job
    def add_job_post(self, job_post_id: str, text: str, metadata, clear_first: bool = False):
        """Add a job post to the collection
        
        Args:
            job_post_id: Unique identifier for the job post
            text: Job post text content
            metadata: Additional metadata
            clear_first: If True, clear collection before adding (use for first job)
        """

        
        return self.load_data(
            collection_name="job_post", 
            doc_id=str(job_post_id), 
            meta_data=metadata, 
            text=text
        )
    ## search jobs using resume embeddings
    def search_jobs_for_resume(self,resume_text: str, k=5):
        embeddings=self.get_embedding(resume_text)
        jobs = self.get_collection("job_post").query(
            query_embeddings=[embeddings],
            n_results=k
        )

        output=[]

        for doc, meta, dist, id_  in zip(jobs['documents'], jobs['metadatas'], jobs['distances'], jobs['ids']):
            output.append({
                "id": id_,
                "text": doc,
                "meta_data": meta,
                "distance": dist,
                "collection_name": "job_post",
            })
        return output

    ## search resumes for jobs
    def search_resumes_for_job(self,job_text: str, k=5):
        embeddings=self.get_embedding(job_text)
        resumes = self.get_collection("resume").query(
            query_embeddings=[embeddings],
            n_results=k
        )

        output=[]

        for doc,meta,dist, id_ in zip(resumes.get('documents'), resumes.get('metadatas'), resumes.get('distances'), resumes.get('ids')):

            output.append({
                "id": id_,
                "text": doc,
                "meta_data": meta,
                "distance": dist,
                "collection_name": "resume",
            })
        return output


    ### update the docs
    def update_docs(self,collection_name: str, doc_id: str, text: str, metadata):
        collection = self.get_collection(collection_name)
        collection.delete(ids=[doc_id])
        embeddings = self.get_embedding(text)
        collection.add(documents=[text], embeddings=[embeddings], metadatas=[metadata], ids=[doc_id])

        return {
            "id": doc_id,
            "text": text,
            "meta_data": metadata,
            "embeddings": embeddings,
            "collection_name": collection_name,
            "status":"success"
        }

    ### add policy chunks - seperately not aligned with chatbot model
    def add_school_policy(self, path, school_id):
        
        # path=TextUtility.resolve_path(path)
        # ext = path.suffix.lower()
        
        
        text = TextUtility.extract_text_from_pdf(path)
 
        
        docs = Document(page_content=text)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size= rag_engine.chunk_size,
            chunk_overlap= rag_engine.chunk_overlap,
            separators=rag_engine.separators,
            length_function=len
        )

        chunks = splitter.split_documents([docs])

        vectorstore = Chroma.from_documents(
            documents = chunks,
            embedding=Embedding_model,
            persist_directory=rag_engine.persist_dir,
            collection_name=f"school_{school_id}"
        )
        
        vectorstore.persist()
        return len(chunks)
    
    # retrieval based on school_id
    def get_retrieval_for_school(self, school_id, persist_dir: str = rag_engine.persist_dir):

        vs = Chroma(
            persist_directory=persist_dir,
            embedding_function=Embedding_model,
            collection_name=f"school_{school_id}"
        )

        return vs.as_retriever(
            search_type = rag_engine.search_type,
            search_kwargs = {"k":rag_engine.k}
        )


    # testing purpose not part of rag chain
    def get_context_for_school(self, school_id: str, question: str):
        retriever = self.get_retrieval_for_school(school_id)
        docs = retriever.invoke(question)
        return docs


    
chroma_db_service = ChromaVectorDBService()