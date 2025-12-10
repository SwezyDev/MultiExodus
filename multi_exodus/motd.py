from . import app, constants
import customtkinter
import requests

def get_motd(): # function to get the message of the day from a remote source
    print("Test")
    try: # try to fetch the motd
        response = requests.get("https://raw.githubusercontent.com/SwezyDev/MultiExodus/main/assets/motd.txt", timeout=5) # fetch motd from github
        if response.status_code == 200: # check if the request was successful
            return response.text # return the motd text
        else: # if request failed
            return "No Message of the Day available." # return default message if fetch failed
    except requests.RequestException: # catch any request exceptions
        return "No Message of the Day available." # return default message if fetch failed

class MotdPopup(customtkinter.CTkToplevel): 
    def __init__(self, master=None, title="Motd Popup", text_color="#FFFFFF",
                fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141"):
        super().__init__(master)
        self.title(title)
        app.center_me(self, 400, 200)
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=fg_color)

        text = get_motd()

        scroll_frame = customtkinter.CTkScrollableFrame(master=self, width=380, height=460, fg_color=fg_color, border_color=scroll_bc, border_width=0.6)
        scroll_frame.pack(padx=10, pady=10)

        info_label = customtkinter.CTkLabel(master=scroll_frame, text=text, fg_color=fg_color, text_color=text_color, font=("Segoe UI", 14), wraplength=325, justify="left")
        info_label.pack(padx=10, pady=10)

        self.after(200, lambda: self.iconbitmap(constants.APP_ICON)) # Thank you https://github.com/aahan0511 ---> https://github.com/TomSchimansky/CustomTkinter/issues/1511#issuecomment-2586303815 

        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.bind("<Escape>", lambda e: self.destroy())

        self.wait_window()
