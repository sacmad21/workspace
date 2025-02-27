import azure.functions as func
import logging
import os
#from groq import Groq
from typing import Dict, List
import logging

import uuid
import os
from datetime import datetime
import traceback
import logging

import os
import traceback
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    jsonify,
    send_from_directory,
)
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory
from qdrant_client import QdrantClient

from langchain_qdrant import Qdrant
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_openai import ChatOpenAI

# from utils.mongo_utils import insert_data
from dotenv import load_dotenv
from langfuse.callback import CallbackHandler
import langchain_community

langchain_community.verbose = True

load_dotenv()
store = {}

# Dev Account
QDRANT_URL = "http://qdrantrg4nozl67fgkq.centralindia.azurecontainer.io:6333/"

# Prod Account
# QDRANT_URL = "http://qdrantk3ufmw42nef2i.southeastasia.azurecontainer.io:6333/"


QDRANT_URL = "https://9d76c474-e153-4feb-b5dc-23a6a86271c9.europe-west3-0.gcp.cloud.qdrant.io:6333"
QDRANT_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwiZXhwIjoxNzQ2NjA5ODYzfQ.0ZVdq3NkjhI4-ytgwRS7ehCViCOJbY2jpXo6eSYW7Dg"


GROQ_URL = "https://api.groq.com/openai/v1"
#GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_API_KEY_VALUE_SMK = "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"
GROQ_API_KEY_VALUE_PRASAD = "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"


TOGETHER_URL = "https://api.together.xyz/v1"
TOGETHER_MODEL ="meta-llama/Llama-3.3-70B-Instruct-Turbo"
TOGETHER_API_KEY = "75830ae44792e6cdb938cd1c1d1806c33cf27d012c2c441d67a4465ca0901070"



HF_INFERENCE_KEY = "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"


llm = ChatOpenAI(model=GROQ_MODEL, base_url=GROQ_URL,  api_key=GROQ_API_KEY_VALUE_PRASAD, verbose=True)


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    "API for chat history"
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]



genAIObjects = {

    "divorce" : { 
        "retriever" : "none",
        "retrieverCreated" : False
        },

    "mp_finance_faq_csv" : {
        "retriever" : "none",
        "retrieverCreated" : False
        },
    
    "MPdata" : {
        "retriever" : "none",
        "retrieverCreated" : False
    }

}

collection_param = {

    "divorce" :{ 
        "prompt" :"You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.",
        "resultWithRefrences" : True
        },

    "mp_finance_faq_csv" :
        {
        "prompt": """You are an assistant for question-answering tasks from Venkatesh Developers. 
                        Be Professional. Use the following pieces of retrieved context to answer the question. 
                            If you don't know the answer, just say that you 'we will get back to you soon'. 
                                Use three sentences maximum and keep the answer concise.""",
        "resultWithRefrences" : True
        },
    
    "MPdata" : {
        "prompt" : "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.",
        "resultWithRefrences" : True
    }
}




def getRefrences(context) :
    
    for i in context:
        # use source for divorce and filename for MP_data
        references.append(i.metadata["source"].split(".")[0].split('/')[-1])            
        references = list(set(references))
        refs = '\n*'.join(references)     

    return list(set(references))


# 5-sec
# qdrant_client = QdrantClient(url=QDRANT_URL, prefer_grpc=False)
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


logging.info("Embeddings initializing started")
embeddings = HuggingFaceInferenceAPIEmbeddings(
        api_key=HF_INFERENCE_KEY,
        model_name="intfloat/multilingual-e5-base",
        )
logging.info("Embeddings initializing Completed")



def answerInSpecific(user_input: str, session_id: str, collection: str) -> str:
    """
    API for advance retrival information chat
    """

    # https://python.langchain.com/v0.1/docs/use_cases/question_answering/chat_history/#returning-sources


    logging.info("Answer In Specifc Started :: " + user_input )


    try:
        if not user_input or not session_id:
            return jsonify({"error": "Missing message or session ID"}), 400
        
        

        if qdrant_client.collection_exists(collection_name=collection):
            if not genAIObjects[collection]["retrieverCreated"] :
                        
                logging.info(f"The selected qdrtant {collection} exists")
                retriever = Qdrant(
                    client=qdrant_client,
                    collection_name=collection,
                    embeddings=embeddings,
                ).as_retriever()

                genAIObjects[collection]["retriever"] = retriever
                genAIObjects[collection]["retrieverCreated"] = True
            
            retriever = genAIObjects[collection]["retriever"]

            contextualize_q_system_prompt = """Given a chat history and the latest user question \
            which might reference context in the chat history, formulate a standalone question \
            which can be understood without the chat history. Do NOT answer the question, \
            just reformulate it if needed and otherwise return it as is."""
            contextualize_q_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", contextualize_q_system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )
            history_aware_retriever = create_history_aware_retriever(
                llm, retriever, contextualize_q_prompt
            )

            qa_system_prompt = """You are an assistant for question-answering tasks. \
                Use the following pieces of retrieved context to answer the question. \
                If you don't know the answer, just say that you don't know. \
                Use three sentences maximum and keep the answer concise.\

                {context}"""
            
            if collection in collection_param :
                prompt = collection_param[collection]["prompt"]
                qa_system_prompt = f"{prompt} \n Context:::" + "{context}"


            qa_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", qa_system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )
            question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

            rag_chain = create_retrieval_chain(
                history_aware_retriever, question_answer_chain
            )

            conversational_rag_chain = RunnableWithMessageHistory(
                rag_chain,
                get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer",
            )

            logging.info("chain initialzation started")
            result = conversational_rag_chain.invoke(
                {"input": user_input},
                config={
                    "configurable": {"session_id": session_id}
                },
            )

            logging.info("Result", result)
            references = []
            context = result["context"]

            return result["answer"]     
        
#           return "*Answer*\n" + result["answer"] + "\n*We refered* :\n" + refs
#           return jsonify( {"content": result["answer"], "references": list(set(references))})

               
        else:
            return "The selected collection does not exist" 

    except Exception as e:
        print(f"Error occurred: {e}")
        print("ERROR", traceback.format_exc())
#       return jsonify({"error": "Internal Server Error"}), 500
        return ("We are working on all the customer queries, We will get back to you on query as soon as possible.")


