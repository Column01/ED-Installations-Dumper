import datetime
import json

from tqdm import tqdm
import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Get a handle to the database and collection
db = client["FSSSignalDiscovered"]
collection = db["eddn"]

# Define the query and projection to find the signals we care about
query = {"message.signals.SignalType": "Installation"}
projection = {
    'message.StarSystem': 1,
    'message.SystemAddress': 1,
    'message.StarPos': 1,
    'message.signals': {
        '$filter': {
            'input': '$message.signals',
            'as': 'signal',
            'cond': {
                '$eq': [ '$$signal.SignalType', 'Installation']
            }
        }
    }
}
print("Collecting entries that have installations and filtering out duplicate results...")
# Find all signals that match the query
signals = collection.find(query, projection=projection)

# Initialize a dictionary to store unique systems and their most recent signal
unique_systems = {}
num_signals = 0
# Iterate through the signals
for signal in tqdm(signals):
    num_signals += 1
    # Get the system name
    system_name = signal["message"]["StarSystem"]
    # If the system is not in the dictionary, add it with the current signal as the most recent
    if system_name not in unique_systems:
        unique_systems[system_name] = signal
    # Otherwise, compare the current signal's timestamp with the one already stored
    else:
        # Assume the current signal is more recent
        most_recent_signal = signal
        # If the current signal's timestamp is older than the one already stored, keep the existing one
        if datetime.datetime.fromisoformat(signal["message"]["signals"][0]["timestamp"]) < datetime.datetime.fromisoformat(unique_systems[system_name]["message"]["signals"][0]["timestamp"]):
            most_recent_signal = unique_systems[system_name]
        # Update the dictionary with the most recent signal
        unique_systems[system_name] = most_recent_signal

# Convert the dictionary to a list of unique signals
unique_signals = list(unique_systems.values())

unique_systems_copy = unique_systems.copy()

for system_name, signal in unique_systems.items():
    unique_systems[system_name].pop("_id")

print("Dumping installations to file...")
with open("installations.json", "w+") as fp:
    json.dump(dict(sorted(unique_systems.items())), fp, indent=2)

print(f"Filtered {num_signals} down to {len(unique_signals)} signals and dumped to file!")
