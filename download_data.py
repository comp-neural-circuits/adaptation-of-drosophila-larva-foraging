#%%%
import os
import wget
import zipfile

URL = "https://zenodo.org/record/7438188/files/data_wosniack2022.zip?download=1"
print("Downloading data from: " + URL)

temp_name = "temp_data_wosniack2022.zip"
wget.download(URL, temp_name)
print("data downloaded to: " + temp_name)

print("unzipping data to folder Data")
with zipfile.ZipFile(temp_name, 'r') as zip_ref:
    zip_ref.extractall("Data")

print("data unzipped, now deleting zip file")
os.remove(temp_name)


# %%
