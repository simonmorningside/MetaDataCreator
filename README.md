# MetaDataCreator
Used to read through existing metadata and help organize files, by assigning unique identifiers and pointing out duplicates.

Make sure to make a python environtment. Then install all the dependancies from the requirements.txt

Create a data folder in your project root, this is where your csv's will go
If you are running test data, create a folder called test/ in data and create copies of your CSVs in there

when running tests use the --test flag ex. python3 metadata.py --test so that your original data is not touched until you are ready. 
This will not only create an ID test pool so that test runs dont get muddled with regular runs, but also allow you to test how the csv is edited.

Create a photos directory, in this directory create a folder for the original photos named original and a folder for them to be put in after being renamed called renamed
If running tests also create a test_original and a test_renamed folder in your photos directory

when you first run metadata.py you will be prompted to name your csv's variables. These will be mapped for use for the rest of the project.

If you change your CSVs or edit them and need to change the ID build pool, run metadata.py and you will be prompted with a (y/n) for rebuilding the ID pool
