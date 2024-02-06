# Elite Dangerous Installation Dumper

This code was written to index, download, process and dump the FSSSignalDiscovered logs from [edgalaxydata](https://edgalaxydata.space/)'s EDDN dumps. When you follow the process below and run the scripts, it should generate a file called `installations.json` which will contain all installations sorted alphabetically by their system location. An example dump (Using a *small* amount of the total data) can be found [here](https://gist.github.com/Column01/8d45fc73117def63b30f12466d7324ac).

**Thank you to [edgalaxydata](https://edgalaxydata.space/) for providing this data!**

## Setup

1. Download and install [Python 3.12+](https://www.python.org/downloads/) (developed and tested on this version, could work on older or newer idk)
2. Install requirements from requirements file: `pip install -r requirements.txt`
3. Download and install [MongoDB's Community Server](https://www.mongodb.com/try/download/community), this is what stores the data for processing

## Running the program

The workflow for generating a dump is somewhat manual at this time. This could be automated using a batch/shell script to run the scripts or programmatically using python if you'd like

**NOTE:** This process will use a reasonable amount of disk space (at the time of writing, approximately ~40-50GB of free space is required)

### Index edgalaxydata

To do this, you need to run the `gather_files.py` script. You can do so like so:

To run the script, use the following command: `python gather_files.py`

This will print in the terminal some output about which url its working on and how many files it finds. This should take a few minutes to complete as it is quite a few files.

### Download the log files we care about

Once the files have been indexed, we need to use the `download_by_type.py` script to download the `FSSSignalDiscovered` files that we care about. When the script is run it will calculate the storage space required to house the files and ask for confirmation from the user before proceeding.

To run the script, use the following command: `python download_by_type.py`

### Insert the data into the database

Now that we have downloaded all the files we care about, we need to process them and insert them all into the MongoDB. This process will take a **LONG** time to complete, for me the import took ~3h on my computer using a 5600x with 32GB of RAM with both the dump files and database being on an NVME drive. As of writing is not designed to be done more than once (**I will touch more on that later though**). This process can be initiated by running the `insert_into_db.py` script.

To run the script, use the following command: `python insert_into_db.py`

### Process the data to generate an installations dump file

Finally, to generate a dump we need to run the `generate_installations_dump.py` file. This file makes a connection to the MongoDB, and executes a query to pull all entries that have installations in them. It then filters the results to remove any duplicates (discarding older results) to ensure there is as little data stored in the dump as possible. This should also mean that any old data of installations that may no longer be present will not show up in the dump so no historic data will be available (this could be changed if required).

When the script is run, it will generate a file called `installations.json` containing every known installations from the EDDN dumps we downloaded

To run the script, use the following command: `python generate_installations_dump.py`

## Additional Notes

### Repeat runs

As new data is added to the EDDN dumps provided graciously by [edgalaxydata](https://edgalaxydata.space/), the installations dump will become outdated. In order to update the dump at this time it would require manual deletion of the MongoDB collection storing the data followed by a reimport of it all.

This *could* be alleviated by moving all processed files out of the downloads folder (done after the new files are downloaded) or by adding a cache of processed files to the `insert_into_db.py` script, but at this time I do not plan to do so as I'm burnt out staring at the database insertion taking 3 hours LOL

### Optimizations

The data downloaded doesn't all contain the info we need, this code relies on the `SignalType` attribute being set in the files which was not present up until Update 17 (October 2023). I plan to optimize the code and alter it to only download and process files that contain this `SignalType` attribute by ignoring files created before this date, but as of writing it doesn't care when the files were created.

## Legal

I am not affiliated with Frontier Developments or Elite Dangerous in any way. All data is graciously provided by [edgalaxydata](https://edgalaxydata.space/). All copyrights are held by their original owners.
