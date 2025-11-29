from . import app, wallet_manager, constants, ui
import customtkinter
import ctypes
import json

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

def sort_change(value, root): # function to handle sort option change
    add_config("sort_wallets_by", value) # update the setting in settings.json
    ui.rebuild(root) # rebuild the UI to reflect the new sorting

class SettingsPopup(customtkinter.CTkToplevel): 
    def __init__(self, master=None, title="Settings Popup", text_color="#FFFFFF",
                fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141"):
        super().__init__(master)
        self.title(title)
        app.center_me(self, 400, 500)
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=fg_color)

        settings = read_config()

        if settings.get("bypass_updates", False):
            bypass_updates_value = True
        else:
            bypass_updates_value = False

        scroll_frame = customtkinter.CTkScrollableFrame(master=self, width=360, height=460, fg_color=scroll_fg, border_color=scroll_bc, border_width=0.6)
        scroll_frame.grid(padx=10, pady=10)

        bypass_updates_label = customtkinter.CTkLabel(master=scroll_frame, text="Bypass Update Checks:", fg_color=fg_color, text_color=text_color, font=("Segoe UI", 14))
        bypass_updates_label.grid(padx=10, pady=10, sticky="w")

        bypass_updates_cb = customtkinter.CTkCheckBox(master=scroll_frame, text="", fg_color=scroll_bc, text_color=text_color, hover_color=scroll_bc, font=("Segoe UI", 14), border_width=0.6, border_color=scroll_bc, command=lambda: add_config("bypass_updates", bypass_updates_cb.get()))
        bypass_updates_cb.place(x=160, y=14.4)

        if bypass_updates_value:
            bypass_updates_cb.select()
        else:
            bypass_updates_cb.deselect()

        change_standard_picture = customtkinter.CTkLabel(master=scroll_frame, text="Change Standard Wallet Picture:", fg_color=fg_color, text_color=text_color, font=("Segoe UI", 14))
        change_standard_picture.grid(padx=10, pady=10, sticky="w")

        change_standard_picture_button = customtkinter.CTkButton(master=scroll_frame, text=" . . . ", fg_color=scroll_bc, hover_color="#292929", text_color="#FFFFFF", width=20, font=("Segoe UI", 14), command=lambda: wallet_manager.change_standard_picture(self))
        change_standard_picture_button.place(x=220, y=59.5)

        sort_wallets_by_label = customtkinter.CTkLabel(master=scroll_frame, text="Sort Wallets By:", fg_color=fg_color, text_color=text_color, font=("Segoe UI", 14))
        sort_wallets_by_label.grid(padx=10, pady=10, sticky="w")

        sort_wallets_by_menu = customtkinter.CTkOptionMenu(master=scroll_frame, values=["Oldest First", "Newest First", "A-Z Alphabetical", "Z-A Alphabetical"], fg_color=scroll_bc, button_color=scroll_bc, text_color=text_color, font=("Segoe UI", 14), button_hover_color="#292929", dropdown_fg_color=scroll_bc, dropdown_text_color=text_color, dropdown_hover_color="#292929", command=lambda e: sort_change(sort_wallets_by_menu.get(), self.master))
        sort_wallets_by_menu.set(settings.get("sort_wallets_by", "Oldest First"))
        sort_wallets_by_menu.place(x=120, y=106.5)

        self.after(200, lambda: self.iconbitmap(constants.APP_ICON)) # Thank you https://github.com/aahan0511 ---> https://github.com/TomSchimansky/CustomTkinter/issues/1511#issuecomment-2586303815 

        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.bind("<Escape>", lambda e: self.destroy())

        self.wait_window()