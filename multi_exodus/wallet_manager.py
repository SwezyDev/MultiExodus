from .constants import MULTI_WALLET_DIR, EXODUS_WALLET, EXODUS_DIR, DEFAULT_PNG # for directory and file paths
from customtkinter import filedialog # for file dialogs
from .dialogs import MyInputDialog # for custom input dialogs
from PIL import Image, ImageDraw # for image processing
from pathlib import Path # for path manipulations
from . import settings # for reading settings
import ctypes # for Windows message boxes
import shutil # for file operations
import time # for time.time() and time.ctime()
import os # for os.startfile and os.system

def change_standard_picture(popup): # function to change the standard wallet picture
    file_path = filedialog.askopenfilename(title="Select new standard wallet picture", filetypes=[("PNG Images", "*.png")]) # open file dialog to select new image
    if file_path: # if a file was selected
        asset_src = Path(file_path) # path to the selected image
        asset_dst = Path(DEFAULT_PNG) # path to the default wallet image
        shutil.copy(asset_src, asset_dst) # copy the selected image to the assets folder
        ctypes.windll.user32.MessageBoxW(0, f"Standard wallet picture changed successfully!\n\nNew wallets will use this picture by default.", "MultiExodus", 0x40) # show success message
        popup.destroy() # close the settings popup

def open_data_location(): # function to open the MultiExodus data location in file explorer
    if MULTI_WALLET_DIR.exists() and MULTI_WALLET_DIR.is_dir(): # if the multi-wallet directory exists
        os.startfile(MULTI_WALLET_DIR) # open the multi-wallet directory in file explorer
    else:
        ctypes.windll.user32.MessageBoxW(0, f"MultiExodus data directory does not exist.", "MultiExodus", 0x10) # show error message

def detect_wallets(): # function to detect existing wallets
    if not MULTI_WALLET_DIR.exists(): # if the multi-wallet directory does not exist
        return [], 0 # return 0 and an empty list, because there are no wallets saved

    config = settings.read_config() # read settings to determine sorting method
    sort_value = config.get("sort_wallets_by", "Oldest First") # default to "Oldest First" if not set

    if sort_value in ("A-Z Alphabetical", "Z-A Alphabetical"): # if sorting alphabetically
        names = sorted([d.name for d in MULTI_WALLET_DIR.iterdir() if d.is_dir()]) # get sorted list of wallet folder names
        if sort_value == "Z-A Alphabetical": # if sorting Z-A
            names.reverse() # reverse the list for Z-A order
        return names, len(names) # return the list of names and the count of wallets

    folders = [] # list to hold wallet folder names and their creation times
    for d in MULTI_WALLET_DIR.iterdir(): # iterate through items in the multi-wallet directory
        if d.is_dir(): # if the item is a directory
            folders.append((d.name, d.stat().st_ctime)) # add the folder name and creation time to the list

    reverse_maybe = True if sort_value == "Newest First" else False # determine if sorting should be reversed
    folders.sort(key=lambda x: x[1], reverse=reverse_maybe) # sort folders by creation time

    names = [name for name, _ in folders] # extract just the folder names
    return names, len(names) # return the list of names and the count of wallets


def round_corners(image, radius): # function to round the corners of an image
    mask = Image.new("L", image.size, 0) # create a mask for rounding
    draw = ImageDraw.Draw(mask) # create a drawing context
    draw.rounded_rectangle((0, 0, image.size[0], image.size[1]), radius=radius, fill=255) # draw a rounded rectangle on the mask

    rounded = Image.new("RGBA", image.size) # create a new image for the rounded result
    rounded.paste(image, (0, 0), mask) # paste the original image onto the rounded image using the mask
    return rounded # return the rounded image


def add_wallet(root, callback): # function to add a new wallet
    backup_wallet = EXODUS_WALLET / f"exodus.wallet_{int(time.time())}_backup" # path for backing up current wallet

    msg_box = ctypes.windll.user32.MessageBoxW(0, f"We will now Trigger the Exodus Recovery Mode.\nYou will be asked to input your Seed Phrase, please follow the instructions from Exodus.\n\nDo you want to continue?", "MultiExodus", 0x04 | 0x40) # show confirmation dialog

    if msg_box == 6: # if user clicked "Yes"
        if (EXODUS_WALLET / "exodus.wallet").exists(): # if there is an existing wallet
            msg_box2 = ctypes.windll.user32.MessageBoxW(0, f"Do you want to backup your current wallet before proceeding?\n\nThe backup will be stored at:\n{backup_wallet}\n\nProceed with backup?\n\nYes = Create a Backup\nNo = Skip Backup\nCancel = Import this Wallet", "MultiExodus", 0x03 | 0x30) # show backup confirmation dialog
            if msg_box2 == 6: # if user clicked "Yes" to backup
                shutil.copytree(EXODUS_WALLET / "exodus.wallet", backup_wallet, dirs_exist_ok=True) # backup the current wallet
            elif msg_box2 == 2: # if user clicked "Cancel" to import wallet
                import_wallet(root, callback) # call the import wallet function
                return # exit the add_wallet function

        restore_file = EXODUS_WALLET / "restore-mnemonic" # path to the restore mnemonic file
        restore_file.write_text("") # create an empty restore mnemonic file to trigger recovery mode | i found this trigger with ProcMon (https://learn.microsoft.com/de-de/sysinternals/downloads/procmon)

        os.startfile(EXODUS_DIR / "Exodus.exe") # start exodus right after creating the restore mnemonic file to trigger recovery mode
        ctypes.windll.user32.MessageBoxW(0, "Press OK after your Wallet was successfully restored by Exodus.\n\n(If you want you can also set a Password for Exodus before pressing OK)\n\nDO NOT PRESS OK BEFORE", "MultiExodus", 0x40) # prompt user to restore wallet
        ctypes.windll.user32.MessageBoxW(0, "Are you sure it got restored successfully? Press OK if so.\n\nLAST CHANCE", "MultiExodus", 0x40) # final confirmation prompt

        os.system("taskkill /f /im Exodus.exe >nul 2>&1") # kill exodus after restoration

        import_wallet(root, callback) # call the import wallet function

    else:
        return # user cancelled the operation


