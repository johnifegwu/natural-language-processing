import gensim
from gensim import corpora
from gensim.models import TfidfModel
from gensim.similarities import MatrixSimilarity
from gensim.parsing.preprocessing import STOPWORDS
from gensim.utils import simple_preprocess
from nltk.stem import WordNetLemmatizer
import nltk
import numpy as np

# Download necessary NLTK data
nltk.download('wordnet')

def document_similarity(documents, query=None):
    """
    Measure similarity between documents or between a query and all documents.
    
    Args:
    documents (list): List of strings, where each string is a document.
    query (str, optional): A query string to compare against all documents.
                           If None, compares all documents with each other.
    
    Returns:
    numpy.ndarray: Similarity matrix if query is None, 
                   or 1D array of similarities if query is provided.
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
    
    # Create TF-IDF model
    tfidf = TfidfModel(corpus)
    
    # Transform corpus to TF-IDF space
    corpus_tfidf = tfidf[corpus]
    
    # Create similarity index
    index = MatrixSimilarity(corpus_tfidf, num_features=len(dictionary))
    
    if query is None:
        # Compare all documents with each other
        similarities = np.zeros((len(documents), len(documents)))
        for i, doc in enumerate(corpus_tfidf):
            sim = index[doc]
            similarities[i] = sim
    else:
        # Compare query with all documents
        query_bow = dictionary.doc2bow(preprocess(query))
        query_tfidf = tfidf[query_bow]
        similarities = index[query_tfidf]
    
    return similarities

# Example usage
documents = [
    "The quick brown fox jumps over the lazy dog.",
    "Machine learning is a subset of artificial intelligence.",
    "Python is a popular programming language for data science.",
    "Natural language processing deals with interactions between computers and human language.",
    "Deep learning models can achieve state-of-the-art results in many tasks."
]

# Compare all documents with each other
sim_matrix = document_similarity(documents)
print("Similarity Matrix:")
print(sim_matrix)

# Compare a query with all documents
query = "Artificial intelligence and machine learning in Python"
sim_vector = document_similarity(documents, query)
print("\nSimilarity to query:")
for i, sim in enumerate(sim_vector):
    print(f"Document {i+1}: {sim:.4f}")

# Find the most similar document to the query
most_similar_index = sim_vector.argmax()
print(f"\nMost similar document to the query: Document {most_similar_index + 1}")
print(f"Content: {documents[most_similar_index]}")
