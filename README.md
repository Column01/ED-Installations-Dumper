# Elite Dangerous Installation Dumper

This code was written to index, download, process and dump the FSSSignalDiscovered logs from [edgalaxydata](https://edgalaxydata.space/)'s EDDN dumps. When you follow the process below and run the scripts, it should generate a file called `installations.json` which will contain all installations sorted alphabetically by their system location. An example dump (Using a *small* amount of the total data) can be found [here](https://gist.github.com/Column01/8d45fc73117def63b30f12466d7324ac).

**Thank you to [edgalaxydata](https://edgalaxydata.space/) for providing this data!**

## Setup

1. Download and install [Python 3.12+](https://www.python.org/downloads/) (developed and tested on this version, could work on older or newer idk)
2. Install requirements from requirements file: `pip install -r requirements.txt`
3. Download and install [MongoDB's Community Server](https://www.mongodb.com/try/download/community), this is what stores the data for processing

## Running the program

The workflow for generating a dump is somewhat manual at this time. This could be automated using a batch/shell script to run the scripts or programmatically using python if you'd like

**NOTE:** This process will use a reasonable amount of disk space, as of writing its between 5-10GB of disk space needed

### Index edgalaxydata

To do this, you need to run the `gather_files.py` script. You can do so like so:

To run the script, use the following command: `python gather_files.py`

This will print in the terminal some output about which url its working on and how many files it finds. This should take about a minute to complete as it is quite a few files. This will also only index files created after Update 17 as thats when the `SignalType` attribute was added.

### Download the log files we care about

Once the files have been indexed, we need to use the `download_by_type.py` script to download the `FSSSignalDiscovered` files that we care about. When the script is run it will calculate the storage space required to house the files and ask for confirmation from the user before proceeding. If run multiple times, it will skip files that are already downloaded so no need to worry about that.

To run the script, use the following command: `python download_by_type.py`

### Insert the data into the database

Now that we have downloaded all the files we care about, we need to process them and insert them all into the MongoDB. This process will take a long time to complete. This process can be initiated by running the `insert_into_db.py` script. The script should ignore files already processed so duplicate data should not be inserted.

To run the script, use the following command: `python insert_into_db.py`

### Process the data to generate an installations dump file

Finally, to generate a dump we need to run the `generate_installations_dump.py` file. This file makes a connection to the MongoDB, and executes a query to pull all entries that have installations in them. It then filters the results to remove any duplicates (discarding older results) to ensure there is as little data stored in the dump as possible. This should also mean that any old data of installations that may no longer be present will not show up in the dump so no historic data will be available (this could be changed if required).

When the script is run, it will generate a file called `installations.json` containing every known installations from the EDDN dumps we downloaded

To run the script, use the following command: `python generate_installations_dump.py`

## Legal

I am not affiliated with Frontier Developments or Elite Dangerous in any way. All data is graciously provided by [edgalaxydata](https://edgalaxydata.space/). All copyrights are held by their original owners.
