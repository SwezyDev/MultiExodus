import customtkinter
from . import app

class InfoPopup(customtkinter.CTkToplevel): 
    def __init__(self, master=None, title="Info Popup", text="Example Text", text_color="#FFFFFF",
                fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141"):
        super().__init__(master)
        self.title(title)
        app.center_me(self, 400, 500)
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=fg_color)

        scroll_frame = customtkinter.CTkScrollableFrame(master=self, width=380, height=460, fg_color=fg_color, border_color=scroll_bc, border_width=0.6)
        scroll_frame.pack(padx=10, pady=10)

        info_label = customtkinter.CTkLabel(master=scroll_frame, text=text, fg_color=fg_color, text_color=text_color, font=("Segoe UI", 14), wraplength=325, justify="left")
        info_label.pack(padx=10, pady=10)

        self.after(200, lambda: self.iconbitmap(r"./assets/app.ico")) # Thank you https://github.com/aahan0511 ---> https://github.com/TomSchimansky/CustomTkinter/issues/1511#issuecomment-2586303815 

        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.bind("<Escape>", lambda e: self.destroy())

        self.wait_window()
