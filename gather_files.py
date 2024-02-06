import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from helpers import bytes_to_size_string, size_string_to_bytes

# Datetime object for the date before update 17 to ensure we only download important files
UPDATE_17_DATETIME = datetime.strptime('2023-Oct-15 12:00:00', '%Y-%b-%d %H:%M:%S')


def find_files(url):
    global total_size
    # Send a GET request to the URL
    response = requests.get(url)
    # Parse the HTML content of the response
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all table rows
    table_rows = soup.find_all('tr')

    # Initialize empty lists to store the data
    files = []
    directories = []

    # Loop through each table row
    for row in table_rows:
        # Gather info about the file
        entry_name = row.find('td', {'class': 'n'})
        entry_type = row.find('td', {'class': 't'})
        entry_modified = row.find('td', {'class': 'm'})
        entry_size = row.find('td', {'class': 's'})

        # Skip entries that are not relevant
        if entry_name is None or entry_type is None or entry_modified is None or entry_modified.text is None:
            continue
        
        # Try to generate a datetime object from the file modified attribute, skip files that do not have this info
        try:
            file_modified_date = datetime.strptime(entry_modified.text, '%Y-%b-%d %H:%M:%S')
        except ValueError:
            continue

        # Only index files after update 17 (when SignalType was added)
        if file_modified_date >= UPDATE_17_DATETIME:
            entry_url = entry_name.find('a')

            # Check if the entry type is a directory
            if entry_type.text == 'Directory':
                if entry_url:
                    # Get the text of the "a" tag
                    directory_name = entry_url.text
                    # Skip dev and beta directory
                    if directory_name in ["dev", "beta"]:
                        continue
                    # Get the "href" attribute of the "a" tag
                    href = entry_url['href']
                    # Add the directory to the directories list
                    directories.append({
                        "name": directory_name,
                        "url": url + href
                    })
            else:
                # Get the text of the "a" tag
                file_name = entry_name.text
                # Skip test files
                if "Test" in file_name:
                    continue
                # Get the "href" attribute of the "a" tag
                href = entry_url['href']
                
                # Convert the file size string to bytes and add it to the total file size variable
                file_size = size_string_to_bytes(entry_size.text)
                total_size += file_size

                # Add the file to the files list
                files.append({
                    "file_name": file_name,
                    "file_size": file_size,
                    "file_type": entry_type.text,
                    "url": url + href
                })

    # Return both lists
    return files, directories

def crawl_directory(url):
    global total_files, directories_scanned
    print(f"Crawling url: {url}")
    # Crawl the directory
    files, directories = find_files(url)
    num_files = len(files)
    total_files += num_files
    print(f"Indexed {num_files} files. Total files indexed: {total_files}")
    # For each directory, call the crawl_directory function recursively
    for directory in directories:
        if directory["name"] == "..":
            continue
        files.extend(crawl_directory(directory["url"]))
    
    directories_scanned.extend(directories)

    return files

def crawl_all(total_files):
    global directories_scanned
    files = crawl_directory('https://edgalaxydata.space/EDDN/')

    # Create a json file with the collected files
    with open('files.json', 'w') as f:
        json.dump({"files": files, "directories_scanned": directories_scanned}, f, indent=4)

total_files = 0
directories_scanned = []
total_size = 0

crawl_all(total_files)

print(f"Directories scanned: {directories_scanned}")

print(f"Total file size: {bytes_to_size_string(total_size)}")