def import_wallet(root, callback): # function to import an existing wallet folder
    dialog = MyInputDialog(master=root, title="Edit Wallet Name", text="Enter new name:") # prompt for new wallet name

    new_name = dialog.get_input() # get the inputted wallet name
    if new_name and new_name.strip() != "": # if a valid name was provided
        target_folder = MULTI_WALLET_DIR / new_name # path for the new wallet folder

        if target_folder.exists(): # if a wallet with this name already exists
            ctypes.windll.user32.MessageBoxW(0, "A wallet with this name already exists.", "MultiExodus", 0x10) # show error message
            return # exit the function

        if not (EXODUS_WALLET / "exodus.wallet").exists(): # if no wallet was restored
            ctypes.windll.user32.MessageBoxW(0, "No current Exodus wallet found.", "MultiExodus", 0x10) # show error message
            return # exit the function

        shutil.copytree(EXODUS_WALLET / "exodus.wallet", target_folder) # copy the restored wallet to the new multi-wallet folder
        asset_src = Path(DEFAULT_PNG) # path to default wallet image 
        if asset_src.exists(): # if the default image exists
            shutil.copy(asset_src, target_folder / "title.png") # copy the default image to the new wallet folder

        ctypes.windll.user32.MessageBoxW(0, f"Exodus wallet successfully imported as '{new_name}'", "MultiExodus", 0x40) # show success message

        callback(root) # rebuild the UI with the new wallet

def show_wallet_info(wallet_name): # function to show wallet information
    target_folder = MULTI_WALLET_DIR / wallet_name # path to the wallet folder
    if target_folder.exists() and target_folder.is_dir(): # if the wallet folder exists
        creation_time = time.ctime(target_folder.stat().st_ctime) # get the creation time of the wallet folder
        ago_time = settings.time_ago(target_folder.stat().st_ctime) # get how long ago the wallet was created
        wallet_note_path = target_folder / "note.txt" # path to the wallet note file
        wallet_pic_path = target_folder / "title.png" # path to the wallet picture file
        wallet_note = "None" # default note text
        if wallet_note_path.exists(): # if the wallet note file exists
            with open(wallet_note_path, "r", encoding="utf-8") as f: # open the note file
                wallet_note = f.read() # read the note text
        
        return f"Wallet Name: {wallet_name}\nCreated On: {creation_time} ({ago_time} ago)\n\nNote: {wallet_note}\n\nImage: {wallet_pic_path}" # return the wallet information string
    else:
        return f"Wallet '{wallet_name}' does not exist." # return error message if wallet does not exist
    
def edit_wallet_name(label, folder): # function to edit wallet name
    old_name = label.current_name # get the current wallet name
    dialog = MyInputDialog(title="Edit Wallet Name", text="Enter new name:") # prompt for new wallet name
    new_name = dialog.get_input() # get the inputted wallet name
    if new_name and new_name.strip() != "": # if a valid name was provided
        (folder / old_name).rename(folder / new_name) # rename the wallet folder
        label.configure(text=new_name) # update the label text
        label.current_name = new_name # update the current_name attribute


def edit_wallet_note(note_label, note_p): # function to edit wallet note
    dialog = MyInputDialog(title="Edit Wallet Note", text="Enter new note:") # prompt for new wallet note
    new_note = dialog.get_input() # get the inputted wallet note
    if new_note is not None and new_note.strip() != "": # if a valid note was provided
        note_label.configure(text=new_note) # update the note label text 
        with open(note_p, "w", encoding="utf-8") as f: # open the note file for writing
            f.write(new_note) # write the new note to the file


def edit_wallet_image(image_label, picture_p): # function to edit wallet image
    file_path = filedialog.askopenfilename(title="Select new wallet image", filetypes=[("PNG Images", "*.png")]) # open file dialog to select new image
    if file_path: # if a file was selected
        pil_image = Image.open(file_path).resize((200, 130)) # open and resize the selected image
        wallet_image = pil_image # use the selected image as the wallet image
        image_label.configure(image=wallet_image) # update the image label
        pil_image.save(picture_p) # save the new image to the specified path

