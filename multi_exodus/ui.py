from .constants import MULTI_WALLET_DIR # for multi-wallet directory path
from CTkToolTip import CTkToolTip # for tooltips
from .settings import read_config # for reading settings configuration
from .tray import restart_tray # for restarting the tray icon
from .rpc import restart_rpc # for restarting the rpc server
from . import wallet_manager, protection, app # for wallet management functions and protection functions
from PIL import Image # for image handling
import customtkinter # for custom tkinter widgets
import ctypes # for Windows message boxes

scroll_frame = None # global variable to hold the scrollable frame
search_frame = None # global variable to hold the search frame
wallet_cache = [] # chache for wallet names
layout_mode = "grid" # global variable to hold the layout mode "grid" or "list"

def rebuild(root, extra=True): # function to rebuild the ui
    from .app import bind_keybinds, restart_title # import bind_keybinds and restart_title functions
    scroll_frame.destroy() # destroy current scroll frame
    search_frame.destroy() # destroy current search frame
    names, count = wallet_manager.detect_wallets() # detect wallets again
    bind_keybinds(root, names[0] if names else None) # rebind keybinds
    restart_tray(root, names[0] if names else None) # restart the tray icon to refresh menu
    build_wallets_ui(root, names, count) # rebuild the ui with updated wallet list
    if extra: # if extra is true call the restart_title and restart_rpc function. (Performance improvement)
        restart_title() # restart the window title with updated wallet count
        restart_rpc(count) # restart the rpc server with updated wallet count

def toggle_layout(): # function to toggle between grid and list layout
    global layout_mode # use the global layout_mode variable
    layout_mode = "list" if layout_mode == "grid" else "grid" # toggle layout mode
    layout_button.configure(text="☷" if layout_mode == "list" else "☰") # update button text
    on_search()  # rerender with the new layout

def encrypt_now(): # function to open encryption settings
    config = read_config() # read settings configuration
    
    name, count = wallet_manager.detect_wallets() # detect wallets
    if count == 0: # if no wallet data exists
        ctypes.windll.user32.MessageBoxW(0, "You don't have any saved Wallets. There is nothing to Encrypt.", "MultiExodus", 0x30) # show error message box
        return # exit the function
    
    returns = protection.encrypt() # call the encrypt function
    if returns and not returns in ["doesnt match", "cancel"]: # if encryption was successful
        ctypes.windll.user32.MessageBoxW(0, "All wallets have been successfully encrypted.", "MultiExodus", 0x40) # show success message box
        if config.get("show_toasts", True): # if toasts are enabled in setting
            wallet_manager.show_toast("MultiExodus", "All wallets have been successfully encrypted.") # show success toast
        
        app.restart_app()
    elif returns == False and not returns in ["doesnt match", "cancel"]: # if encryption failed or was aborted
        ctypes.windll.user32.MessageBoxW(0, "Wallet encryption failed or was aborted.", "MultiExodus", 0x30) # show failure message box
        if config.get("show_toasts", True): # if toasts are enabled in setting
            wallet_manager.show_toast("MultiExodus", "Wallet encryption failed or was aborted.") # show failure toast
    else: # if passwords do not match
        pass # do nothing if passwords do not match

