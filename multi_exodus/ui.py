from .constants import MULTI_WALLET_DIR
from . import wallet_manager
from PIL import Image
import customtkinter

scroll_frame = None # global variable to hold the scrollable frame

def build_wallets_ui(root, names, count): # function to build the wallets ui
    global scroll_frame # use the global scroll_frame variable

    if scroll_frame is not None: # if scroll_frame already exists, destroy it
        try: 
            scroll_frame.destroy() # destroy the existing scroll_frame
        except Exception:
            pass

    scroll_frame = customtkinter.CTkScrollableFrame(master=root, width=1355, height=680, fg_color="#202020") # create a new scrollable frame
    scroll_frame.place(x=10, y=10) # place the scrollable frame in the main window

    def rebuild(): # function to rebuild the ui
        scroll_frame.destroy() # destroy current scroll frame
        build_wallets_ui(root, *wallet_manager.detect_wallets()) # rebuild the ui with updated wallet list

    for i in range(count): # create wallet frames for each detected wallet
        row = i // 5 # calculate the row position for the wallet frame
        col = i % 5  # calculate the column position for the wallet frame
        standard_frame = customtkinter.CTkFrame( # create a frame for each wallet
            master=scroll_frame, width=250, height=250,
            fg_color="#202020", border_color="#414141",
            border_width=0.6, corner_radius=12
        )
        standard_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nw") # place the wallet frame in the grid

        wallet_name = names[i] # get the wallet name
        wallet_picture_path = MULTI_WALLET_DIR / wallet_name / "title.png" # path to wallet image
        wallet_note_path = MULTI_WALLET_DIR / wallet_name / "note.txt" # path to wallet note
        image_height = 130 # height of the wallet image
        top_margin = 10 # top margin for the wallet image
        spacing = 5 # spacing between image and labels

        if wallet_picture_path.exists(): # if wallet image exists, load and display it
            pil_image = Image.open(wallet_picture_path).resize((130, image_height)) # load and resize image
            pil_image = wallet_manager.round_corners(pil_image, radius=12) # round image corners
            wallet_image = customtkinter.CTkImage( # create a CTkImage from the PIL image
                light_image=pil_image,
                dark_image=pil_image,
                size=(130, image_height)
            )
            image_label = customtkinter.CTkLabel(master=standard_frame, image=wallet_image, text="") # create label for the image
            image_label.place(relx=0.5, y=top_margin + image_height // 2, anchor="center") # place the image label

        label = customtkinter.CTkLabel( # create label for wallet name
            master=standard_frame, text=wallet_name,
            fg_color="#202020", font=("Segoe UI", 16)
        )
        label.current_name = wallet_name # store current name in label attribute
        label.place(relx=0.5, y=top_margin + image_height + spacing, anchor="n") # place the wallet name label

        note_text = " " * 50 # default empty note text
        if wallet_note_path.exists(): # if wallet note exists, load and display it
            with open(wallet_note_path, "r", encoding="utf-8") as note_file: # open the note file
                note_text = note_file.read()[:36] # read the note text (up to 36 characters)

        note_label = customtkinter.CTkLabel( # create label for wallet note
            master=standard_frame, text=note_text,
            fg_color="#202020", font=("Segoe UI", 12),
            wraplength=220, justify="center"
        )
        note_label.place(relx=0.5, y=top_margin + image_height + spacing + 30, anchor="n") # place the wallet note label under wallet name label

        load_button = customtkinter.CTkButton( # create button to load wallet
            master=standard_frame, text="Load Wallet",
            fg_color="#414141", hover_color="#2C2C2C",
            font=("Segoe UI", 14), width=200, height=30,
            command=lambda wn=wallet_name: wallet_manager.load_wallet(wn)
        )
        load_button.place(relx=0.5, y=210, anchor="n") # place the load button under note label

        label.bind("<Button-1>", lambda e, lbl=label: wallet_manager.edit_wallet_name(lbl, MULTI_WALLET_DIR)) # bind click event to edit wallet name
        note_label.bind("<Button-1>", lambda e, lbl=note_label, path=wallet_note_path: wallet_manager.edit_wallet_note(lbl, path)) # bind click event to edit wallet note

        if wallet_picture_path.exists(): # if wallet image exists, bind click event to edit image
            image_label.bind("<Button-1>", lambda e, path=wallet_picture_path: edit_img_rebuild(path, rebuild, root)) # bind click event to edit wallet image

        delete_button = customtkinter.CTkButton( # create button to delete wallet
            master=standard_frame, text="🗑",
            fg_color="#202020", hover_color="#202020", text_color="#FF0000",
            font=("Segoe UI", 14), width=0, height=0,
            command=lambda wn=wallet_name: wallet_manager.delete_wallet(wn, rebuild)
        )
        delete_button.place(x=215, y=5) # place the delete button at top-right corner

    add_frame_index = count # index for the "Add Wallet"
    add_frame_row = add_frame_index // 5 # row position
    add_frame_col = add_frame_index % 5 # column position
    add_frame = customtkinter.CTkFrame( # create frame for "Add Wallet"
        master=scroll_frame, width=250, height=250,
        fg_color="#181818", border_color="#414141",
        border_width=0.6, corner_radius=12
    )
    add_frame.grid(row=add_frame_row, column=add_frame_col, padx=10, pady=10, sticky="nw") # place the "Add Wallet" frame in the grid

    plus_label = customtkinter.CTkLabel( # create label for the plus sign
        master=add_frame, text="+", font=("Segoe UI", 70),
        text_color="#4CAF50"
    )
    plus_label.place(relx=0.5, rely=0.5, anchor="center") # center the plus label
    
    add_frame.bind("<Button-1>", lambda e: wallet_manager.add_wallet(root, lambda r=root: build_wallets_ui(root, *wallet_manager.detect_wallets()))) # bind click event to add wallet
    plus_label.bind("<Button-1>", lambda e: wallet_manager.add_wallet(root, lambda r=root: build_wallets_ui(root, *wallet_manager.detect_wallets()))) # bind click event to add wallet


def edit_img_rebuild(path, rebuild, root): # helper function to edit wallet image and rebuild ui
    from customtkinter import filedialog
    from PIL import Image
    file_path = filedialog.askopenfilename(title="Select new wallet image", filetypes=[("PNG Images", "*.png")]) # open file dialog to select new image
    
    if file_path: # if a file was selected
        pil_image = Image.open(file_path).resize((200, 130)) # open and resize the selected image
        pil_image.save(path) # save the new image to the specified path
        rebuild() # rebuild the UI to reflect the changes