import praw

reddit = praw.Reddit(
    client_id="",
    client_secret="",
    user_agent="<platform>:<12>:<v1> (by u/<username>)",
)

# # Accessing a subreddit
# subreddit = reddit.subreddit('AskReddit')

# # Fetch top posts from the subreddit
# for post in subreddit.top(limit=10):
#     print(post.title, post.selftext)

# Stream all new posts in a subreddit
for submission in reddit.subreddit('news').stream.submissions():
    print(submission.title)
