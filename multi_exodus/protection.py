from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC # PBKDF2HMAC key derivation function
from cryptography.hazmat.primitives import hashes # for hashing algorithms
from .constants import MULTI_WALLET_DIR # for wallet directory path
from cryptography.fernet import Fernet # for symmetric encryption
from pathlib import Path # for path manipulations
from PIL import Image # for image handling
from . import dialogs # for password dialog
import base64 # for base64 encoding/decoding
import ctypes # for windows message boxes
import io # for in-memory byte streams

_ENCRYPTION_SALT = b'MultiExodus-Swezy<3' # fixed salt for key derivation
_VERIFICATION_FILE = '.multieexodus_verify' # verification file to check if password is correct | used as backup if no pictures are found
_VERIFICATION_MARKER = b'MULTIEEXODUS_ENCRYPTED' # marker to verify correct decryption

def password_key(password: str) -> bytes: # derive a Fernet key from the given password
    kdf = PBKDF2HMAC( # using PBKDF2HMAC key derivation function
        algorithm=hashes.SHA256(), # hash algorithm
        length=32, # desired key length
        salt=_ENCRYPTION_SALT,# fixed salt
        iterations=100000, # number of iterations
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode())) # return base64 key

def encrypt(): # encrypt all wallet files using the given password
    warn = ctypes.windll.user32.MessageBoxW(0, "You are about to Encrypt your Wallet data, if you proceed, make sure you remember your password.\nIf you forget your password, you will lose access to your wallets on MultiExodus permanently.\n\nWe recommend to save your Password physically, not on a Device due to security risks.\n\nDo you want to proceed?", "MultiExodus", 0x04 | 0x30) # warning msg box
    if warn != 6: # if user did not click "Yes"
        return "cancel" # exit the function

    dialog = dialogs.MyInputDialog(title="Enter Password", text="Enter password to encrypt wallets:") # create password input dialog
    password = dialog.get_input() # get the password from the dialog

    if not password or password.strip() == "": # ensure password is not empty
        return False # return False if password is empty
    
    verify_dialog = dialogs.MyInputDialog(title="Verify Password", text="Re-enter password to verify:") # create password verification dialog
    verify_password = verify_dialog.get_input() # get the verification password from the dialog
    if password != verify_password: # check if passwords match
        ctypes.windll.user32.MessageBoxW(0, "Passwords do not match. Encryption aborted.", "MultiExodus", 0x30) # show warning with OK only
        return "doesnt match" # return doesnt match if passwords do not match
    
    if password and password.strip() != "": # ensure password is not empty
        wallet_dir = Path(MULTI_WALLET_DIR) # path to the multi wallet directory

        if not wallet_dir.exists(): # check if wallet directory exists
            return False # do not proceed if directory does not exist

        key = password_key(password) # derive encryption key from password
        cipher = Fernet(key) # create Fernet cipher with derived key


        verify_path = wallet_dir / _VERIFICATION_FILE # path to the verification file
        encrypted_marker = cipher.encrypt(_VERIFICATION_MARKER) # encrypt the verification marker
        with open(verify_path, 'wb') as f: # create the verification file
            f.write(encrypted_marker) # write encrypted marker to file

        for p in wallet_dir.rglob('*'): # iterate over all files in the wallet directory
            if p.is_file() and p.name != _VERIFICATION_FILE and p.parent != wallet_dir: # only encrypt files inside subfolders
                try: # attempt encryption
                    with open(p, 'rb') as f: # open file in binary read mode
                        txt = f.read() # read file content

                    encrypted = cipher.encrypt(txt) # encrypt the content

                    with open(p, 'wb') as f: # open file in binary write mode
                        f.write(encrypted) # write encrypted content back to file

                except Exception as e: # catch any exceptions
                    return False # return False on failure
        return True # return True on success

