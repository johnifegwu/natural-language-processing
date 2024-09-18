from pyspark.sql import SparkSession
from pyspark.ml.feature import CountVectorizer
from pyspark.sql.functions import udf, col
from pyspark.sql.types import ArrayType, StringType
import gensim
from gensim import corpora
from gensim.models import LdaModel
from gensim.parsing.preprocessing import STOPWORDS
from gensim.utils import simple_preprocess
from nltk.stem import WordNetLemmatizer
import nltk

# Download necessary NLTK data
nltk.download('wordnet')

    """
    Perform distributed topic modeling on a large corpus of documents using Gensim and Apache Spark.
    
    Args:
    spark (SparkSession): The active Spark session.
    documents (list or RDD): List of strings or RDD of strings, where each string is a document.
    num_topics (int): Number of topics to extract (default: 5).
    num_words (int): Number of words to show for each topic (default: 10).
    
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
    preprocess_udf = udf(lambda x: preprocess(x), ArrayType(StringType()))
    
    # Create DataFrame from documents
    if isinstance(documents, list):
        df = spark.createDataFrame([(doc,) for doc in documents], ["text"])
    else:  # Assume it's an RDD
        df = documents.toDF(["text"])
    
    # Preprocess documents
    processed_df = df.withColumn("words", preprocess_udf(col("text")))
    
    # Create CountVectorizer model
    cv = CountVectorizer(inputCol="words", outputCol="features", vocabSize=10000, minDF=5)
    cv_model = cv.fit(processed_df)
    
    # Transform the data
    vectorized_df = cv_model.transform(processed_df)
    
    # Collect the corpus as a list of lists
    corpus = vectorized_df.select("features").rdd.map(lambda row: row[0].toArray()).collect()
    
    # Create dictionary
    dictionary = corpora.Dictionary.from_corpus(corpus, id2word=cv_model.vocabulary)
    
    # Train LDA model
    
    # Extract topics
    topics = lda_model.print_topics(num_words=num_words)
    
    # Format topics for better readability
    formatted_topics = []
    for topic in topics:
        topic_terms = [(term.split('*')[1].strip().replace('"', ''), float(term.split('*')[0])) 
                       for term in topic[1].split(' + ')]
        formatted_topics.append(topic_terms)
    
    return formatted_topics

# Example usage
if __name__ == "__main__":
    # Create Spark session
    spark = SparkSession.builder \
        .appName("DistributedTopicModeling") \
        .getOrCreate()

    # Example documents (in a real scenario, this could be millions of documents)
    documents = [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning is a subset of artificial intelligence.",
        "Python is a popular programming language for data science.",
        "Natural language processing deals with interactions between computers and human language.",
        "Deep learning models can achieve state-of-the-art results in many tasks.",
        # ... (add more documents here)
    ]

    # Convert documents to RDD (for demonstration; in practice, you might load from a distributed file system)
    doc_rdd = spark.sparkContext.parallelize(documents)

    # Perform distributed topic modeling
    topics = distributed_topic_modeling(spark, doc_rdd, num_topics=3, num_words=5)

    print("Discovered Topics:")
    for i, topic in enumerate(topics):
        print(f"Topic {i + 1}: {topic}")

    # Stop Spark session
    spark.stop()
