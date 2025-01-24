import azure.functions as func
import logging
import os
from groq import Groq
from typing import Dict, List

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
from utils.mongo_utils import insert_data
from dotenv import load_dotenv
from langfuse.callback import CallbackHandler



load_dotenv()
store = {}

MONGO_URI = "mongodb+srv://vprasannakumar:RNNLJduqLMJ0GrMf@pwc.2imj7.mongodb.net/?retryWrites=true&w=majority&appName=pwc"
MONGO_DATABASE = "pwc"
MONGO_HISTORY_COLLECTION = "history"
QDRANT_URL = "http://qdrantrg4nozl67fgkq.centralindia.azurecontainer.io:6333/"
                     

GROQ_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"
LANGFUSE_PUBLIC_KEY = "pk-lf-28abb1b5-7442-4c09-8125-1ea144526f18"
LANGFUSE_SECRET_KEY = "sk-lf-f04bd683-d17c-4f89-81cc-ab7e5fa97f2b"
LANGFUSE_HOST = "https://cloud.langfuse.com"
HF_INFERENCE_KEY = "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"
GROQ_API_KEY_VALUE = "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"


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    "API for chat history"
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


langfuse_handler = CallbackHandler(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host=LANGFUSE_HOST,
)

client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
mongo_db = client[MONGO_DATABASE]
llm = ChatOpenAI(model=GROQ_MODEL, base_url=GROQ_URL, api_key=GROQ_API_KEY_VALUE)

def answerInSpecific(user_input: str, session_id: str, collection: str) -> str:
    """
    API for advance retrival information chat
    """
    # https://python.langchain.com/v0.1/docs/use_cases/question_answering/chat_history/#returning-sources
    try:
        

        if not user_input or not session_id:
            return jsonify({"error": "Missing message or session ID"}), 400
        print("Embeddings initializing started")
        embeddings = HuggingFaceInferenceAPIEmbeddings(
            api_key=HF_INFERENCE_KEY,
            model_name="intfloat/multilingual-e5-base",
        )
        print("Embeddings initializing Completed")

        qdrant_client = QdrantClient(url=QDRANT_URL, prefer_grpc=False)
        if qdrant_client.collection_exists(collection_name=collection):
            print(f"The selected qdrtant {collection} exists")
            retriever = Qdrant(
                client=qdrant_client,
                collection_name=collection,
                embeddings=embeddings,
            ).as_retriever()
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

            print("chain initialzation started")
            result = conversational_rag_chain.invoke(
                {"input": user_input},
                config={
                    "configurable": {"session_id": session_id},
                    "callbacks": [langfuse_handler],
                },
            )

            print("Results insertion into Mongo")
            insert_data(
                data={
                    "session_id": session_id,
                    "user_message": user_input,
                    "ai_response": result["answer"],
                },
                collection=mongo_db[MONGO_HISTORY_COLLECTION],
            )
            print("Result", result)
            references = []
            context = result["context"]
            
            for i in context:
                # use source for divorce and filename for MP_data
                references.append(i.metadata["source"].split(".")[0].split('/')[-1])
            
            references = list(set(references))

            refs = '\n*'.join(references)                
#           return jsonify( {"content": result["answer"], "references": list(set(references))} )
            return "*Answer*\n" + result["answer"] + "\n*We refered* :\n" + refs
        else:
#           return jsonify({"content": "The selected collection does not exist"})
            return "The selected collection does not exist" 

    except Exception as e:
        print(f"Error occurred: {e}")
        print("ERROR", traceback.format_exc())
#       return jsonify({"error": "Internal Server Error"}), 500
        return ("Internal Server Error")

#response = answerInSpecific("How to apply for custody of child ? " , "sess021123" , "divorce")
#print(response)


