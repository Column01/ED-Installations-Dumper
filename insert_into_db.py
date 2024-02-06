import bz2
import json
import os
import shutil
import time
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
    shutil.move(os.path.join("downloads", file), os.path.join("downloads/processed", file))
    return (file, duration)

def process_files(files):
    results = [process_file(file) for file in tqdm(files) if not os.path.isdir(os.path.join("downloads", file))]


# Iterate over the files in the downloads folder
files = os.listdir('downloads')
print(f"Processing {len(files)} files")
t0 = time.time()
process_files(files)
print(f"Processed files in {time.time() - t0}s")
time.sleep(1)
