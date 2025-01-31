import pandas as pd
import gradio as gr



from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import Document
# from googletrans import Translator

OPEN_API_KEY="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"
# Load FAQ Data
faq_file = "/home/devzone/MyCenter/genAIProj/llamaWork/govBotApp/faqApp/faq .csv"  # Update with actual path
df = pd.read_csv(faq_file)


# Convert CSV to LangChain Documents
documents = [
    Document(page_content=row['question'] + " " + row['answer'], metadata={"qno": row['qNo']})
    for _, row in df.iterrows()
]

# Split text into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPEN_API_KEY)

# Create FAISS In-Memory Vector Store
vector_store = FAISS.from_documents(chunks, embeddings)

# Initialize OpenAI Model
llm = ChatOpenAI(
    model_name="llama-3.3-70b-versatile", 
    base_url="https://api.groq.com/openai/v1",
    api_key="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",
    temperature=0
    )


# Define conversation memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Define structured response template
response_template = PromptTemplate(
    input_variables=["question", "answer"],
    template="""
    **User Query:** {question}
    
    **Expert Response:** {answer}
    
    Let me know if you have more queries!
    """
)

# Create ConversationalRetrievalChain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vector_store.as_retriever(),
    memory=memory
)

# Initialize Translator
#translator = Translator()



# ChatBot Session State
session_state = {"welcome_sent": False, "query_session": False, "promotion_sent": False}

# Function to handle chatbot conversation
def chatbot(query, language):
    global session_state

    # Translate query to English if needed
    if language != "English":
        # query = translator.translate(query, src=language.lower(), dest="en").text
        query = query

    # Welcome Message
    if query.lower() == "hi":
        session_state["welcome_sent"] = True
        return "Welcome! How can I assist you with real estate queries today?"

    # Start Q/A Session
    if session_state["welcome_sent"] and not session_state["query_session"]:
        session_state["query_session"] = True
        return "Feel free to ask me any real estate-related question."

    # If user is in Q/A session
    if session_state["query_session"]:
        result = qa_chain({"question": query})
        answer = result["answer"]

        # Translate back if needed
        if language != "English":
#           answer = translator.translate(answer, src="en", dest=language.lower()).text
            answer = answer + ""


        return response_template.format(question=query, answer=answer)

    # End of Q/A session - Ask for Promotional Offer
    if session_state["query_session"] and not session_state["promotion_sent"]:
        session_state["query_session"] = False
        session_state["promotion_sent"] = True
        return "We have launched a new project, are you interested to know about it?"

    # If user says Yes → Send Brochure
    if session_state["promotion_sent"] and query.lower() in ["yes", "haan", "haa", "હા", "हाँ"]:
        return "Great! Here is the brochure for our new project: [Download Brochure](#)"

    # If user says No → Exit Message
    if session_state["promotion_sent"] and query.lower() in ["no", "nahin", "નહી", "नहीं"]:
        return "Thank you for your time! I hope your queries were resolved. Have a great day!"

    return "I'm here to assist you. Let me know if you have any questions."

# Create Gradio UI
interface = gr.Interface(
    fn=chatbot,
    inputs=[
        gr.Textbox(label="Ask a real estate question or say 'Hi' to start"),
        gr.Radio(["English", "Hindi", "Marathi", "Gujarati"], label="Select Language", value="English")
    ],
    outputs="text",
    title="Multilingual Real Estate Q/A Chatbot",
    description="Ask real estate-related questions in English, Hindi, Marathi, or Gujarati."
)

# Run chatbot
if __name__ == "__main__":
    interface.launch()
