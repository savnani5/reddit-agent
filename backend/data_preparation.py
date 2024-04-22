import os
import praw
from dotenv import load_dotenv
import pymongo
import pandas as pd
from mistralai.client import MistralClient
from llama_index.core.settings import Settings
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables from .env file
load_dotenv()

# Reddit API Credentials
reddit = praw.Reddit(
    client_id="",
    client_secret="",
    user_agent="<platform>:<12>:<v1> (by u/<userid>)",
)

# Mistral API Key and MongoDB URI
api_key = os.environ.get("MISTRAL_API_KEY")
mongo_uri = os.environ.get("MONGO_URI")

def connect_mongodb():
    client = pymongo.MongoClient(mongo_uri)
    db = client["vector-database"]
    collection = db["vector-collection"]
    return collection

def get_embedding(text, client):
    text = text.replace("\n", " ")
    embeddings_batch_response = client.embeddings(
        model="mistral-embed",
        input=text,
    )
    return embeddings_batch_response.data[0].embedding

def recursive_split_and_store(text, client, collection, max_length=512):
    # Manually split text into chunks of max_length
    chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]

    # Store each chunk with its embedding
    for chunk in chunks:
        if chunk.strip():  # Ensure chunk has content
            embedding = get_embedding(chunk, client)
            collection.insert_one({"text_chunks": chunk, "embedding": embedding})


def fetch_reddit_data(subreddit_name, limit=10):
    subreddit = reddit.subreddit(subreddit_name)
    client = MistralClient(api_key=api_key)
    collection = connect_mongodb()

    # Fetch top posts
    posts = list(subreddit.hot(limit=limit))
    for post in posts:
        print(post.title)
        recursive_split_and_store(post.title + " " + post.selftext, client, collection)

        # Fetch top comments for each post
        post.comment_sort = 'top'
        post.comments.replace_more(limit=0)  # Load all top comments
        comments = post.comments.list()[:100]  # Adjust number of comments as needed
        for comment in comments:
            recursive_split_and_store(comment.body, client, collection)

    return "Data fetched and stored in MongoDB."


if __name__ == "__main__":
    subreddit_name = 'AskReddit'
    print(fetch_reddit_data(subreddit_name, 2))