# -*- coding: utf-8 -*-
"""Chat with Website Using RAG Pipeline.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1oQX_FmESEYXBZxa7Kn25fZqQngtqHxBH
"""

!pip install -U langchain-community

!pip install langchain-google-genai

!pip install pinecone-client

!pip install gradio

#!pip install langchain openai pinecone-client sentence-transformers beautifulsoup4 requests nltk google.generativeai
from IPython import get_ipython
from IPython.display import display

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone as LongchainPinecone
from langchain.chains import RetrievalQA
#from langchain.llms import Gemini
from langchain_google_genai import GoogleGenerativeAI
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from pinecone import Pinecone, ServerlessSpec
import pinecone
import os
import google.generativeai as genai

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab') # Download the punkt_tab data package

google_api_key = os.environ.get('AIzaSyCSZ6wqUK48UId_A6pkd6BxkTRoeCA4Pa0')
genai.configure(api_key=google_api_key)
# Create the GenerativeModel instance
llm_model = genai.GenerativeModel('gemini-1.5-flash')

def get_website_text(url):
    """Fetches and extracts text content from a given URL."""
    try:
       response = requests.get(url)
       response.raise_for_status() # Raise an exception for bad status codes

       soup = BeautifulSoup(response.content, "html.parser")
       # Extract text content (adjust this based on your website's structure)
       text = soup.get_text()
       return text

    except requests.exceptions.RequestException as e:
       print(f"Error fetching URL: {url} - {e}")
       return None


def preprocess_text(text):
    """Performs basic text preprocessing."""
    # Tokenization
    tokens = word_tokenize(text.lower())
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]

    # Join tokens back into a string
    processed_text = " ".join(filtered_tokens)

    return processed_text


# 1. Load embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 2. Initialize Pinecone
# **Replace with your actual Pinecone initialization**
# Assuming you have already created a Pinecone index and have the necessary environment variables set
# Delete the existing index
# pc.delete_index("website-data")

# Get API key and environment from environment variables
os.environ["PINECONE_API_KEY"] = "pcsk_4vNvY_UJPbuZPtKUeYFWZSs1LjGueU3dxcZSJu8z1NskKRdrx2YqWLGEC1ttBMAUV9PTQ"
os.environ["PINECONE_ENVIRONMENT"] = "us-east-1"

os.environ["GOOGLE_API_KEY"] = "AIzaSyCSZ6wqUK48UId_A6pkd6BxkTRoeCA4Pa0"

# Check if the API key and environment are set
if not os.environ.get("PINECONE_API_KEY") or not os.environ.get("PINECONE_ENVIRONMENT"):
 raise ValueError("PINECONE_API_KEY and PINECONE_ENVIRONMENT environment variables must be set.")

# Initialize Pinecone
pc = Pinecone(
    api_key=os.environ.get("PINECONE_API_KEY"),
    environment=os.environ.get("PINECONE_ENVIRONMENT")
)

# Recreate the index
index_name = "website-data"
if index_name in pc.list_indexes().names():
  print(f"Index '{index_name}' already exists. Skipping creation.")
   # You might want to delete the existing index and recreate it if needed:
    # pc.delete_index(index_name)
     # ... then recreate the index using pc.create_index ...
else:
  # Recreate the index if it doesn't exist
   pc.create_index(
        name=index_name,
        dimension=len(embeddings.embed_documents(["test"])[0]),
        metric="cosine", # Or your preferred metric
        spec=ServerlessSpec(
             cloud="aws",
             region="us-east-1"
             )
        )

# Re-initialize vectorstore
vectorstore = LongchainPinecone.from_existing_index("website-data", embeddings)

# 3. Define target websites (replace with your own)
target_websites = [
    "https://www.washington.edu/",
    "https://www.stanford.edu/",
    "https://und.edu/"
]

# 4. Extract and store website text in Pinecone (uncomment if needed)
for url in target_websites:
  website_text = get_website_text(url)
  if website_text:
    processed_text = preprocess_text(website_text)
    vectorstore.add_texts([processed_text])

# 5. Create RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=GoogleGenerativeAI(model="gemini-1.5-flash", temperature=0),  # Pass the model name as a string and set temperature
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# 6. User Interaction Loop
while True:
  query = input("You: ")

  # Use website search
  if query.startswith("search"):
    response = qa_chain.run(query[6:])
    print(response)
  else:
    print("Please prefix your query with 'search ' for website search.")


"""while True:
  query = input("You: ")

   # Use website search
  if query.startswith("search"):
       response = qa_chain.run(query[6:])
  else:
    # Use Gemini for general text generation
    google_api_key = os.environ.get('GOOGLE_API_KEY')
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(query)
    if response.text: # Check if response.text is not empty
       print(response.text)
    else:
      print("The model did not provide a text response.") # Handle the case where response.text is empty"""

# 6. User Interaction Loop
"""while True:
  query = input("You: ")

  # Use website search
  if query.startswith("search"):
    response = qa_chain.run(query[6:])
    print(response)
  else:
    print("Please prefix your query with 'search ' for website search.")


while True:
  query = input("You: ")

   # Use website search
  if query.startswith("search"):
       response = qa_chain.run(query[6:])
  else:
    # Use Gemini for general text generation
    google_api_key = os.environ.get('GOOGLE_API_KEY')
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(query)
    if response.text: # Check if response.text is not empty
       print(response.text)
    else:
      print("The model did not provide a text response.") # Handle the case where response.text is empty"""