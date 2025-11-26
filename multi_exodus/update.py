from .constants import GITHUB_REPO
import subprocess
import requests
import os

sha256_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/main/MultiExodus.sha256" # url to the sha256 hash file
api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest" # github api url for latest release
installer_name = "Multi.Exodus.Installer.exe" # name of the installer file

def get_latest_hash(): # function to get the sha256 hash of the latest release executable
    try:
        response = requests.get(sha256_url) # make a get request to the sha256 url
        response.raise_for_status() # raise an error for bad responses
        hash_text = response.text.strip() # get the hash text from the response
        return hash_text # return the hash text
    except Exception:
        return None # return None if there was an error

def download_latest():
    try:
        response = requests.get(api_url) # make a get request to the api
        response.raise_for_status() # raise an error for bad responses
        release_data = response.json() # parse the json response

        assets = release_data.get("assets", []) # get the assets from the release data
        download_url = None # initialize download url
        for a in assets: # iterate through the assets
            if a["name"].lower().endswith(".exe"): # look for the executable asset
                download_url = a["browser_download_url"] # get the download url
                break # exit loop once found

        if not download_url: # if no download url found
            return False # return False

        if os.path.exists(installer_name): # remove existing installer if it exists
            os.remove(installer_name) # remove existing installer

        with requests.get(download_url, stream=True) as r: # download the installer
            r.raise_for_status() # raise an error for bad responses
            with open(installer_name, "wb") as f: # write the installer to a file
                for chunk in r.iter_content(chunk_size=8192): # write in chunks
                    f.write(chunk) # write chunk to file

        os.startfile(installer_name) # run the installer
        return True # return True on success
    except Exception as e:
        return False # return False on failure
