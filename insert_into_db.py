import bz2
import json
import os
import time
import shutil
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

from pymongo import MongoClient
from tqdm import tqdm

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['FSSSignalDiscovered']
collection = db['eddn']

def process_file(file):
    start_time = time.time()
    if file.endswith('.bz2'):
        # If the file is a bz2 file, open it using bz2
        with bz2.open('downloads/' + file, 'rt') as f:
            for line in f:
                # Treat each line as JSON and insert it into the database
                doc = json.loads(line)
                collection.insert_one(doc)
    elif file.endswith('.jsonl'):
        # If the file is a jsonl file, open it normally
        with open('downloads/' + file, 'r') as f:
            for line in f:
                # Treat each file as JSON and insert it into the database
                doc = json.loads(line)
                collection.insert_one(doc)
    duration = time.time() - start_time
    shutil.move(file, os.path.join("downloads/processed", file))
    return (file, duration)

def process_files_parallel(files):
    cpus = 4
    print(f"Starting file import with {cpus} threads")
    results = ThreadPool(cpus).imap_unordered(process_file, files)

    for result in results:
        print(f'File: {result[0]} processed in {result[1]:.2f}s')

def process_files(files):
    results = [process_file(file) for file in tqdm(files)]


# Iterate over the files in the downloads folder
files = os.listdir('downloads')
print(f"Processing {len(files)} files")
t0 = time.time()
process_files(files)
print(f"Processed files in {time.time() - t0}s")
