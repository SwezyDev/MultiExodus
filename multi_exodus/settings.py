from . import app, wallet_manager, constants, ui, rpc # import necessary modules
from CTkToolTip import CTkToolTip # for tooltips
import customtkinter # for custom tkinter widgets
import threading # for threading
import ctypes # for Windows message boxes
import time # for time calculations
import json # for json operations

def read_config(): # function to read settings from settings.json
    try: # try to read the settings file
        with open(f"{constants.MULTI_WALLET_DIR}/settings.json", "r", encoding="utf-8") as f: # open the settings file
            return json.load(f) # return the settings as a dictionary
    except Exception: # if there was an error, return an empty dictionary
        return {} # return an empty dictionary

def add_config(key, value): # function to add or update a setting in settings.json
    config = read_config() # read the current settings
    config[key] = value # add or update the setting
    try: # try to write the settings file
        with open(f"{constants.MULTI_WALLET_DIR}/settings.json", "w", encoding="utf-8") as f: # open the settings file for writing
            json.dump(config, f, indent=4) # write the settings to the file
    except Exception: # catch any exceptions
        ctypes.windll.user32.MessageBoxW(0, f"Failed to save settings to settings.json.\n\nPlease check file permissions.", "MultiExodus", 0x10) # show error message box

def title_change(value): # function to update the window title based on settings
    add_config("title", value) # update the setting in settings.json
    threading.Thread(target=app.restart_title, daemon=True).start() # start a new thread to update the title

def rpc_change(value): # function to handle rpc option change
    add_config("enable_rpc", value) # update the setting in settings.json
    if value: # if rpc is enabled
        names, count = wallet_manager.detect_wallets() # detect wallets to get current count
        rpc.restart_rpc(count) # restart the rpc server with current wallet count
    else: # if rpc is disabled
        rpc.stop_rpc() # stop the rpc server

def sort_change(value, root): # function to handle sort option change
    add_config("sort_wallets_by", value) # update the setting in settings.json
    ui.rebuild(root) # rebuild the UI to reflect the new sorting

def time_ago(timestamp): # function to convert timestamp to "time ago" format
    seconds_ago = time.time() - timestamp # calculate seconds ago
    minutes_ago = seconds_ago // 60 # calculate minutes ago
    hours_ago = minutes_ago // 60 # calculate hours ago
    days_ago = hours_ago // 24 # calculate days ago
    weeks_ago = days_ago // 7 # calculate weeks ago
    months_ago = days_ago // 30 # calculate months ago
    years_ago = days_ago // 365 # calculate years ago

    if years_ago >= 1: # if more than a year ago
        return f"{int(years_ago)} year{'s' if years_ago > 1 else ''} ago" # return years ago string
    elif months_ago >= 1: # if more than a month ago
        return f"{int(months_ago)} month{'s' if months_ago > 1 else ''} ago" # return months ago string
    elif weeks_ago >= 1: # if more than a week ago
        return f"{int(weeks_ago)} week{'s' if weeks_ago > 1 else ''} ago" # return weeks ago string
    elif days_ago >= 1: # if more than a day ago
        return f"{int(days_ago)} day{'s' if days_ago > 1 else ''} ago" # return days ago string
    elif hours_ago >= 1: # if more than an hour ago
        return f"{int(hours_ago)} hour{'s' if hours_ago > 1 else ''} ago" # return hours ago string
    elif minutes_ago >= 1: # if more than a minute ago
        return f"{int(minutes_ago)} minute{'s' if minutes_ago > 1 else ''} ago" # return minutes ago string
    else: # if less than a minute ago
        return f"{int(seconds_ago)} second{'s' if seconds_ago > 1 else ''} ago" # return seconds ago string

