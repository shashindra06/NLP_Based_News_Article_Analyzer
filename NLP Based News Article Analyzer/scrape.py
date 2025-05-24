import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
# import time # Optional: if you want to add delays between requests

def scrape_article(url, url_id):
    # Ensure the 'articles' directory exists
    articles_dir = 'articles'
    if not os.path.exists(articles_dir):
        os.makedirs(articles_dir)

    # Convert URL_ID to string in case it's a number (e.g., from Excel)
    url_id_str = str(url_id)
    
    status_message = "Success" # Default status

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title (adjust tag if needed)
        title = soup.find('h1')
        title_text = title.text.strip() if title else "Title Not Found"

        # --- EXTRACT BODY - REFINEMENT STARTS HERE ---
        body_text = ""

        # Attempt 1: Look for a specific main content div
        # REPLACE 'td-post-content' with the actual class/ID you found during debugging!
        main_content_container = soup.find('div', class_='td-post-content') # <--- Confirm this class!

        if main_content_container:
            paragraphs = main_content_container.find_all('p')
            body_text = ' '.join([p.text.strip() for p in paragraphs if p.text.strip()])

        # Attempt 2: If no specific container, try to get all paragraphs
        if not body_text: # If the first attempt didn't yield results
            paragraphs = soup.find_all('p')
            body_text = ' '.join([p.text.strip() for p in paragraphs if p.text.strip()])

        # Attempt 3: Sometimes the content is in an <article> tag
        if not body_text or len(body_text) < 100: # If still too short or empty, try <article>
            article_tag = soup.find('article')
            if article_tag:
                paragraphs = article_tag.find_all('p')
                body_text = ' '.join([p.text.strip() for p in paragraphs if p.text.strip()])

        # --- EXTRACT BODY - REFINEMENT ENDS HERE ---

        # If title or body is still empty, mark as failed
        if not title_text or not body_text:
            status_message = "Failed: Content Missing"
        
        # Save to articles/URL_ID.txt
        file_path = os.path.join(articles_dir, f'{url_id_str}.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(title_text + '\n\n' + body_text)

        print(f"Successfully scraped {url_id_str}.txt")
        return title_text, body_text, status_message

    except requests.exceptions.RequestException as req_err:
        status_message = f"Failed: Network/HTTP Error - {req_err}"
        print(f"Network or HTTP error scraping {url_id_str} ({url}): {req_err}")
        title_text = f"ERROR: Network/HTTP Issue - {req_err}"
        body_text = ""
    except Exception as e:
        status_message = f"Failed: General Error - {e}"
        print(f"General error scraping {url_id_str} ({url}): {e}")
        title_text = f"ERROR: General Issue - {e}"
        body_text = ""
    finally:
        # Ensure an empty file is created even on failure
        file_path = os.path.join(articles_dir, f'{url_id_str}.txt')
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(title_text + '\n\n' + body_text)
        return title_text, body_text, status_message


# --- Scrape ALL URLs from Input.xlsx and log results ---
if __name__ == "__main__":
    print("\n--- Starting full scraping from Input.xlsx with logging ---")

    log_data = [] # List to store dictionaries for the DataFrame

    try:
        df = pd.read_excel('Input.xlsx')
        if 'URL_ID' not in df.columns or 'URL' not in df.columns:
            raise ValueError("Input.xlsx must contain 'URL_ID' and 'URL' columns.")

        for index, row in df.iterrows():
            url_id = row['URL_ID']
            url = row['URL']
            print(f"\nScraping {url_id}: {url}")

            # Call scrape_article and get the status message back
            title, body, status = scrape_article(url, url_id)
            
            # Add entry to log_data
            log_data.append({
                'URL_ID': url_id,
                'URL': url,
                'Title': title, # Optional: log the title too for quick checks
                'Status': status
            })
            
            # Optional: Add a small delay between requests to be polite to the server
            # time.sleep(1) # Un-comment and adjust if you face issues with too many requests

    except FileNotFoundError:
        print("Error: Input.xlsx not found in the project directory.")
        print("Please ensure 'Input.xlsx' is in 'C:\\Users\\Shashendra\\Desktop\\NLP Based News Article Analyzer\\'.")
    except Exception as e:
        print(f"An error occurred during full scraping: {e}")
    finally:
        # Always attempt to save the log file, even if errors occurred during scraping
        if log_data: # Only save if there's data to log
            log_df = pd.DataFrame(log_data)
            log_df.to_csv('scrape_log.csv', index=False, encoding='utf-8')
            print("\nScraping log saved to scrape_log.csv")
        else:
            print("\nNo scraping data to log.")

    print("\n--- Full Scraping Complete ---")