def open_wallet(wallet_name): # function to open the wallet folder in file explorer
    target_folder = MULTI_WALLET_DIR / wallet_name # path to the wallet folder
    if target_folder.exists() and target_folder.is_dir(): # if the wallet folder exists
        os.startfile(target_folder) # open the wallet folder in file explorer
    else: # if the wallet folder does not exist
        ctypes.windll.user32.MessageBoxW(0, f"Wallet '{wallet_name}' does not exist.", "MultiExodus", 0x10) # show error message


def delete_all_wallets(callback): # function to delete all saved wallets
    os.system("taskkill /f /im Exodus.exe >nul 2>&1") # kill exodus to avoid file access issues

    if MULTI_WALLET_DIR.exists(): # if the multi-wallet directory exists
        all_wallets = sorted(
            (f.name for f in MULTI_WALLET_DIR.iterdir() if f.is_dir()),# list of all wallet folder names
            key=lambda name: (MULTI_WALLET_DIR / name).stat().st_ctime # sort by creation time
        )
    else: # if the multi-wallet directory does not exist
        ctypes.windll.user32.MessageBoxW(0, f"No saved wallets found.", "MultiExodus", 0x10) # show error message
        return # exit the function

    msg_box = ctypes.windll.user32.MessageBoxW(0, f"Are you sure you want to delete ALL saved wallets?\nThis action cannot be undone.\n\n- " + '\n- '.join(all_wallets), "MultiExodus", 0x04 | 0x10) # show confirmation dialog

    if msg_box == 6: # if user confirmed deletion
        if MULTI_WALLET_DIR.exists() and MULTI_WALLET_DIR.is_dir(): # if the multi-wallet directory exists
            shutil.rmtree(MULTI_WALLET_DIR) # delete the multi-wallet directory
            ctypes.windll.user32.MessageBoxW(0, f"All saved wallets have been deleted.", "MultiExodus", 0x40) # show success message
            callback() # rebuild the ui with the updated wallet list
        else: # if the multi-wallet directory does not exist
            ctypes.windll.user32.MessageBoxW(0, f"No saved wallets found.", "MultiExodus", 0x10) # show error message

def delete_wallet(wallet_name, callback): # function to delete a wallet
    os.system("taskkill /f /im Exodus.exe >nul 2>&1") # kill exodus to avoid file access issues
    msg_box = ctypes.windll.user32.MessageBoxW(0, f"Are you sure you want to delete the wallet '{wallet_name}'?\nThis action cannot be undone.", "MultiExodus", 0x04 | 0x10) # show confirmation dialog

    if msg_box == 6: # if user confirmed deletion
        target_folder = MULTI_WALLET_DIR / wallet_name # path to the wallet folder
        if target_folder.exists() and target_folder.is_dir(): # if the wallet folder exists
            shutil.rmtree(target_folder) # delete the wallet folder
            ctypes.windll.user32.MessageBoxW(0, f"Wallet '{wallet_name}' has been deleted.", "MultiExodus", 0x40) # show success message
            callback() # rebuild the ui with the updated wallet list
        else: # if the wallet folder does not exist
            ctypes.windll.user32.MessageBoxW(0, f"Wallet '{wallet_name}' does not exist.", "MultiExodus", 0x10) # show error message


def load_wallet(wallet_name): # function to load a wallet into Exodus
    os.system("taskkill /f /im Exodus.exe >nul 2>&1") # kill exodus to avoid file access issues
    target_folder = MULTI_WALLET_DIR / wallet_name # path to the wallet folder
    if not target_folder.exists(): # if the wallet folder does not exist
        ctypes.windll.user32.MessageBoxW(0, f"Wallet '{wallet_name}' does not exist.", "MultiExodus", 0x10) # show error message
        return # exit the function

    if (EXODUS_WALLET / "exodus.wallet").exists(): # if there is an existing exodus wallet
        shutil.rmtree(EXODUS_WALLET / "exodus.wallet") # remove existing exodus wallet folder

    def ignore_files(dir, files): # function to ignore certain files when copying
        return [f for f in files if f in ("note.txt", "title.png")] # ignore note and title image files when copying

    shutil.copytree(target_folder, EXODUS_WALLET / "exodus.wallet", ignore=ignore_files) # copy the selected wallet to the exodus wallet folder
    msg_b = ctypes.windll.user32.MessageBoxW(0, f"Wallet '{wallet_name}' has been loaded into Exodus.\n\nDo you want to launch Exodus now?", "MultiExodus", 0x04 | 0x40) # show success message
    if msg_b == 6: # if user clicked "Yes"
        os.startfile(EXODUS_DIR / "Exodus.exe") # launch exodus

def get_exodus_version(): # function to get the installed exodus version
    app_folders = [f for f in EXODUS_DIR.iterdir() if f.is_dir() and f.name.startswith("app-")] # list of app folders
    if not app_folders: # if no app folders found
        return "Unknown" # return unknown version

    latest_folder = max(app_folders, key=lambda f: list(map(int, f.name.replace("app-", "").split(".")))) # find the folder with the highest version number
    return latest_folder.name.replace("app-", "") # return the version number