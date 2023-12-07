import tkinter as tk
from tkinter import scrolledtext
from threading import Thread, Lock
import requests
import re
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Constants
REQUEST_DELAY = 0.1
NUM_THREADS = 4
EXCLUDE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg')  # Add more extensions if needed

# Shared resources with locks for thread-safe operations
visited_urls = set()
email_set = set()
url_lock = Lock()
email_lock = Lock()

def extract_emails_from_text(text):
    email_regex = re.compile(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)')
    return set(email_regex.findall(text))

def fetch_links_from_text(text, base_url):
    soup = BeautifulSoup(text, 'html.parser')
    return {urljoin(base_url, link.get('href')) for link in soup.find_all('a', href=True)}

def is_valid_email(email):
    if any(email.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
        return False
    domain = email.split('@')[-1]
    if re.match(r'^[0-9.]+$', domain):  # Check if domain consists of only numbers and dots
        return False
    return True

def is_valid_tld(url, desired_tld):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    if netloc.endswith(desired_tld):
        return True
    return False

def fetch_webpage_content(thread_num, url, keywords, output_text, sub_websites, tld, max_depth, depth=0):
    global visited_urls, email_set

    with url_lock:
        if depth > max_depth or url in visited_urls:
            return
        visited_urls.add(url)

    if not url.startswith(("http://", "https://")):
        return

    if not is_valid_tld(url, tld):
        return

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            text = response.text
            emails = extract_emails_from_text(text)

            for email in emails:
                with email_lock:
                    if email not in email_set and (not keywords or any(keyword.lower() in email.lower() for keyword in keywords)) and is_valid_email(email):
                        output_text.insert(tk.END, f"Thread {thread_num}: Found email: {email}\n")
                        with open('result.csv', 'a') as f:
                            f.write(email + '\n')
                        email_set.add(email)

            if depth < max_depth:
                links = fetch_links_from_text(text, url)
                for link in links:
                    fetch_webpage_content(thread_num, link, keywords, output_text, sub_websites, tld, max_depth, depth=depth + 1)
        else:
            output_text.insert(tk.END, f"Thread {thread_num}: Failed to fetch {url}: Status code {response.status_code}\n")
    except requests.RequestException as e:
        output_text.insert(tk.END, f"Thread {thread_num}: Error fetching {url}: {e}\n")

    sub_websites.append(url)


def search_google(thread_num, query, api_key, cse_id, start_page):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': api_key,
        'cx': cse_id,
        'start': start_page
    }
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None

def run(thread_num, start_page, total_pages, query, api_key, cse_id, keywords, output_text, tld):
    global visited_urls, email_set
    keywords_list = [keyword.strip() for keyword in keywords.split(',')] if keywords else []
    sub_websites = []

    for page in range(start_page, total_pages + 1, NUM_THREADS):
        output_text.insert(tk.END, f"Thread {thread_num}: Searching page {page}...\n")
        result = search_google(thread_num, query, api_key, cse_id, start_page=page)

        if result and 'items' in result:
            for item in result['items']:
                url = item.get('link')
                output_text.insert(tk.END, f"Thread {thread_num}: Fetching URL: {url}\n")
                fetch_webpage_content(thread_num, url, keywords_list, output_text, sub_websites, tld, 2)
                time.sleep(REQUEST_DELAY)
        else:
            output_text.insert(tk.END, f"Thread {thread_num}: No more results found.\n")
            break

    output_text.insert(tk.END, f"Thread {thread_num}: Email scraping completed.\n")
    for sub_website in sub_websites:
        output_text.insert(tk.END, sub_website + '\n')

def start_scraping(window, api_key, cse_id, query, keywords, output_text, total_pages, tld):
    threads = []
    for i in range(NUM_THREADS):
        start_page = i + 1
        thread = Thread(target=run, args=(i+1, start_page, total_pages, query, api_key, cse_id, keywords, output_text, tld))
        threads.append(thread)
        thread.start()

    def update_gui():
        if any(thread.is_alive() for thread in threads):
            window.after(1000, update_gui)
        else:
            output_text.insert(tk.END, "All threads have completed.\n")

    update_gui()

def create_gui():
    window = tk.Tk()
    window.title("Web Scraper")

    tk.Label(window, text="API Key:").pack()
    api_key_entry = tk.Entry(window, width=50)
    api_key_entry.pack()

    tk.Label(window, text="CSE ID:").pack()
    cse_id_entry = tk.Entry(window, width=50)
    cse_id_entry.pack()

    tk.Label(window, text="Query:").pack()
    query_entry = tk.Entry(window, width=50)
    query_entry.pack()

    tk.Label(window, text="Keywords (comma-separated, leave empty to fetch all emails):").pack()
    keywords_entry = tk.Entry(window, width=50)
    keywords_entry.pack()

    tk.Label(window, text="Total Pages to Visit:").pack()
    total_pages_var = tk.IntVar(value=10)
    total_pages_entry = tk.Entry(window, textvariable=total_pages_var, width=10)
    total_pages_entry.pack()

    tk.Label(window, text="Desired TLD (e.g., .com, .org):").pack()
    tld_entry = tk.Entry(window, width=50)
    tld_entry.pack()

    output_text = scrolledtext.ScrolledText(window, width=70, height=20)
    output_text.pack()

    scrape_button = tk.Button(window, text="Start Scraping", command=lambda: start_scraping(window, api_key_entry.get(), cse_id_entry.get(), query_entry.get(), keywords_entry.get(), output_text, total_pages_var.get(), tld_entry.get()))
    scrape_button.pack()

    window.mainloop()

if __name__ == '__main__':
    create_gui()
