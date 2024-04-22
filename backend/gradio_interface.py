import gradio as gr
import time
from data_preparation import fetch_reddit_data
from qa_system import qna

def reddit_fetch_interface(subreddit_name):
    print("creating the database......")
    time.sleep(5)
    return "vectordb created"
    # return fetch_reddit_data(subreddit_name, 10)

reddit_fetch_ui = gr.Interface(
    fn=reddit_fetch_interface,
    inputs=gr.Textbox(placeholder="AskReddit", label="Subreddit Name"),
    outputs="text",
    description="Enter the name of the subreddit to fetch and store top posts and comments."
)

chatbot_interface = gr.Interface(
    fn=qna,
    inputs=gr.Textbox(placeholder="Enter Your Question", label="Enter Your Question"),
    outputs=[
        gr.Textbox(label="Mistral Answer"),
        gr.Textbox(label="Retrieved Documents from MongoDB Atlas")
    ],
    description="Ask any question to get answers based on the fetched Reddit data."
)

iface = gr.TabbedInterface([reddit_fetch_ui, chatbot_interface], ["Fetch Reddit Data", "Chatbot"])
iface.launch()
