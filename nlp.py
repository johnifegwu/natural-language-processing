import gensim
from gensim import corpora
from gensim.models import LdaModel, LsiModel
from gensim.parsing.preprocessing import STOPWORDS
from gensim.utils import simple_preprocess
from nltk.stem import WordNetLemmatizer
import nltk

# Download necessary NLTK data
nltk.download('wordnet')

def topic_modeling(documents, num_topics=5, model_type='lda'):
    """
    Perform topic modeling on a corpus of documents using Gensim.
    
    Args:
    documents (list): List of strings, where each string is a document.
    num_topics (int): Number of topics to extract (default: 5).
    model_type (str): Type of model to use - 'lda' or 'lsa' (default: 'lda').
    
    Returns:
    list: List of topics, where each topic is a list of (word, weight) tuples.
    """
    
    # Text preprocessing
    def preprocess(text):
        result = []
        for token in simple_preprocess(text):
            if token not in STOPWORDS and len(token) > 3:
                result.append(lemmatizer.lemmatize(token))
        return result
    
    lemmatizer = WordNetLemmatizer()
    processed_docs = [preprocess(doc) for doc in documents]
    
    # Create dictionary
    dictionary = corpora.Dictionary(processed_docs)
    
    # Create corpus
    corpus = [dictionary.doc2bow(doc) for doc in processed_docs]
    
    # Train model
    if model_type.lower() == 'lda':
        model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, 
                         random_state=42, update_every=1, chunksize=100, 
                         passes=10, alpha='auto', per_word_topics=True)
    elif model_type.lower() == 'lsa':
        model = LsiModel(corpus=corpus, id2word=dictionary, num_topics=num_topics)
    else:
        raise ValueError("Invalid model_type. Choose 'lda' or 'lsa'.")
    
    # Extract topics
    topics = model.print_topics(num_words=10)
    
    # Format topics for better readability
    formatted_topics = []
    for topic in topics:
        topic_terms = [(term.split('*')[1].strip().replace('"', ''), float(term.split('*')[0])) 
                       for term in topic[1].split(' + ')]
        formatted_topics.append(topic_terms)
    
    return formatted_topics

# Example usage
documents = [
    "The quick brown fox jumps over the lazy dog.",
    "Machine learning is a subset of artificial intelligence.",
    "Python is a popular programming language for data science.",
    "Natural language processing deals with interactions between computers and human language.",
    "Deep learning models can achieve state-of-the-art results in many tasks."
]

lda_topics = topic_modeling(documents, num_topics=3, model_type='lda')
print("LDA Topics:")
for i, topic in enumerate(lda_topics):
    print(f"Topic {i + 1}: {topic}")

lsa_topics = topic_modeling(documents, num_topics=3, model_type='lsa')
print("\nLSA Topics:")
for i, topic in enumerate(lsa_topics):
    print(f"Topic {i + 1}: {topic}")
