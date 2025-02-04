import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pandas as pd
import re
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi


# Initialize UserAgent for headers
ua = UserAgent()
userAgent = ua.random
headers = {'User-Agent': userAgent}

# List of arXiv categories to scrape
categories = ['cs.CV', 'cs.CL', 'cs.CR','cs.DC','cs.DS','cs.OS','cs.AI','cs.DB','cs.LG','cs.NE','cs.HC','cs.IR','cs.IT','cs.RO','cs.SI','cs.SE','cs.SY']

# Lists to store extracted data
all_data = []

# Loop through each category
for category in categories:
    print(f"Scraping category: {category}")
    
    # Fetch the first page to get the total number of entries
    base_url = f'https://arxiv.org/list/{category}/recent'
    try:
        page = requests.get(base_url, headers=headers)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, "html.parser")
        
        # Extract the total number of entries from the paging div
        paging_div = soup.find('div', class_='paging')
        if paging_div:
            total_entries_text = paging_div.text.strip()
            total_entries = int(re.search(r'Total of (\d+) entries', total_entries_text).group(1))
            print(f"Total entries in {category}: {total_entries}")
        else:
            print(f"Could not find total entries for {category}. Skipping...")
            continue
        
        # Construct the URL to fetch all entries in one go
        url = f'https://arxiv.org/list/{category}/recent?skip=0&show={total_entries}'
        # url = f'https://arxiv.org/list/{category}/recent?skip=0&show={1}'
        print(f"Fetching all entries from: {url}")
        
        # Fetch the page with all entries
        page = requests.get(url, headers=headers)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, "html.parser")
        
        # Process each article on the page
        for dt in soup.select('dl#articles dt'):
            dd = dt.find_next('dd')
            
            # Extract Title and remove "Title:\n" or any unwanted prefixes
            title_div = dd.find('div', class_='list-title')
            if title_div:
                # Get the text content of the div and remove "Title:" and leading/trailing whitespace
                title = title_div.get_text(strip=True).replace('Title:', '').strip()
            else:
                title = None
            
            # Extract Authors
            authors_div = dd.find('div', class_='list-authors')
            authors = [a.text.strip() for a in authors_div.find_all('a')] if authors_div else []
            
            # Extract PDF Link and make it an absolute URL
            pdf_link = dt.find('a', {'title': 'Download PDF'})
            pdf_url = f"https://arxiv.org{pdf_link['href']}" if pdf_link else None  # Prefix with https://arxiv.org
            
            # Extract HTML Link
            html_link = dt.find('a', {'title': 'View HTML'})
            html_url = html_link['href'] if html_link else None  # Use the full URL directly
            
            # Extract Subjects (Tags) and remove brackets and their contents
            subjects_div = dd.find('div', class_='list-subjects')
            subjects = []
            if subjects_div:
                subjects_text = subjects_div.text.replace('Subjects:', '').strip()
                # Use regex to remove brackets and their contents
                subjects_text = re.sub(r'\([^)]*\)', '', subjects_text)
                subjects = [s.strip() for s in subjects_text.split(';')]
            
            # Extract Abstract from the HTML page
            abstract = None
            if html_url:
                try:
                    # Fetch the HTML page of the paper
                    paper_page = requests.get(html_url, headers=headers)
                    paper_page.raise_for_status()
                    paper_soup = BeautifulSoup(paper_page.content, "html.parser")
                    
                    # Find the abstract (inside a div with class 'ltx_abstract')
                    abstract_div = paper_soup.find('div', class_='ltx_abstract')
                    if abstract_div:
                        # Extract the text inside the <p> tag within the abstract div
                        abstract_p = abstract_div.find('p')
                        if abstract_p:
                            abstract = abstract_p.get_text(strip=True)
                except requests.exceptions.RequestException as e:
                    print(f"Failed to fetch abstract from {html_url}: {e}")
            
            # Append data to the list
            all_data.append({
                'Category': category,
                'Link': pdf_url,
                'Title': title,
                'Authors': ", ".join(authors),
                'Tags': ", ".join(subjects),
                'Abstract': abstract
            })

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {base_url}: {e}")

# Create a DataFrame
df = pd.DataFrame(all_data)
df_cleaned = df.drop_duplicates(subset=['Title', 'Authors'], keep='first')
print(f"Shape of the dataframe obtained is : {df.shape} and after cleaning is : {df_cleaned.shape}")

load_dotenv()
uri = os.environ['URI_KEY']

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Specify the database and collection
db = client['my_database']  # Create/use 'my_database'
collection = db['arxiv_collection']  # Create/use 'my_collection'

# Convert DataFrame to dictionary (list of dictionaries)
data = df_cleaned.to_dict(orient='records')

# Insert the data into the MongoDB collection
result = collection.insert_many(data)

# Print the inserted IDs
print("Inserted document IDs:", result.inserted_ids)

# Step 1: Identify duplicates
pipeline = [
    {
        "$group": {
            "_id": "$Link",  # Field to check for duplicates
            "uniqueIds": { "$addToSet": "$_id" },  # Store all unique _ids
            "count": { "$sum": 1 }  # Count duplicates
        }
    },
    {
        "$match": {
            "count": { "$gt": 1 }  # Only keep duplicates
        }
    }
]

duplicates = collection.aggregate(pipeline)

# Step 2: Remove duplicates
for doc in duplicates:
    unique_ids = doc['uniqueIds']
    unique_ids.pop(0)  # Keep the first id
    # Delete the duplicates
    collection.delete_many({"_id": {"$in": unique_ids}})

print("Duplicates removed.")

# Fetch data from MongoDB
data_from_db = collection.find()
data_list = list(data_from_db)
df_retrieved = pd.DataFrame(data_list)


# print(df_retrieved.columns)
# print(df_retrieved.head(10))
# print(df_retrieved['Link'])
# print(df_retrieved.count)