def build_wallets_ui(root, names, count): # function to build the wallets ui
    global scroll_frame, search_frame, wallet_cache, layout_mode, layout_button, on_search # use the global scroll_frame, search_frame variables

    if scroll_frame is not None: # if scroll_frame already exists, destroy it
        try: # attempt to destroy existing scroll_frame
            scroll_frame.destroy() # destroy the existing scroll_frame
        except Exception: # catch any exceptions
            pass # ignore exceptions

    if search_frame is not None: # if search_frame already exists, destroy it
        try: # attempt to destroy existing search_frame
            search_frame.destroy() # destroy the existing search_frame
        except Exception: # catch any exceptions
            pass # ignore exceptions

    config = read_config() # read the settings configuration

    scroll_frame = customtkinter.CTkScrollableFrame(master=root, width=1345, height=630, fg_color="#202020") # create a new scrollable frame
    scroll_frame.place(x=10, y=44) # place the scrollable frame in the main window

    search_frame = customtkinter.CTkFrame(master=root, width=250, height=30, fg_color="#202020", border_color="#414141", border_width=0.6, corner_radius=8) # create a frame for the search bar
    search_frame.place(x=26, y=10) # place the search frame at the top-left corner of the scrollable frame
    
    search_bar = customtkinter.CTkEntry( # create a search bar
        master=search_frame, width=250, height=30,
        fg_color="#2C2C2C", border_color="#414141",
        border_width=0.6, corner_radius=8,
        placeholder_text="Search Wallets..."
    )
    search_bar.place(x=0, y=0) # place the search bar below the scrollable frame
    
    layout_button = customtkinter.CTkButton( # create a button to toggle layout
        master=root, text="☷" if layout_mode == "list" else "☰",
        width=35, height=30,
        fg_color="#2C2C2C", hover_color="#414141",
        border_color="#414141", border_width=0.6,
        corner_radius=8,
        font=("Segoe UI", 16),
        command=toggle_layout
    )
    layout_button.place(x=285, y=10) # place the layout toggle button next to the search bar

    wallet_cache = list(names) # populate wallet_cache with wallet names

    encrypt_button = customtkinter.CTkButton( # create a button to open encryption settings
        master=root, text="🔒",
        width=35, height=30,
        fg_color="#2C2C2C", hover_color="#414141",
        border_color="#414141", border_width=0.6,
        corner_radius=8,
        font=("Segoe UI", 16),
        command=encrypt_now
    )
    encrypt_button.place(x=1315, y=10) # place the encryption settings button next to the layout toggle button

    def sort_wallets_by_star(wallet_list): # function to sort wallets with starred ones first
        starred = [] # list for starred wallets
        unstarred = [] # list for unstarred wallets
        for wallet in wallet_list: # iterate through wallets
            if wallet_manager.is_wallet_starred(wallet): # if wallet is starred
                starred.append(wallet) # add to starred list
            else: # if wallet is not starred
                unstarred.append(wallet) # add to unstarred list
        return starred + unstarred # return starred wallets first, then unstarred

    def render_wallets(wallet_list, show_add_frame=True):
        wallet_list = sort_wallets_by_star(wallet_list) # sort wallets with starred ones first
        for widget in scroll_frame.winfo_children(): # clear existing wallet frames
            widget.destroy() # destroy each child widget in the scrollable frame

        if layout_mode == "grid":
            render_grid_layout(wallet_list, show_add_frame)
        else:
            render_list_layout(wallet_list, show_add_frame)

    def render_grid_layout(wallet_list, show_add_frame=True): # function to render wallets in grid layout
        for i, wallet_name in enumerate(wallet_list): # create wallet frames for each detected wallet
            row = i // 5 # calculate the row position for the wallet frame
            col = i % 5  # calculate the column position for the wallet frame
            standard_frame = customtkinter.CTkFrame( # create a frame for each wallet
                master=scroll_frame, width=250, height=250,
                fg_color="#202020", border_color="#414141",
                border_width=0.6, corner_radius=12
            )
            standard_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nw") # place the wallet frame in the grid

            def on_hover(event): # function to handle hover event
                    root.focus_set() # remove focus from search bar

            root.bind("<Enter>", on_hover) # bind hover event to clear search and unfocus

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
                fg_color="#202020", font=("Segoe UI", 18, "bold")
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

            tags = wallet_manager.get_wallet_tags(wallet_name) # get wallet tags (max 5 tags)

            # there is no space for the tags lol, only visible in list view :(

            load_button = customtkinter.CTkButton( # create button to load wallet
                master=standard_frame, text="Load Wallet",
                fg_color="#414141", hover_color="#2C2C2C",
                font=("Segoe UI", 14), width=200, height=30,
                command=lambda lbl=label: wallet_manager.load_wallet(lbl.current_name, config.get("show_toasts", True))
            )
            load_button.place(relx=0.5, y=210, anchor="n") # place the load button under note label

            label.bind("<Button-1>", lambda e, lbl=label: wallet_manager.edit_wallet_name(lbl, MULTI_WALLET_DIR)) # bind click event to edit wallet name
            note_label.bind("<Button-1>", lambda e, lbl=note_label, path=wallet_note_path: wallet_manager.edit_wallet_note(lbl, path)) # bind click event to edit wallet note

            if wallet_picture_path.exists(): # if wallet image exists, bind click event to edit image
                image_label.bind("<Button-1>", lambda e, path=wallet_picture_path: edit_img_rebuild(path, rebuild, root)) # bind click event to edit wallet image

            CTkToolTip( # create tooltip for wallet frame
                image_label if wallet_picture_path.exists() else standard_frame, delay=0.5,
                message=wallet_manager.show_wallet_info(wallet_name, tags)
            )

            delete_button = customtkinter.CTkButton( # create button to delete wallet
                master=standard_frame, text="🗑",
                fg_color="#202020", hover_color="#202020", text_color="#FF0000",
                font=("Segoe UI", 14), width=0, height=0,
                command=lambda lbl=label: wallet_manager.delete_wallet(lbl.current_name, lambda: rebuild(root), config.get("show_toasts", True))
            )
            delete_button.place(x=215, y=5) # place the delete button at top-right corner

            folder_button = customtkinter.CTkButton( # create button to open wallet location
                master=standard_frame, text="📂",
                fg_color="#202020", hover_color="#202020", text_color="#FFC400",
                font=("Segoe UI", 14), width=0, height=0,
                command=lambda lbl=label: wallet_manager.open_wallet(lbl.current_name)
            )
            folder_button.place(x=215, y=30) # place the folder button at top-right corner

            star_icon = " ★" if wallet_manager.is_wallet_starred(wallet_name) else " ☆" # determine star icon
            star_button = customtkinter.CTkButton( # create button to toggle wallet star
                master=standard_frame, text=star_icon,
                fg_color="#202020", hover_color="#202020", text_color="#006EFF",
                font=("Segoe UI", 14), width=0, height=0,
                command=lambda lbl=label: wallet_manager.toggle_wallet_star(lbl.current_name, lambda: rebuild(root, extra=False))
            )
            star_button.place(x=213, y=55) # place the star button below folder button

        add_frame_index = count # index for the "Add Wallet"
        add_frame_row = add_frame_index // 5 # row position
        add_frame_col = add_frame_index % 5 # column position
        
        if show_add_frame: # only show add_frame if show_add_frame is True
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

            add_frame.bind("<Button-1>", lambda e: wallet_manager.add_wallet(root, lambda r=root: build_wallets_ui(root, *wallet_manager.detect_wallets()), config.get("show_toasts", True))) # bind click event to add wallet
            plus_label.bind("<Button-1>", lambda e: wallet_manager.add_wallet(root, lambda r=root: build_wallets_ui(root, *wallet_manager.detect_wallets()), config.get("show_toasts", True))) # bind click event to add wallet

    def render_list_layout(wallet_list, show_add_frame=True): # function to render wallets in list layout
        for i, wallet_name in enumerate(wallet_list): # create wallet frames for each detected wallet
            standard_frame = customtkinter.CTkFrame( # create a frame for each wallet
                master=scroll_frame, width=1330, height=180,
                fg_color="#202020", border_color="#414141",
                border_width=0.6, corner_radius=12
            )
            standard_frame.grid(row=i, column=0, padx=10, pady=10, sticky="ew") # place the wallet frame in the grid
            standard_frame.grid_propagate(False) # prevent frame from resizing

            def on_hover(event): # function to handle hover event
                    root.focus_set() # remove focus from search bar

            root.bind("<Enter>", on_hover) # bind hover event to clear search and unfocus

            wallet_picture_path = MULTI_WALLET_DIR / wallet_name / "title.png" # path to wallet image
            wallet_note_path = MULTI_WALLET_DIR / wallet_name / "note.txt" # path to wallet note

            if wallet_picture_path.exists(): # if wallet image exists, load and display it
                pil_image = Image.open(wallet_picture_path).resize((150, 150)) # load and resize image
                pil_image = wallet_manager.round_corners(pil_image, radius=12) # round image corners
                wallet_image = customtkinter.CTkImage( # create a CTkImage from the PIL image
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(150, 150)
                )
                image_label = customtkinter.CTkLabel(master=standard_frame, image=wallet_image, text="") # create label for the image
                image_label.place(x=15, y=15) # place the image label on the left

            label = customtkinter.CTkLabel( # create label for wallet name
                master=standard_frame, text=wallet_name,
                fg_color="#202020", font=("Segoe UI", 18, "bold")
            )
            label.current_name = wallet_name # store current name in label attribute
            label.place(x=180, y=20, anchor="nw") # place the wallet name label

            note_text = " " * 50 # default empty note text
            if wallet_note_path.exists(): # if wallet note exists, load and display it
                with open(wallet_note_path, "r", encoding="utf-8") as note_file: # open the note file
                    note_text = note_file.read()[:100] # read the note text (up to 100 characters for list view)

            note_label = customtkinter.CTkLabel( # create label for wallet note
                master=standard_frame, text=note_text,
                fg_color="#202020", font=("Segoe UI", 12),
                wraplength=950, justify="left", anchor="w"
            )
            note_label.place(x=180, y=55, anchor="nw") # place the wallet note label under wallet name label

            tags_container = customtkinter.CTkFrame( # create container for tags
                master=standard_frame, width=1124, height=24,
                fg_color="#202020"
            )
            tags_container.place(x=180, y=95, anchor="nw") # place the tags container under wallet note label

            tags_container.bind("<Button-1>", lambda e, lbl=label: wallet_manager.edit_wallet_tags(lbl.current_name, None, lambda: rebuild(root, extra=False))) # bind click to edit tags

            tags = wallet_manager.get_wallet_tags(wallet_name) # get wallet tags (max 5 tags)
            if not tags: # if no tags, show "No Tags" label
                tag_label = customtkinter.CTkLabel( # create label for "No Tags"
                    master=tags_container, text="No Tags",
                    fg_color="#202020", font=("Segoe UI", 11),
                    text_color="#666666"
                )
                tag_label.place(x=0, y=0, anchor="nw") # place the "No Tags" label
                tag_label.bind("<Button-1>", lambda e, lbl=label: wallet_manager.edit_wallet_tags(lbl.current_name, None, lambda: rebuild(root, extra=False))) # bind click to edit tags
            else: # display each tag as a separate label
                x = 0 # initial x position for tags
                for t in tags: # iterate through each tag
                    tag_label = customtkinter.CTkLabel( # create label for each tag
                        master=tags_container, text=t,
                        fg_color="#202020", font=("Segoe UI", 11),
                        text_color="#666666", corner_radius=0
                    ) # create label for each tag
                    tag_label.place(x=x, y=0, anchor="nw") # place the tag label
                    tag_label.update_idletasks() # update to get correct width
                    x += tag_label.winfo_reqwidth() + 10 # update x position for next tag
                    tag_label.bind("<Button-3>", lambda e, tag=t, wname=wallet_name: wallet_manager.delete_wallet_tag(wname, tag, lambda: rebuild(root, extra=False))) # bind right-click to delete tag
                    tag_label.bind("<Button-1>", lambda e, lbl=label: wallet_manager.edit_wallet_tags(lbl.current_name, None, lambda: rebuild(root, extra=False))) # bind click to edit tags

            load_button = customtkinter.CTkButton( # create button to load wallet
                master=standard_frame, text="Load Wallet",
                fg_color="#414141", hover_color="#2C2C2C",
                font=("Segoe UI", 14), width=1134, height=35,
                command=lambda lbl=label: wallet_manager.load_wallet(lbl.current_name, config.get("show_toasts", True))
            )
            load_button.place(x=180, y=130, anchor="nw") # place the load button stretched at the bottom

            label.bind("<Button-1>", lambda e, lbl=label: wallet_manager.edit_wallet_name(lbl, MULTI_WALLET_DIR)) # bind click event to edit wallet name
            note_label.bind("<Button-1>", lambda e, lbl=note_label, path=wallet_note_path: wallet_manager.edit_wallet_note(lbl, path)) # bind click event to edit wallet note

            if wallet_picture_path.exists(): # if wallet image exists, bind click event to edit image
                image_label.bind("<Button-1>", lambda e, path=wallet_picture_path: edit_img_rebuild(path, rebuild, root)) # bind click event to edit wallet image

            CTkToolTip( # create tooltip for wallet frame
                image_label if wallet_picture_path.exists() else standard_frame, delay=0.5,
                message=wallet_manager.show_wallet_info(wallet_name, tags)
            )

            delete_button = customtkinter.CTkButton( # create button to delete wallet
                master=standard_frame, text="🗑",
                fg_color="#202020", hover_color="#202020", text_color="#FF0000",
                font=("Segoe UI", 14), width=0, height=0,
                command=lambda lbl=label: wallet_manager.delete_wallet(lbl.current_name, lambda: rebuild(root), config.get("show_toasts", True))
            )
            delete_button.place(x=1280, y=10) # place the delete button at top-right corner

            folder_button = customtkinter.CTkButton( # create button to open wallet location
                master=standard_frame, text="📂",
                fg_color="#202020", hover_color="#202020", text_color="#FFC400",
                font=("Segoe UI", 14), width=0, height=0,
                command=lambda lbl=label: wallet_manager.open_wallet(lbl.current_name)
            )
            folder_button.place(x=1280, y=40) # place the folder button below delete button

            star_icon = " ★" if wallet_manager.is_wallet_starred(wallet_name) else " ☆" # determine star icon
            star_button = customtkinter.CTkButton( # create button to toggle wallet star
                master=standard_frame, text=star_icon,
                fg_color="#202020", hover_color="#202020", text_color="#006EFF",
                font=("Segoe UI", 14), width=0, height=0,
                command=lambda lbl=label: wallet_manager.toggle_wallet_star(lbl.current_name, lambda: rebuild(root, extra=False))
            )
            star_button.place(x=1278, y=70) # place the star button below folder button

        if show_add_frame: # only show add_frame if show_add_frame is True
            add_frame = customtkinter.CTkFrame( # create frame for "Add Wallet"
                master=scroll_frame, width=1330, height=180,
                fg_color="#181818", border_color="#414141",
                border_width=0.6, corner_radius=12
            )
            add_frame.grid(row=len(wallet_list), column=0, padx=10, pady=10, sticky="ew") # place the "Add Wallet" frame in the grid

            plus_label = customtkinter.CTkLabel( # create label for the plus sign
                master=add_frame, text="+", font=("Segoe UI", 50),
                text_color="#4CAF50"
            )
            plus_label.place(relx=0.5, rely=0.5, anchor="center") # center the plus label

            add_frame.bind("<Button-1>", lambda e: wallet_manager.add_wallet(root, lambda r=root: build_wallets_ui(root, *wallet_manager.detect_wallets()), config.get("show_toasts", True))) # bind click event to add wallet
            plus_label.bind("<Button-1>", lambda e: wallet_manager.add_wallet(root, lambda r=root: build_wallets_ui(root, *wallet_manager.detect_wallets()), config.get("show_toasts", True))) # bind click event to add wallet


    def on_search(event=None): # function to handle search input
        query = search_bar.get().lower() # get search guery in lower chars
        if not query: # if query is empty
            filtered = wallet_cache # if query is empty, show all wallets
            render_wallets(filtered, show_add_frame=True) # render all wallets with add button
        else: # if query is not empty
            filtered = [] # initialize filtered list
            for name in wallet_cache: # iterate through all wallet names
                # Check if query matches wallet name
                if query in name.lower(): # if query is in wallet name
                    filtered.append(name) # add to filtered list
                    continue # skip to next wallet
                # Check if query matches any tags
                tags = wallet_manager.get_wallet_tags(name) # get wallet tags
                if any(query in tag.lower() for tag in tags): # if query matches any tag
                    filtered.append(name) # add to filtered list
            render_wallets(filtered, show_add_frame=False) # render the filtered wallet list without add button

    search_bar.bind("<KeyRelease>", on_search) # bind key release event to search bar

    render_wallets(wallet_cache) # render all wallets initially

def edit_img_rebuild(path, rebuild, root): # helper function to edit wallet image and rebuild ui
    from customtkinter import filedialog # import filedialog from customtkinter
    file_path = filedialog.askopenfilename(title="Select new wallet image", filetypes=[("PNG Images", "*.png")]) # open file dialog to select new image
    
    if file_path: # if a file was selected
        pil_image = Image.open(file_path).resize((130, 130)) # open and resize the selected image
        pil_image.save(path) # save the new image to the specified path
        rebuild(root, extra=False) # rebuild the UI to reflect the changes