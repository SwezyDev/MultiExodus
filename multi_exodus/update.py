from .constants import GITHUB_REPO
import subprocess
import requests
import os

api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest" # github api url for latest release
installer_name = "Multi.Exodus.Installer.exe" # name of the installer file

def get_latest_hash(): # function to get the sha256 hash of the latest release executable
    try:
        response = requests.get(api_url) # make a get request to the api
        response.raise_for_status() # raise an error for bad responses
        release_data = response.json() # parse the json response

        assets = release_data.get("assets", []) # get the assets from the release data
        for a in assets: # iterate through the assets
            if a["name"].lower().endswith(".exe"): # look for the executable asset
                digest = a.get("digest", "") # get the digest field
                if digest.startswith("sha256:"): # check if the digest is a sha256 hash
                    return digest.split("sha256:")[1].strip() # return the sha256 hash
        return None # return None if no executable asset found
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

        subprocess.run([installer_name], check=True) # run the installer
        return True # return True on success
    except Exception as e:
        return False # return False on failure