class SettingsPopup(customtkinter.CTkToplevel): # settings popup window class
    def __init__(self, master=None, title="Settings Popup", text_color="#FFFFFF",
                fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141"): # constructor with customizable colors
        super().__init__(master) # initialize the parent class
        self.title(title) # set the window title
        app.center_me(self, 400, 500) # center the window on the screen
        self.resizable(False, False) # make the window non-resizable
        self.grab_set() # make the popup modal
        self.configure(fg_color=fg_color) # set the background color

        settings = read_config() # read current settings

        if settings.get("bypass_updates", False): # get bypass_updates setting
            bypass_updates_value = True # if set, use True
        else: # if not set, default to False
            bypass_updates_value = False # default to False

        if settings.get("enable_rpc", False): # get enable_rpc setting
            rpc_value = True # if set, use True
        else: # if not set, default to False
            rpc_value = False # default to False

        scroll_frame = customtkinter.CTkScrollableFrame(master=self, width=360, height=460, fg_color=scroll_fg, border_color=scroll_bc, border_width=0.6) # create scrollable frame
        scroll_frame.grid(padx=10, pady=10) # place the scrollable frame in the window

        bypass_updates_label = customtkinter.CTkLabel(master=scroll_frame, text="Bypass Update Checks:", fg_color=fg_color, text_color=text_color, font=("Segoe UI", 14)) # label for bypass updates option
        bypass_updates_label.grid(padx=10, pady=10, sticky="w") # place the label in the grid

        bypass_updates_cb = customtkinter.CTkCheckBox(master=scroll_frame, text="", fg_color=scroll_bc, text_color=text_color, hover_color=scroll_bc, font=("Segoe UI", 14), border_width=0.6, border_color=scroll_bc, command=lambda: add_config("bypass_updates", bypass_updates_cb.get())) # checkbox for bypass updates
        bypass_updates_cb.place(x=160, y=14.4) # place the checkbox

        rpc_label = customtkinter.CTkLabel(master=scroll_frame, text="Enable Discord RPC:", fg_color=fg_color, text_color=text_color, font=("Segoe UI", 14)) # label for rpc option
        rpc_label.grid(padx=10, pady=10, sticky="w") # place the label in the grid

        rpc_cb = customtkinter.CTkCheckBox(master=scroll_frame, text="", fg_color=scroll_bc, text_color=text_color, hover_color=scroll_bc, font=("Segoe UI", 14), border_width=0.6, border_color=scroll_bc, command=lambda: rpc_change(rpc_cb.get())) # checkbox for rpc
        rpc_cb.place(x=140, y=59.5) # place the checkbox

        if bypass_updates_value: # if bypass_updates is enabled
            bypass_updates_cb.select() # select the checkbox
        else: # if bypass_updates is disabled
            bypass_updates_cb.deselect() # deselect the checkbox

        if rpc_value: # if rpc is enabled
            rpc_cb.select() # select the checkbox
        else: # if rpc is disabled
            rpc_cb.deselect() # deselect the checkbox

        change_standard_picture = customtkinter.CTkLabel(master=scroll_frame, text="Change Standard Wallet Picture:", fg_color=fg_color, text_color=text_color, font=("Segoe UI", 14)) # label for changing standard wallet picture
        change_standard_picture.grid(padx=10, pady=10, sticky="w") # place the label in the grid

        change_standard_picture_button = customtkinter.CTkButton(master=scroll_frame, text=" . . . ", fg_color=scroll_bc, hover_color="#292929", text_color="#FFFFFF", width=20, font=("Segoe UI", 14), command=lambda: wallet_manager.change_standard_picture(self)) # button to change standard wallet picture
        change_standard_picture_button.place(x=220, y=106.5) # place the button

        sort_wallets_by_label = customtkinter.CTkLabel(master=scroll_frame, text="Sort Wallets By:", fg_color=fg_color, text_color=text_color, font=("Segoe UI", 14)) # label for sorting wallets
        sort_wallets_by_label.grid(padx=10, pady=10, sticky="w") # place the label in the grid

        sort_wallets_by_menu = customtkinter.CTkOptionMenu(master=scroll_frame, values=["Oldest First", "Newest First", "A-Z Alphabetical", "Z-A Alphabetical"], fg_color=scroll_bc, button_color=scroll_bc, text_color=text_color, font=("Segoe UI", 14), button_hover_color="#292929", dropdown_fg_color=scroll_bc, dropdown_text_color=text_color, dropdown_hover_color="#292929", command=lambda e: sort_change(sort_wallets_by_menu.get(), self.master)) # option menu for sorting wallets
        sort_wallets_by_menu.set(settings.get("sort_wallets_by", "Oldest First")) # set current value from settings
        sort_wallets_by_menu.place(x=120, y=155) # place the option menu

        title_ = settings.get("title", "MultiExodus - {count} Loaded {s} | {time}") # get current title setting

        custom_title_input = customtkinter.CTkEntry(master=scroll_frame, placeholder_text=title_, fg_color=scroll_bc, text_color=text_color, font=("Segoe UI", 14), width=300, border_width=0.6, border_color=scroll_bc) # entry for custom title
        custom_title_input.grid(padx=10, pady=10, sticky="w") # place the entry in the grid

        custom_title_input.insert(0, title_) # insert current title into entry

        info_extra = "You can use the following variables in the custom title:\n\n{s} - Say Wallet or Wallets if count is 1 or more\n{count} - Number of wallets loaded\n{time} - Current time in HH:MM:SS format\n{date} - Current date in YYYY-MM-DD format\n{username} - Current System Username\n{computername} - Current Computer Name\n{exodus_version} - Installed Exodus Version\n{motd} - Message of the Day" # tooltip info for custom title

        CTkToolTip(custom_title_input, delay=0.5, message=info_extra) # create tooltip for custom title entry

        save_title_button = customtkinter.CTkButton(master=scroll_frame, text="💾", fg_color=scroll_bc, hover_color="#292929", text_color="#FFFFFF", width=10, font=("Segoe UI", 14), command=lambda: title_change(custom_title_input.get())) # button to save custom title
        save_title_button.place(x=320, y=201) # place the save button

        self.after(200, lambda: self.iconbitmap(constants.APP_ICON)) # set the window icon (Thank you https://github.com/aahan0511 ---> https://github.com/TomSchimansky/CustomTkinter/issues/1511#issuecomment-2586303815)

        self.protocol("WM_DELETE_WINDOW", self.destroy) # handle window close event

        self.bind("<Escape>", lambda e: self.destroy()) # bind Escape key to close the window

        self.wait_window() # wait for the window to be closed