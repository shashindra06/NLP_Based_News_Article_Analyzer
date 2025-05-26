import os

# Check articles/
articles_dir = 'articles'
if os.path.exists(articles_dir) and os.path.isdir(articles_dir):
    articles = [f for f in os.listdir(articles_dir) if f.endswith('.txt')]
    print(f"Found {len(articles)} article files in {articles_dir}: {articles[:5]}")
else:
    print(f"Error: {articles_dir} directory not found or is not a directory.")

# Check stopword files
stopword_files = [
    'StopWords_Names.txt', 'StopWords_Geographic.txt', 'StopWords_Generic.txt',
    'StopWords_GenericLong.txt', 'StopWords_Currencies.txt',
    'StopWords_DatesandNumbers.txt', 'StopWords_Auditor.txt'
]

all_stopwords_found = True
for file in stopword_files:
    if os.path.exists(file):
        print(f"{file} found")
    else:
        print(f"Error: {file} missing")
        all_stopwords_found = False

if all_stopwords_found:
    print("All stopword files found.")