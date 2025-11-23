from . import app
import customtkinter

# custom input dialog - credits https://github.com/TomSchimansky/CustomTkinter/issues/1826#issuecomment-1904712879 thank you (who ever you are, your account is deleted :( )

class MyInputDialog(customtkinter.CTkToplevel): 
    def __init__(self, master=None, title="Input", text="Enter value:",
                fg_color="#202020", text_color="#FFFFFF",
                button_fg_color="#414141", button_hover_color="#2C2C2C", button_text_color="#FFFFFF",
                entry_fg_color="#2C2C2C", entry_border_color="#414141", entry_text_color="#FFFFFF"):
        super().__init__(master)
        self.title(title)
        app.center_me(self, 300, 150)
        self.resizable(False, False)
        
        self.grab_set()
        self.configure(fg_color=fg_color)

        self.result = None
        self.cancelled = True

        label = customtkinter.CTkLabel(master=self, text=text, bg_color=fg_color,
                                    fg_color=fg_color, text_color=text_color)
        label.pack(padx=10, pady=(10, 5))

        self.entry = customtkinter.CTkEntry(master=self,
                                            fg_color=entry_fg_color,
                                            border_color=entry_border_color,
                                            text_color=entry_text_color, width=510)
        self.entry.pack(padx=10, pady=(0, 10))
        self.entry.focus_set()

        button_frame = customtkinter.CTkFrame(master=self, fg_color="transparent", border_width=0)
        button_frame.pack(pady=5)

        okay_button = customtkinter.CTkButton(master=button_frame, text="OK",
                                            fg_color=button_fg_color,
                                            hover_color=button_hover_color,
                                            text_color=button_text_color,
                                            command=self.ok, width=135)
        okay_button.pack(side="left", padx=5)

        cancel_button = customtkinter.CTkButton(master=button_frame, text="Cancel",
                                                fg_color=button_fg_color,
                                                hover_color=button_hover_color,
                                                text_color=button_text_color,
                                                command=self.cancel, width=135)
        cancel_button.pack(side="left", padx=5)

        self.after(200, lambda: self.iconbitmap(r"./assets/app.ico")) # Thank you https://github.com/aahan0511 ---> https://github.com/TomSchimansky/CustomTkinter/issues/1511#issuecomment-2586303815 

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.bind("<Return>", lambda e: self.ok())
        self.bind("<Escape>", lambda e: self.cancel())

        self.wait_window()

    def ok(self):
        self.result = self.entry.get()
        self.cancelled = False
        self.destroy()

    def cancel(self):
        self.result = None
        self.cancelled = True
        self.destroy()

    def get_input(self):
        return self.result
