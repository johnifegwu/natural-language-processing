import praw
import nltk
from nltk.corpus import stopwords
from collections import Counter
import string

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Reddit API authentication
def reddit_auth():
    reddit = praw.Reddit(client_id='WjgGkv2I08zPEOJQ_ePBaA',
                         client_secret='iE-_WYpcAGVdAW5iuXR8Z7WF6W2uUg',
                         user_agent='johnifegwu')
    return reddit

# Fetch Reddit posts from the programming subreddit
def fetch_reddit_posts(reddit, topic, subreddit='programming', limit=100):
    posts = []
    for submission in reddit.subreddit(subreddit).search(topic, limit=limit):
        posts.append(submission.title + " " + submission.selftext)
    return posts

# Preprocess the text: Remove stopwords and punctuation
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    words = nltk.word_tokenize(text)
    words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]
    return words

# Find common subtopics by counting word frequency
def find_common_subtopics(posts, top_n=10):
    all_words = []
    for post in posts:
        all_words.extend(preprocess_text(post))
    
    # Count the frequency of each word
    word_counts = Counter(all_words)
    
    # Return the most common subtopics
    return word_counts.most_common(top_n)

# Main function to get the most common subtopics on Reddit
def main(topic):
    reddit = reddit_auth()
    
    # Step 1: Fetch Reddit posts for the given topic
    posts = fetch_reddit_posts(reddit, topic)
    
    # Step 2: Find common subtopics from the posts
    common_subtopics = find_common_subtopics(posts)
    
    print(f"Most common subtopics for '{topic}' on Reddit:")
    for subtopic, count in common_subtopics:
        print(f"{subtopic}: {count} mentions")

# Run the main function with a broad topic like 'programming'
if __name__ == "__main__":
    topic = "programming"
    main(topic)
