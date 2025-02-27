from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Load Medication Dataset
loader = TextLoader("medication_data.txt")
documents = loader.load()

# Split into Chunks
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# Create FAISS Index
vector_store = FAISS.from_documents(texts, OpenAIEmbeddings())

# Save Index
vector_store.save_local("faiss_index")
