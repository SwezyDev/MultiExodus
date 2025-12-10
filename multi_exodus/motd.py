from . import app, constants # import app and constants modules
import customtkinter # for custom tkinter widgets
import requests # for making http requests

def get_motd(): # function to get the message of the day from a remote source
    try: # try to fetch the motd
        response = requests.get(f"https://raw.githubusercontent.com/{constants.GITHUB_REPO}/main/assets/motd.txt", timeout=5) # fetch motd from github
        if response.status_code == 200: # check if the request was successful
            return response.text # return the motd text
        else: # if request failed
            return "No Message of the Day available." # return default message if fetch failed
    except requests.RequestException: # catch any request exceptions
        return "No Message of the Day available." # return default message if fetch failed

class MotdPopup(customtkinter.CTkToplevel): # class for the Message of the Day popup window
    def __init__(self, master=None, title="Motd Popup", text_color="#FFFFFF", 
                fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141"): # initialize the popup window
        super().__init__(master) # call the parent constructor
        self.title(title) # set the window title
        app.center_me(self, 400, 200) # center the window on the screen
        self.resizable(False, False) # make the window non-resizable 
        self.grab_set() # make the window modal
        self.configure(fg_color=fg_color) # set the background color

        text = get_motd() # get the message of the day text

        scroll_frame = customtkinter.CTkScrollableFrame(master=self, width=380, height=460, fg_color=fg_color, border_color=scroll_bc, border_width=0.6) # create the scrollable frame
        scroll_frame.pack(padx=10, pady=10) # create and pack the scrollable frame

        info_label = customtkinter.CTkLabel(master=scroll_frame, text=text, fg_color=fg_color, text_color=text_color, font=("Segoe UI", 14), wraplength=325, justify="left") # create the label with the motd text
        info_label.pack(padx=10, pady=10) # create and pack the label with the motd text

        self.after(200, lambda: self.iconbitmap(constants.APP_ICON)) # set the window icon (Thank you https://github.com/aahan0511 ---> https://github.com/TomSchimansky/CustomTkinter/issues/1511#issuecomment-2586303815)

        self.protocol("WM_DELETE_WINDOW", self.destroy) # handle window close event

        self.bind("<Escape>", lambda e: self.destroy()) # bind Escape key to close the window

        self.wait_window() # wait for the window to be closed
