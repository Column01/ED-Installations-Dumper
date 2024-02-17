import json
import os
import time
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

import requests

from helpers import bytes_to_size_string, size_string_to_bytes

FILE_TYPE = "FSSSignalDiscovered"

def download_file(file_blob):
    t0 = time.time()
    url = file_blob["url"]
    file_name = os.path.join("downloads", file_blob["file_name"])
    file_name_processed = os.path.join("downloads/processed", file_blob["file_name"])
    # Download the file if we don't already have it
    if not os.path.exists(file_name) and not os.path.exists(file_name_processed):
        try:
            r = requests.get(url)
            with open(file_name, 'wb') as f:
                f.write(r.content)
            return (url, time.time() - t0)
        except Exception as e:
            print("Exception in download_file():", e)
            print(f"File name: {file_name}, URL: {url}")
            return (f"ERROR DOWNLOADING {file_name}", time.time() - t0)
    else:
        # Skip existing files that have been downloaded already
        return (url, 0)


def download_files_parallel(files):
    # Spawns a threadpool of (CPU count - 1) threads to use to download the files
    cpus = cpu_count() - 1
    print(f"Starting file downloads with {cpus} threads")
    results = ThreadPool(cpus).imap_unordered(download_file, files)
    for result in results:
        if result[1] == 0:
            print(f'Skipped existing file at url: {result[0]}')
        print('url:', result[0], 'time (s):', result[1])


# Make the downloads directory if it doesn't exist
if not os.path.exists("downloads"): 
    os.makedirs("downloads") 

if not os.path.exists("downloads/processed"): 
    os.makedirs("downloads/processed") 


with open("files.json", "r") as fp:
    files = json.load(fp)

    # Filter function to filter for the file type we care about
    is_type = lambda file_blob: FILE_TYPE in file_blob["file_name"]

    not_exist = lambda file_blob: not os.path.exists(os.path.join("downloads", file_blob["file_name"])) and not os.path.exists(os.path.join("downloads/processed", file_blob["file_name"]))

    # Apply the filter to the list of files to return files we care about
    filtered_files = list(filter(not_exist, filter(is_type, files["files"])))

    # Initialize some metrics
    num_files = len(filtered_files)

    if num_files == 0:
        quit("There are no new files to download! Please check again later.")
    total_size = sum([file_blob["file_size"] for file_blob in filtered_files])
    
    # Ask for confirmation and finally download the files
    print("="*20, "\n")
    print(f"You are about to download {num_files} files totalling {bytes_to_size_string(total_size)} of data!")
    choice = input("Would you like to proceed? (Y/N): ")
    print("="*20, "\n")
    if choice.lower() == "y":
        print("Download files... this will take a while!")
        t0 = time.time()
        download_files_parallel(filtered_files)
        print('Total time:', time.time() - t0)

    else:
        quit("Exiting program as user denied the download...")
