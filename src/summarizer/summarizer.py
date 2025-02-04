import pandas as pd
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from scipy.stats import ttest_rel

# Step 1: Load the Dataset
def load_dataset(file_path):
    df = pd.read_csv(file_path)
    print("Dataset loaded successfully!")
    return df

# Step 2: Generate Summaries using different LLMs
def generate_summaries(texts, model_name):
    summarizer = pipeline("summarization", model=model_name)
    summaries = []
    for text in texts:
        # Handle missing/NaN values
        if pd.isna(text) or not isinstance(text, str):
            summaries.append("")  # Append an empty string for invalid data
            continue
        # Truncate text to fit within the model's token limit (1024 tokens for most models)
        truncated_text = text[:1024] 
        summary = summarizer(truncated_text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
        summaries.append(summary)
    return summaries

# Step 3: Generate Embeddings
def generate_embeddings(texts, embedding_model):
    embeddings = embedding_model.encode(texts, convert_to_tensor=True)
    return embeddings

# Step 4: Calculate Similarity
def calculate_similarity(original_embeddings, summary_embeddings):
    similarity_scores = util.pytorch_cos_sim(original_embeddings, summary_embeddings)
    return similarity_scores.diag().tolist()

# Step 5: Add Summaries to the Dataset
def add_summaries_to_dataset(df, abstracts, model_names):
    for model_name in model_names:
        print(f"Generating summaries using {model_name}...")
        summaries = generate_summaries(abstracts, model_name)
        df[f'{model_name}_summary'] = summaries
    return df

# Step 6: Save Dataset with Summaries
def save_dataset_with_summaries(df, output_file):
    df.to_csv(output_file, index=False)
    print(f"Dataset with summaries saved to {output_file}!")

# Step 7: Evaluate Models and Save Similarity Scores
def evaluate_models(df, abstracts, model_names, embedding_model, scores_file):
    original_embeddings = generate_embeddings(abstracts, embedding_model)
    results = {}
    
    for model_name in model_names:
        summaries = df[f'{model_name}_summary'].tolist()
        summary_embeddings = generate_embeddings(summaries, embedding_model)
        similarity_scores = calculate_similarity(original_embeddings, summary_embeddings)
        results[model_name] = similarity_scores
    
    # Save similarity scores to a CSV file
    scores_df = pd.DataFrame(results)
    scores_df.to_csv(scores_file, index=False)
    print(f"Similarity scores saved to {scores_file}!")
    
    return results

# Step 8: Perform Paired t-tests
def perform_statistical_tests(scores_df, model_names):
    print("\nPerforming paired t-tests...")
    for i in range(len(model_names)):
        for j in range(i + 1, len(model_names)):
            model1 = model_names[i]
            model2 = model_names[j]
            stat, p = ttest_rel(scores_df[model1], scores_df[model2])
            print(f"\nPaired t-test between {model1} and {model2}:")
            print(f"Statistic={stat}, p-value={p}")
            if p < 0.05:
                print(f"There is a significant difference between {model1} and {model2}.")
            else:
                print(f"There is NO significant difference between {model1} and {model2}.")

# Main Execution
if __name__ == "__main__":
    load_dotenv()
    uri = os.environ['URI_KEY']
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Specify the database and collection
    db = client['my_database'] 
    collection = db['arxiv_collection'] 

    # Fetch data from MongoDB
    data_from_db = collection.find()
    data_list = list(data_from_db)
    df = pd.DataFrame(data_list)
    # df.to_csv('arxiv-data.csv', index=True)

    # File paths
    output_file = "abstract_with_summaries.csv"  # Output file with summaries
    scores_file = "similarity_scores.csv"  # File to store similarity scores
    
    # Ensure the 'Abstract' column is treated as strings and handle missing values
    df['Abstract'] = df['Abstract'].astype(str)  # Convert all values to strings
    abstracts = df['Abstract'].tolist()  # Extract the 'Abstract' column

    # Define the LLMs to compare
    model_names = [
        "facebook/bart-large-cnn",  # BART model
        "t5-small",                 # T5 model
        "google/pegasus-xsum"   # Pegasus model         
    ]

    # Add summaries to the dataset
    df = add_summaries_to_dataset(df, abstracts, model_names)

    # Save the dataset with summaries
    save_dataset_with_summaries(df, output_file)

    # Load embedding model (Sentence-BERT)
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    # Evaluate models and save similarity scores
    similarity_results = evaluate_models(df, abstracts, model_names, embedding_model, scores_file)

    # Load similarity scores for statistical testing
    scores_df = pd.read_csv(scores_file)

    # Perform paired t-tests
    perform_statistical_tests(scores_df, model_names)