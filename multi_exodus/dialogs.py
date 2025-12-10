from . import app, constants # import app and constants modules
import customtkinter # for custom tkinter widgets

# custom input dialog - credits https://github.com/TomSchimansky/CustomTkinter/issues/1826#issuecomment-1904712879 thank you (who ever you are, your account is deleted :( )

class MyInputDialog(customtkinter.CTkToplevel): # custom input dialog class
    def __init__(self, master=None, title="Input", text="Enter value:",
                fg_color="#202020", text_color="#FFFFFF",
                button_fg_color="#414141", button_hover_color="#2C2C2C", button_text_color="#FFFFFF",
                entry_fg_color="#2C2C2C", entry_border_color="#414141", entry_text_color="#FFFFFF"): # initialize the dialog
        super().__init__(master) # call the parent constructor
        self.title(title) # set the window title
        app.center_me(self, 300, 150) # center the window
        self.resizable(False, False) # make the window non-resizable
        
        self.grab_set() # make the window modal
        self.configure(fg_color=fg_color) # set the background color

        self.result = None # variable to hold the result
        self.cancelled = True # variable to track if cancelled

        label = customtkinter.CTkLabel(master=self, text=text, bg_color=fg_color,
                                    fg_color=fg_color, text_color=text_color) # create the label
        label.pack(padx=10, pady=(10, 5)) # pack the label

        self.entry = customtkinter.CTkEntry(master=self,
                                            fg_color=entry_fg_color,
                                            border_color=entry_border_color,
                                            text_color=entry_text_color, width=510) # create the entry field
        self.entry.pack(padx=10, pady=(0, 10)) # pack the entry field
        self.entry.focus_set() # set focus to the entry field

        button_frame = customtkinter.CTkFrame(master=self, fg_color="transparent", border_width=0) # frame for buttons
        button_frame.pack(pady=5) # pack the button frame

        okay_button = customtkinter.CTkButton(master=button_frame, text="OK",
                                            fg_color=button_fg_color,
                                            hover_color=button_hover_color,
                                            text_color=button_text_color,
                                            command=self.ok, width=135) # create the OK button
        okay_button.pack(side="left", padx=5) # pack the OK button

        cancel_button = customtkinter.CTkButton(master=button_frame, text="Cancel",
                                                fg_color=button_fg_color,
                                                hover_color=button_hover_color,
                                                text_color=button_text_color,
                                                command=self.cancel, width=135) # create the Cancel button
        cancel_button.pack(side="left", padx=5) # pack the Cancel button

        self.after(200, lambda: self.iconbitmap(constants.APP_ICON)) # set the window icon (Thank you https://github.com/aahan0511 ---> https://github.com/TomSchimansky/CustomTkinter/issues/1511#issuecomment-2586303815)

        self.protocol("WM_DELETE_WINDOW", self.cancel) # handle window close event

        self.bind("<Return>", lambda e: self.ok()) # bind Enter key to OK
        self.bind("<Escape>", lambda e: self.cancel()) # bind Escape key to Cancel

        self.wait_window() # wait for the window to be closed

    def ok(self): # function to handle OK button click
        self.result = self.entry.get() # get the input value
        self.cancelled = False # mark as not cancelled
        self.destroy() # close the dialog

    def cancel(self): # function to handle Cancel button click
        self.result = None # clear the result
        self.cancelled = True # mark as cancelled
        self.destroy() # close the dialog

    def get_input(self): # function to get the input value
        return self.result # return the input value
