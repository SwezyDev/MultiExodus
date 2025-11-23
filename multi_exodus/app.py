from . import wallet_manager, ui
from datetime import datetime
import customtkinter
import threading
import time

def title_updater(root): # function to update the window title with wallet count and current time
    while True: # loop for ever lol
        names, count = wallet_manager.detect_wallets() # update wallet count
        root.title(f"MultiExodus - {count} Loaded Wallets | {datetime.now().strftime('%H:%M:%S')}") # update title with wallet count and current time
        time.sleep(1) # Update every second

def main(): # main function to start the application
    root = customtkinter.CTk(fg_color="#202020") # create the main window
    root.geometry("1375x700") # set window size
    root.resizable(False, False) # disable resizing

    names, count = wallet_manager.detect_wallets() # detect existing wallets

    threading.Thread(target=title_updater, args=(root,), daemon=True).start() # start title updater thread

    ui.build_wallets_ui(root, names, count) # build the wallets UI

    root.mainloop() # start the main event loop
