from multi_exodus import main, constants, update
import hashlib
import ctypes
import sys
import os

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
    
if __name__ == '__main__': 
    print("Welcome to MultiExodus Wallet Manager!")
    print("-------------------------------------")
    print("Made with love by Swezy <3")
    print("https://github.com/SwezyDev")
    print("-------------------------------------")
    print("Contact: https://t.me/Swezy")
    # print some info to the console about the project :)

    current_hash = sha256_get(sys.executable) # get the sha256 hash of the current executable
    latest_hash = update.get_latest_hash() # get the latest sha256 hash from github

    if current_hash is None or latest_hash is None:
        ctypes.windll.user32.MessageBoxW(0, f"SHA256 calculation failed for MultiExodus. Auto-Update wont work.\n\nCheck if you're on the latest version.\nhttps://github.com/SwezyDev/MultiExodus", "MultiExodus", 0x10) # show error message box
    elif current_hash.lower() != latest_hash.lower():
        user_response = ctypes.windll.user32.MessageBoxW(0, f"A new version of MultiExodus is available!\n\nDo you want to download it now?", "MultiExodus", 0x04 | 0x40) # show info message box
        if user_response == 6: # if user clicked "Yes"
            r = update.download_latest() # download the latest version
            if not r: # if download failed
                if not ctypes.windll.shell32.IsUserAnAdmin():
                    user_response2 = ctypes.windll.user32.MessageBoxW(0, f"Failed to download the latest version of MultiExodus.\n\nWant to retry as administrator?", "MultiExodus", 0x04 | 0x10) # show error message box
                    if user_response2 == 6: # if user clicked "Yes"
                        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, None, None, 1) # restart the application as admin
                        os._exit(0) # exit the current instance
                ctypes.windll.user32.MessageBoxW(0, f"Failed to download the latest version of MultiExodus.\n\nPlease visit the GitHub page to download it manually.\nhttps://github.com/SwezyDev/MultiExodus", "MultiExodus", 0x10) # show error message box
                os.system("start https://github.com/SwezyDev/MultiExodus") # open GitHub page
            os._exit(0) # exit the application to allow user to run the new version

    if not constants.MULTI_WALLET_DIR.exists(): # check if the MultiExodus directory exists
        constants.MULTI_WALLET_DIR.mkdir(parents=True, exist_ok=True) # create the directory if it doesnt exist

    if not constants.EXODUS_DIR.exists(): # check if the Exodus directory exists
        ctypes.windll.user32.MessageBoxW(0, f"Exodus directory not found! Please install Exodus wallet first.", "MultiExodus", 0x30) # show info message box
        os.system("start https://www.exodus.com/download/") # open Exodus download page
        os._exit(0) # exit the application if Exodus is not installed

    main() # Start the MultiExodus application