def decrypt(password): # decrypt all wallet files using the given password
    wallet_dir = Path(MULTI_WALLET_DIR) # path to the multi wallet directory

    if not wallet_dir.exists(): # check if wallet directory exists
        return False # do not proceed if directory does not exist

    key = password_key(password) # derive decryption key from password
    cipher = Fernet(key) # create Fernet cipher with derived key

    verify_path = wallet_dir / _VERIFICATION_FILE # path to the verification file
    if verify_path.exists(): # check if verification file exists
        try: # attempt to verify password
            with open(verify_path, 'rb') as f: # open verification file in binary read mode
                encrypted_marker = f.read() # read encrypted marker
            
            decrypted_marker = cipher.decrypt(encrypted_marker) # decrypt the marker
            if decrypted_marker != _VERIFICATION_MARKER: # check if decrypted marker matches expected value
                return False # return False if password is incorrect
        except Exception: # catch any exceptions
            return False # return False if password is incorrect
    else: # if verification file doesn't exist, try to verify using a picture file
        wallet_pictures = list(wallet_dir.rglob('*.png')) # get list of wallet picture files
        if wallet_pictures: # if there are wallet pictures
            try: # attempt to decrypt and verify a picture
                with open(wallet_pictures[0], 'rb') as f: # open first picture file
                    encrypted_pic = f.read() # read encrypted content
                
                decrypted_pic = cipher.decrypt(encrypted_pic) # decrypt the picture
                
                with Image.open(io.BytesIO(decrypted_pic)) as img: # try to open decrypted data as image
                    img.verify() # verify image integrity
            except Exception: # catch any exceptions (wrong password or invalid image)
                return False # return False if password is incorrect

    for p in wallet_dir.rglob('*'): # iterate over all files in the wallet directory
        if p.is_file() and p.name != _VERIFICATION_FILE and p.parent != wallet_dir: # only decrypt files inside subfolders
            try: # attempt decryption
                with open(p, 'rb') as f: # open file in binary read mode
                    encrypted_txt = f.read() # read encrypted content

                decrypted = cipher.decrypt(encrypted_txt) # decrypt the content

                with open(p, 'wb') as f: # open file in binary write mode
                    f.write(decrypted) # write decrypted content back to file
            except Exception as e: # catch any exceptions
                return False # return False on failure
            
    verify_path.unlink() # remove the verification file after successful decryption
    return True # return True on success

def is_encrypted() -> bool: # check if wallets are encrypted by looking for the verification file
    wallet_dir = Path(MULTI_WALLET_DIR) # path to the multi wallet directory
    verify_path = wallet_dir / _VERIFICATION_FILE # path to the verification file

    if not verify_path.exists(): # check if verification file exists
        wallet_pictures = list(wallet_dir.rglob('*.png')) # get list of wallet picture files
        if wallet_pictures: # if there are wallet pictures
            for pic in wallet_pictures: # iterate through wallet pictures
                try: # attempt to open the image
                    with Image.open(pic) as img: # open image file
                        img.verify() # verify image integrity
                except Exception: # catch any exceptions
                    return True # return True if image cannot be opened (likely encrypted)
    else:
        return True # return True if verification file exists

def lost_password(): # handle lost password scenario
    from .app import restart_app # for restarting the app
    warn = ctypes.windll.user32.MessageBoxW(0, "This will erase all your wallets and wallet settings. There is no way to recover your wallets if you proceed. Make sure you have backed up your recovery phrases before continuing.\n\nDo you want to continue?", "MultiExodus", 0x04 | 0x30) # show warning msg box
    if warn != 6: # if user did not click "Yes"
        return False # exit the function
    
    wallet_dir = Path(MULTI_WALLET_DIR) # path to the multi wallet directory
    if wallet_dir.exists(): # check if wallet directory exists
        for p in wallet_dir.rglob('*'): # iterate over all files and folders in the
            if p.is_dir() and p.parent == wallet_dir: # only delete subfolders
                try: # attempt to delete folder
                    for sub in p.rglob('*'): # iterate over all files in the subfolder
                        if sub.is_file(): # only delete files
                            sub.unlink() # delete file
                    p.rmdir() # remove the empty subfolder
                except Exception: # catch any exceptions
                    return False # return False on failure
        
        verify_path = wallet_dir / _VERIFICATION_FILE # path to the verification file
        if verify_path.exists(): # check if verification file exists
            try: # attempt to delete verification file
                verify_path.unlink() # delete the verification file
            except Exception: # catch any exceptions
                return False # return False on failure
    
    restart_app() # restart the application to reflect changes
    return True # return True on success