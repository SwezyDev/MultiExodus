from . import wallet_manager, ui, info, settings, update, motd, tray, constants
from datetime import datetime
import customtkinter
import threading
import ctypes
import psutil
import time
import sys
import os

def title_updater(root): # function to update the window title with wallet count and current time
    while True: # loop for ever lol
        names, count = wallet_manager.detect_wallets() # update wallet count
        root.title(f"MultiExodus - {count} Loaded Wallet{'s' if count != 1 else ''} | {datetime.now().strftime('%H:%M:%S')}") # update title with wallet count and current time
        time.sleep(1) # Update every second

def center_me(root, width, height): # function to center the window on the screen
    screen_width = root.winfo_screenwidth() # get screen width
    screen_height = root.winfo_screenheight() # get screen height

    x = int((screen_width / 2) - (width / 2)) # calculate x position
    y = int((screen_height / 2) - (height / 2)) # calculate y position

    root.geometry(f"{width}x{height}+{x}+{y}") # set window geometry

def focus_window(hwnd): # function to focus an existing window
    user32 = ctypes.windll.user32 # get user32 dll
    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    user32.SetForegroundWindow(hwnd) # bring window to foreground

def search_win(): # function to find a window by its title prefix
    user32 = ctypes.windll.user32 # get user32 dll
    handles = [] # list to hold matching window handles

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int) # define callback function type
    def enum_proc(hwnd, lParam): # callback function for EnumWindows
        length = user32.GetWindowTextLengthW(hwnd) # get window title length
        if length > 0: # if window has a title
            buf = ctypes.create_unicode_buffer(length + 1) # create buffer for title
            user32.GetWindowTextW(hwnd, buf, length + 1) # get window title
            title = buf.value # convert buffer to string
            if title.startswith(constants.WINDOW_TITLE): # check if title matches
                handles.append(hwnd) # add handle to list
        return True # continue enumeration

    user32.EnumWindows(enum_proc, 0) # enumerate all windows
    return handles[0] if handles else None # return first matching handle or None

def check_proc(): # function to check if another instance is running
    pid = os.getpid() # get current process id
    name = os.path.basename(sys.argv[0]) # get current executable name
    
    running = any(proc.info['pid'] != pid and proc.info['name'] == name.startswith(constants.WINDOW_TITLE) for proc in psutil.process_iter(['pid', 'name']))  # check for other processes with same name

    if running: # if another instance is running
        hwnd = search_win(constants.WINDOW_TITLE) # find the window handle
        if hwnd: # if window handle found
            focus_window(hwnd) # focus the existing window
        sys.exit(0) # exit the current instance

def bind_keybinds(root, first_wallet, info_text): # function to bind keybinds to the root window
    root.bind("<Escape>", lambda e: root.quit()) # bind escape key to quit the app
    root.bind("<F1>", lambda e: info.InfoPopup(root, title="Multi Exodus Information", text=info_text, text_color="#FFFFFF", fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141")) # bind F1 key to show info popup
    root.bind("<F2>", lambda e: settings.SettingsPopup(root, title="Multi Exodus Settings", text_color="#FFFFFF", fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141")) # bind F2 key to open settings popup (not implemented yet)
    root.bind("<F3>", lambda e: wallet_manager.open_data_location()) # bind F3 key to open data location in file explorer
    root.bind("<F4>", lambda e: update.check_updates(msg_box=True)) # bind F4 to check for updates
    root.bind("<F5>", lambda e: ui.rebuild(root)) # bind F5 key to refresh the wallets ui
    root.bind("m", lambda e: motd.MotdPopup(root, title="Message of the Day", text_color="#FFFFFF", fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141")) # bind m key to show message of the day popup
    root.bind("+", lambda e: wallet_manager.add_wallet(root, lambda r=root: ui.build_wallets_ui(root, *wallet_manager.detect_wallets()))) # bind + key to add a new wallet
    root.bind("-", lambda e: wallet_manager.delete_wallet(first_wallet, ui.rebuild(root))) # bind - key to delete a wallet
    root.bind("*", lambda e: wallet_manager.load_wallet(first_wallet)) # bind * key to load a wallet
    root.bind("<Delete>", lambda e: wallet_manager.delete_all_wallets(lambda: ui.rebuild(root))) # bind delete key to delete all saved wallets

def main(): # main function to start the application
    root = customtkinter.CTk(fg_color="#202020") # create the main window
    center_me(root, 1375, 700) # center the window
    root.resizable(False, False) # disable resizing
    root.iconbitmap(constants.APP_ICON) # set window icon


    names, count = wallet_manager.detect_wallets() # detect existing wallets

    first_wallet = names[0] if names else "" # get the first wallet name for delete binding

    tray.create(root, first_wallet)

    threading.Thread(target=title_updater, args=(root,), daemon=True).start() # start title updater thread

    ui.build_wallets_ui(root, names, count) # build the wallets ui

    with open(constants.INFO_PATH, "r", encoding="utf-8") as f: # load info text from file
        info_text = f.read()

    bind_keybinds(root, first_wallet, info_text) # bind keybinds

    root.protocol("WM_DELETE_WINDOW", lambda: root.withdraw()) # minimize to tray on close

    root.mainloop() # start the main event loop

