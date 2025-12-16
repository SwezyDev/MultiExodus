from . import wallet_manager, ui, info, settings, update, motd, tray, constants, rpc # import necessary modules
from collections import defaultdict # for defaultdict
from .toast import show_toast # for showing toast notifications
from datetime import datetime # for date and time handling
import customtkinter # for custom tkinter widgets
import threading # for threading
import ctypes # for windows api calls
import psutil # for process management
import time # for time operations
import sys # for system operations
import os # for operating system interactions
import re # for regular expressions

title_stop_event = threading.Event() # event to signal title updater thread to stop
title_thread = None # global variable to hold the title updater thread
title_lock = threading.Lock() # make thread start thread-safe

def restart_title(): # function to restart the title updater thread
    global title_thread, title_stop_event # use global variables

    with title_lock: # ensure thread-safe operation
        if title_thread and title_thread.is_alive(): # if title thread is running, stop it
            title_stop_event.set() # signal the thread to stop
            title_thread.join() # wait for the thread to finish

        title_stop_event.clear() # clear the stop event for the new thread
        title_thread = threading.Thread(target=title_updater, args=(root,), daemon=True) # create a new title updater thread
        title_thread.start() # start the new title updater thread

def title_updater(root): # function to update the window title with wallet count and current time
    last_slow_update = 0 # timestamp of last slow update
    slow_update = 3600  # update slow fields every hour
    cached_values = {} # cache for slow updating fields

    def eepy_cat(sec): # helper function to sleep with stop event checking
        for i in range(sec): # loop for the number of seconds
            if title_stop_event.is_set(): # check if stop event is set
                return True # exit if stop event is set
            time.sleep(1) # sleep for 1 second
        return False # return False if completed without stop event

    while not title_stop_event.is_set(): # loop until stop event is set
        config = settings.read_config() # read settings from settings.json
        title_template = config.get("title", "MultiExodus - {count} Loaded {s} | {time}") # get title template from settings
        needed_fields = set(re.findall(r"{(.*?)}", title_template)) # find all fields in the title template

        now_ts = time.time() # current timestamp
        slow_update_needed = (now_ts - last_slow_update) >= slow_update # check if slow update is needed

        cached_values = {k: v for k, v in cached_values.items() if k in needed_fields} # remove cached values that are no longer needed

        if slow_update_needed: # if slow update is needed
            if "count" in needed_fields: # if count field is needed
                names, count = wallet_manager.detect_wallets() # detect existing wallets
                cached_values["count"] = count # set count value

            if "s" in needed_fields: # if s field is needed
                if "count" not in cached_values: # if count is not already cached
                    names, count = wallet_manager.detect_wallets() # detect existing wallets
                cached_values["s"] = "Wallets" if count != 1 else "Wallet" # set plural s value

            if "date" in needed_fields: # if date field is needed
                cached_values["date"] = datetime.now().strftime("%Y-%m-%d") # set current date value

            if "username" in needed_fields: # if username field is needed
                cached_values["username"] = os.getlogin() # set system username value

            if "computername" in needed_fields: # if computername field is needed
                cached_values["computername"] = os.environ.get("COMPUTERNAME", "Unknown") # set computer name value

            if "exodus_version" in needed_fields: # if exodus_version field is needed
                cached_values["exodus_version"] = wallet_manager.get_exodus_version() # set exodus version value

            if "motd" in needed_fields: # if motd field is needed
                cached_values["motd"] = motd.get_motd().strip().replace("\n", " ")[:50]  # set motd value (first 50 chars, single line)

            last_slow_update = now_ts # update last slow update timestamp

        if "time" in needed_fields: # if time field is needed
            cached_values["time"] = datetime.now().strftime("%H:%M:%S") # set current time value

        safe_values = defaultdict(str, cached_values) # create a defaultdict to avoid KeyErrors
        formatted_title = title_template.format_map(safe_values) # format the title with the collected values

        root.title(formatted_title) # update title with formatted title

        if "time" in needed_fields: # if time field is needed, update every second
            if eepy_cat(1): # wait 1 second before updating again
                break # exit if stop event is set
            
        elif "date" in needed_fields: # otherwise, update on new day
            now = datetime.now() # get current time
            sec_midnight = ((24 - now.hour - 1) * 3600) + ((60 - now.minute - 1) * 60) + (60 - now.second) + 1 # calculate seconds until midnight
            if eepy_cat(sec_midnight + 1): # wait until just after midnight to update
                break # exit if stop event is set

        else: # otherwise, update every 6 hours
            if eepy_cat(21600): # wait 6 hours before updating again
                break # exit if stop event is set

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


def check_proc(config): # function to check if another instance of the app is running
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
                if config.get("show_toasts", True): # check if show_toasts is enabled in settings
                    show_toast("MultiExodus", "Another instance of MultiExodus is already running.") # show toast notification
                os._exit(0) # exit the current instance

    return # no other instance found

def pre_check(): # function to perform pre-checks before starting the app
    config = settings.read_config() # read settings from settings.json
    check_proc(config) # check if another instance is running

    if config.get("show_toasts", True): # check if show_toasts is enabled in settings
        show_toast("MultiExodus", f"Welcome back, {os.getlogin()}") # show startup toast notification

    if not config.get("bypass_updates", False): # check if bypass updates is not enabled in settings
        update.check_updates(msg_box=False, config=config) # check for updates unless bypassed in settings
    
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
        info_text = f.read() # read the entire content of the file

    config = settings.read_config() # read settings from settings.json

    root.bind("<Escape>", lambda e: root.quit()) # bind escape key to quit the app
    root.bind("<F1>", lambda e: info.InfoPopup(root, title="Multi Exodus Information", text=info_text, text_color="#FFFFFF", fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141")) # bind F1 key to show info popup
    root.bind("<F2>", lambda e: settings.SettingsPopup(root, title="Multi Exodus Settings", text_color="#FFFFFF", fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141")) # bind F2 key to open settings popup (not implemented yet)
    root.bind("<F3>", lambda e: wallet_manager.open_data_location()) # bind F3 key to open data location in file explorer
    root.bind("<F4>", lambda e: update.check_updates(msg_box=True, config=config)) # bind F4 to check for updates
    root.bind("<F5>", lambda e: ui.rebuild(root, extra=False)) # bind F5 key to refresh the wallets ui
    root.bind("m", lambda e: motd.MotdPopup(root, title="Message of the Day", text_color="#FFFFFF", fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141")) # bind m key to show message of the day popup
    root.bind("+", lambda e: wallet_manager.add_wallet(root, lambda r=root: ui.build_wallets_ui(root, *wallet_manager.detect_wallets()), config.get("show_toasts", True))) # bind + key to add a new wallet
    root.bind("-", lambda e: wallet_manager.delete_wallet(first_wallet, ui.rebuild(root), config.get("show_toasts", True))) # bind - key to delete a wallet
    root.bind("*", lambda e: wallet_manager.load_wallet(first_wallet, config.get("show_toasts", True))) # bind * key to load a wallet
    root.bind("<Delete>", lambda e: wallet_manager.delete_all_wallets(lambda: ui.rebuild(root), config.get("show_toasts", True))) # bind delete key to delete all saved wallets
    root.bind("<Alt_L>", lambda e: ui.toggle_layout()) # bind left alt key to toggle wallet layout

def main(): # main function to start the application
    global root # use the global root variable
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