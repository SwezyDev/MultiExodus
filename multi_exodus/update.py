from .constants import GITHUB_REPO
import requests
import hashlib
import ctypes
import sys
import os

sha256_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/main/MultiExodus.sha256" # url to the sha256 hash file
api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest" # github api url for latest release
installer_name = "Multi.Exodus.Installer.exe" # name of the installer file

def check_updates(msg_box): # function to check for updates
    current_hash = sha256_get(sys.executable) # get the sha256 hash of the current executable
    latest_hash = get_latest_hash() # get the latest sha256 hash from github

    if current_hash is None or latest_hash is None:
        ctypes.windll.user32.MessageBoxW(0, f"SHA256 calculation failed for MultiExodus. Auto-Update wont work.\n\nCheck if you're on the latest version.\nhttps://github.com/SwezyDev/MultiExodus", "MultiExodus", 0x10) # show error message box
    elif current_hash.lower() != latest_hash.lower():
        user_response = ctypes.windll.user32.MessageBoxW(0, f"A new version of MultiExodus is available!\n\nDo you want to download it now?", "MultiExodus", 0x04 | 0x40) # show info message box
        if user_response == 6: # if user clicked "Yes"
            r = download_latest() # download the latest version
            if not r: # if download failed
                if not ctypes.windll.shell32.IsUserAnAdmin():
                    user_response2 = ctypes.windll.user32.MessageBoxW(0, f"Failed to download the latest version of MultiExodus.\n\nWant to retry as administrator?", "MultiExodus", 0x04 | 0x10) # show error message box
                    if user_response2 == 6: # if user clicked "Yes"
                        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, None, None, 1) # restart the application as admin
                        os._exit(0) # exit the current instance
                ctypes.windll.user32.MessageBoxW(0, f"Failed to download the latest version of MultiExodus.\n\nPlease visit the GitHub page to download it manually.\nhttps://github.com/SwezyDev/MultiExodus", "MultiExodus", 0x10) # show error message box
                os.system("start https://github.com/SwezyDev/MultiExodus") # open GitHub page
            os._exit(0) # exit the application to allow user to run the new version
    
    if msg_box:
        ctypes.windll.user32.MessageBoxW(0, f"You are running the latest version of MultiExodus.", "MultiExodus", 0x40) # show info message box

def get_latest_hash(): # function to get the sha256 hash of the latest release executable
    try:
        response = requests.get(sha256_url) # make a get request to the sha256 url
        response.raise_for_status() # raise an error for bad responses
        hash_text = response.text.strip() # get the hash text from the response
        return hash_text # return the hash text
    except Exception:
        return None # return None if there was an error

def sha256_get(path): # function to get the sha256 hash of a file
    if not os.path.isfile(path): # check if the file exists
        return None # return None if the file does not exist
    sha256_hash = hashlib.sha256() # create a sha256 hash object
    try: # read the file in chunks to avoid memory issues
        with open(path, "rb") as f: # open the file in binary mode
            for byte_block in iter(lambda: f.read(4096), b""): # read the file in 4096 byte chunks
                sha256_hash.update(byte_block) # update the hash object with the chunk
        return sha256_hash.hexdigest() # return the hex digest of the hash
    except Exception as e: # catch any exceptions
        return None # return None if there was an error

def download_latest(): # function to download the latest release executable
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
