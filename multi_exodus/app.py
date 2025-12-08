from . import wallet_manager, ui, info, settings, update, motd, tray, constants, rpc
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
    ctypes.windll.user32.SwitchToThisWindow(hwnd, True) # switch to the window

def search_win(): # function to search for existing window by title
    user32 = ctypes.windll.user32 # get user32 dll
    handles = [] # list to hold window handles

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int) # callback function for EnumWindows
    def enum_proc(hwnd, lParam): # function to enumerate windows
        length = user32.GetWindowTextLengthW(hwnd) # get window title length
        if length > 0: # if window has a title 
            buf = ctypes.create_unicode_buffer(length + 1) # create buffer for title
            user32.GetWindowTextW(hwnd, buf, length + 1) # get window title
            title = buf.value # store title in variable
            if title.startswith(constants.WINDOW_TITLE): # check if title matches our app
                handles.append(hwnd) # add handle to list
        return True # continue enumeration

    user32.EnumWindows(enum_proc, 0) # enumerate all windows
    return handles if handles else None # return the matching handle or None


def check_proc(): # function to check if another instance of the app is running
    curr_pid = os.getpid() # get current process id
    exe_name = os.path.basename(sys.argv[0]).lower() # get current executable name

    matching = [] # list to hold matching processes
    for proc in psutil.process_iter(['pid', 'name']): # iterate through all running processes
        try: # iterate through all running processes
            name = proc.info['name'] # get process name
            pid = proc.info['pid'] # get process id
            if not name: # skip processes with no name
                continue # skip processes with no name
            if name.lower() == exe_name: # check if process name matches the current executable name
                matching.append(pid) # add matching process id to list
        except (psutil.NoSuchProcess, psutil.AccessDenied): # ignore processes that no longer exist or are inaccessible
            pass # ignore processes that no longer exist or are inaccessible

    if len(matching) > 2: # if more than one instance is found
        for pid in matching: # iterate through matching processes
            if pid != curr_pid: # if the pid is not the current process
                hwnd = search_win() # search for existing window
                for h in hwnd: # focus all found windows
                    focus_window(h) # focus the existing window
                os._exit(0) # exit the current instance

    return # no other instance found

def pre_check(): # function to perform pre-checks before starting the app
    check_proc() # check if another instance is running

    config = settings.read_config() # read settings from settings.json

    if not config.get("bypass_updates", False): # check if bypass updates is not enabled in settings
        update.check_updates(msg_box=False) # check for updates unless bypassed in settings
    
    if not constants.MULTI_WALLET_DIR.exists(): # check if the MultiExodus directory exists
        constants.MULTI_WALLET_DIR.mkdir(parents=True, exist_ok=True) # create the directory if it doesnt exist

    if not constants.EXODUS_DIR.exists(): # check if the Exodus directory exists
        ctypes.windll.user32.MessageBoxW(0, f"Exodus directory not found! Please install Exodus wallet first.", "MultiExodus", 0x30) # show info message box
        os.system("start https://www.exodus.com/download/") # open Exodus download page
        os._exit(0) # exit the application if Exodus is not installed

def interpolate_color(start_color, end_color, factor): # function to interpolate between two hex colors
    start_rgb = [int(start_color[i:i+2], 16) for i in (1, 3, 5)] # convert start color to rgb
    end_rgb = [int(end_color[i:i+2], 16) for i in (1, 3, 5)] # convert end color to rgb
    result_rgb = [ # interpolate each color channel
        int(start_rgb[j] + (end_rgb[j] - start_rgb[j]) * factor) 
        for j in range(3) # for each color channel (r, g, b)
    ]
    return f"#{result_rgb[0]:02x}{result_rgb[1]:02x}{result_rgb[2]:02x}" # convert back to hex color

def animation(label, root, step=0, max_steps=100): # function for smooth color transition animation
    factor = abs((step % (2 * max_steps)) - max_steps) / max_steps # calculate interpolation factor
    smooth_color = interpolate_color("#1F1F1F", "#FFFFFF", factor) # interpolate between two colors
    if label.winfo_exists(): # check if label still exists
        label.configure(text_color=smooth_color) # update label color
    root.after(10, animation, label, root, step + 1, max_steps) # schedule next animation step

def load_app(root, pre_frame): # function to load the main application
    pre_check() # heavy work
    time.sleep(2) # simulate loading time
    root.after(0, create_app, root, pre_frame)  # switch back to UI thread

def bind_keybinds(root, first_wallet): # function to bind keybinds to the root window
    with open(constants.INFO_PATH, "r", encoding="utf-8") as f: # load info text from file
        info_text = f.read()

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
    root.title("MultiExodus Loading...") # set pre window title

    pre_frame = customtkinter.CTkFrame(root, width=1375, height=700, fg_color="#202020", corner_radius=0) # create pre frame
    pre_frame.pack(fill="both", expand=True) # pack pre frame

    loading = customtkinter.CTkLabel(pre_frame, text="Loading MultiExodus...", fg_color="#202020", text_color="#FFFFFF", font=("Segoe UI", 32), bg_color="#202020") # create loading label
    loading.place(relx=0.5, rely=0.5, anchor="center") # place loading label in center

    animation(loading, root) # start loading animation

    threading.Thread(target=lambda: load_app(root, pre_frame), daemon=True).start() # start loading the app in a separate thread

    root.protocol("WM_DELETE_WINDOW", lambda: root.withdraw()) # minimize to tray on close

    root.mainloop() # start the main event loop


def create_app(root, pre_frame): # function to create and run the MultiExodus application
    pre_frame.destroy() # destroy pre frame
    names, count = wallet_manager.detect_wallets() # detect existing wallets

    first_wallet = names[0] if names else "" # get the first wallet name for delete binding

    config = settings.read_config() # read settings from settings.json

    tray.create(root, first_wallet) # create the system tray icon and menu

    threading.Thread(target=title_updater, args=(root,), daemon=True).start() # start title updater thread

    if config.get("enable_rpc", False): # check if rpc is enabled in settings
        threading.Thread(target=lambda: rpc.start_rpc(count), daemon=True).start() # start discord rich presence

    ui.build_wallets_ui(root, names, count) # build the wallets ui

    bind_keybinds(root, first_wallet) # bind keybinds