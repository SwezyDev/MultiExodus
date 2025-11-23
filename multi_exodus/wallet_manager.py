from .constants import MULTI_WALLET_DIR, EXODUS_WALLET, EXODUS_DIR
from customtkinter import filedialog
from .dialogs import MyInputDialog
from PIL import Image, ImageDraw
from pathlib import Path
import ctypes
import shutil
import time
import os

def detect_wallets(): # function to detect existing wallets
    if not MULTI_WALLET_DIR.exists(): # if the multi-wallet directory does not exist
        return [], 0 # return 0 and an empty list, because there are no wallets saved

    folders = [] # list to hold wallet folder names and their creation times
    for d in MULTI_WALLET_DIR.iterdir(): # iterate through items in the multi-wallet directory
        if d.is_dir(): # if the item is a directory
            folders.append((d.name, d.stat().st_ctime)) # add the folder name and creation time to the list

    folders.sort(key=lambda x: x[1]) # sort folders by creation time

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
            msg_box2 = ctypes.windll.user32.MessageBoxW(0, f"Do you want to backup your current wallet before proceeding?\n\nThe backup will be stored at:\n{backup_wallet}\n\nProceed with backup?", "MultiExodus", 0x04 | 0x40) # show backup confirmation dialog
            if msg_box2 == 6: # if user clicked "Yes" to backup
                shutil.copytree(EXODUS_WALLET / "exodus.wallet", backup_wallet, dirs_exist_ok=True) # backup the current wallet

        restore_file = EXODUS_WALLET / "restore-mnemonic" # path to the restore mnemonic file
        restore_file.write_text("") # create an empty restore mnemonic file to trigger recovery mode | i found this trigger with ProcMon (https://learn.microsoft.com/de-de/sysinternals/downloads/procmon)

        os.startfile(EXODUS_DIR / "Exodus.exe") # start exodus right after creating the restore mnemonic file to trigger recovery mode
        ctypes.windll.user32.MessageBoxW(0, "Press OK after your Wallet was successfully restored by Exodus.\n\nDO NOT PRESS OK BEFORE", "MultiExodus", 0x40) # prompt user to restore wallet
        ctypes.windll.user32.MessageBoxW(0, "Are you sure it got restored successfully? Press OK if so.\n\nLAST CHANCE", "MultiExodus", 0x40) # final confirmation prompt

        os.system("taskkill /f /im Exodus.exe >nul 2>&1") # kill exodus after restoration

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
            asset_src = Path("./assets/title.png") # path to default wallet image 
            if asset_src.exists(): # if the default image exists
                shutil.copy(asset_src, target_folder / "title.png") # copy the default image to the new wallet folder

            ctypes.windll.user32.MessageBoxW(0, f"Exodus wallet successfully imported as '{new_name}'", "MultiExodus", 0x40) # show success message

            callback(root) # rebuild the UI with the new wallet

    else:
        return # user cancelled the operation


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


def delete_wallet(wallet_name, callback): # function to delete a wallet
    os.system("taskkill /f /im Exodus.exe >nul 2>&1") # kill exodus to avoid file access issues
    msg_box = ctypes.windll.user32.MessageBoxW(0, f"Are you sure you want to delete the wallet '{wallet_name}'?\nThis action cannot be undone.", "MultiExodus", 0x04 | 0x10) # show confirmation dialog

    if msg_box == 6: # if user confirmed deletion
        target_folder = MULTI_WALLET_DIR / wallet_name # path to the wallet folder
        if target_folder.exists() and target_folder.is_dir(): # if the wallet folder exists
            shutil.rmtree(target_folder) # delete the wallet folder
            ctypes.windll.user32.MessageBoxW(0, f"Wallet '{wallet_name}' has been deleted.", "MultiExodus", 0x40) # show success message
            callback() # rebuild the ui with the updated wallet list
        else:
            ctypes.windll.user32.MessageBoxW(0, f"Wallet '{wallet_name}' does not exist.", "MultiExodus", 0x10) # show error message


def load_wallet(wallet_name): # function to load a wallet into Exodus
    os.system("taskkill /f /im Exodus.exe >nul 2>&1") # kill exodus to avoid file access issues
    target_folder = MULTI_WALLET_DIR / wallet_name # path to the wallet folder
    if not target_folder.exists(): # if the wallet folder does not exist
        ctypes.windll.user32.MessageBoxW(0, f"Wallet '{wallet_name}' does not exist.", "MultiExodus", 0x10) # show error message
        return # exit the function

    if (EXODUS_WALLET / "exodus.wallet").exists(): # if there is an existing exodus wallet
        shutil.rmtree(EXODUS_WALLET / "exodus.wallet") # remove existing exodus wallet folder

    shutil.copytree(target_folder, EXODUS_WALLET / "exodus.wallet") # copy the selected wallet to the exodus wallet folder
    ctypes.windll.user32.MessageBoxW(0, f"Wallet '{wallet_name}' has been loaded into Exodus.\nYou can now launch Exodus to access it.", "MultiExodus", 0x40) # show success message
    os.startfile(EXODUS_DIR / "Exodus.exe") # launch exodus