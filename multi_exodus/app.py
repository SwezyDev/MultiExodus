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

def center_me(root, width, height): # function to center the window on the screen
    screen_width = root.winfo_screenwidth() # get screen width
    screen_height = root.winfo_screenheight() # get screen height

    x = int((screen_width / 2) - (width / 2)) # calculate x position
    y = int((screen_height / 2) - (height / 2)) # calculate y position

    root.geometry(f"{width}x{height}+{x}+{y}") # set window geometry

def main(): # main function to start the application
    root = customtkinter.CTk(fg_color="#202020") # create the main window
    center_me(root, 1375, 700) # center the window
    root.resizable(False, False) # disable resizing
    root.iconbitmap("./assets/app.ico") # set window icon

    names, count = wallet_manager.detect_wallets() # detect existing wallets

    threading.Thread(target=title_updater, args=(root,), daemon=True).start() # start title updater thread

    ui.build_wallets_ui(root, names, count) # build the wallets UI

    root.mainloop() # start the main event loop
