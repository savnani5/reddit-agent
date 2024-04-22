import os
from dotenv import load_dotenv
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage  # Add this line
from data_preparation import get_embedding
import pymongo

# Load environment variables from .env file
load_dotenv()

# Now you can safely use os.environ to access your variables
api_key = os.environ["MISTRAL_API_KEY"]
mongo_uri = os.environ["MONGO_URI"]

def connect_mongodb():
    mongo_url = os.environ["MONGO_URI"]
    client = pymongo.MongoClient(mongo_url)
    db = client["vector-database"]
    collection = db["vector-collection"]
    print("Connected to MongoDB")  # Debug statement
    return collection

def find_similar_documents(embedding):
    collection = connect_mongodb()
    documents = list(
        collection.aggregate([
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": embedding,
                    "numCandidates": 20,
                    "limit": 10
                }
            },
            {"$project": {"_id": 0, "text_chunks": 1}}
        ]))
    return documents

def qna(users_question):
    # Set up Mistral client
    client = MistralClient(api_key=api_key)

    question_embedding = get_embedding(users_question, client)
    print("-----Here is user question------")
    print(users_question)
    documents = find_similar_documents(question_embedding)
    
    print("-----Retrieved documents------")
    print(documents)
    for doc in documents:
        doc['text_chunks'] = doc['text_chunks'].replace('\n', ' ')
    
    for document in documents:
        print(str(document) + "\n")

    context = " ".join([doc["text_chunks"] for doc in documents])
    template = f"""
    You are an expert who loves to help people! Given the following context sections, answer the
    question using only the given context. If you are unsure say "Sorry, I don't know how to help with that."

    Context sections:
    {context}

    Question:
    {users_question}

    Answer:
    """
    messages = [ChatMessage(role="user", content=template)]
    chat_response = client.chat(
        model="mistral-large-latest",
        messages=messages,
    )
    formatted_documents = '\n'.join([doc['text_chunks'] for doc in documents])
    return chat_response.choices[0].message.content, formatted_documents

if __name__ == "__main__":
    import sys
    question = sys.argv[1] if len(sys.argv) > 1 else 'Enter your question here'
    print(qna(question))
