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
import numpy as np

# Download necessary NLTK data
nltk.download('wordnet')

# Text preprocessing function
def preprocess(text):
    result = []
    for token in simple_preprocess(text):
        if token not in STOPWORDS and len(token) > 3:
            result.append(lemmatizer.lemmatize(token))
    return result

lemmatizer = WordNetLemmatizer()
preprocess_udf = udf(lambda x: preprocess(x), ArrayType(StringType()))

# Distributed topic modeling function
def distributed_topic_modeling(spark, documents, num_topics=5, num_words=10):
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

    # Collect the corpus as a list of lists of (word_id, count) tuples
    corpus = vectorized_df.select("features").rdd.map(lambda row: [(i, val) for i, val in enumerate(row["features"].toArray()) if val > 0]).collect()

    # Create dictionary from vocabulary
    dictionary = corpora.Dictionary([cv_model.vocabulary])

    # Train LDA model
    lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, passes=10)

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
