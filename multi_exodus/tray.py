from . import settings, update, info, wallet_manager, motd, ui, constants # import necessary modules
from PIL import Image # for image handling
import threading # for threading
import pystray # for system tray icon

tray_icon = None # global variable to hold the tray icon

def read_info(): # function to read info text from info.txt
    with open(constants.INFO_PATH, "r", encoding="utf-8") as f: # load info text from file
        info_text = f.read() # read the entire content of the file

    return info_text # return the info text

def create(root, first_wallet): # function to create the system tray icon and menu
    global tray_icon # use the global tray_icon variable
    def on_quit(): # function to quit the application
        icon.stop() # stop the tray icon
        root.after(0, root.quit) # quit the main application

    info_text = read_info() # read info text for tray menu

    config = settings.read_config() # read settings from settings.json

    menu = pystray.Menu( # create the tray menu
        pystray.MenuItem("Show MultiExodus", lambda: root.after(0, root.deiconify)),
        pystray.MenuItem("────────────────", action=None, enabled=False),
        pystray.MenuItem("Show Information", lambda: info.InfoPopup(root, title="Multi Exodus Information", text=info_text, text_color="#FFFFFF", fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141")),
        pystray.MenuItem("Check for Updates", lambda: update.check_updates(msg_box=True, config=config)),
        pystray.MenuItem("Refresh Wallets UI", lambda: ui.rebuild(root, extra=False)),
        pystray.MenuItem("Encrypt Wallets", lambda: ui.encrypt_now()),
        pystray.MenuItem("────────────────", action=None, enabled=False),
        pystray.MenuItem("Add New Wallet", lambda: wallet_manager.add_wallet(root, lambda r=root: ui.build_wallets_ui(root, *wallet_manager.detect_wallets()), config.get("show_toasts", True))),
        pystray.MenuItem("Load First Wallet", lambda: wallet_manager.load_wallet(first_wallet, config.get("show_toasts", True))),
        pystray.MenuItem("Delete First Wallet", lambda: wallet_manager.delete_wallet(first_wallet, lambda: ui.rebuild(root), config.get("show_toasts", True))),
        pystray.MenuItem("Delete All Wallets", lambda: wallet_manager.delete_all_wallets(lambda: ui.rebuild(root), config.get("show_toasts", True))),
        pystray.MenuItem("────────────────", action=None, enabled=False),
        pystray.MenuItem("Open Data Location", lambda: wallet_manager.open_data_location()),
        pystray.MenuItem("Show Message of the Day", lambda: motd.MotdPopup(root, title="Message of the Day", text_color="#FFFFFF", fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141")),
        pystray.MenuItem("Settings", lambda: settings.SettingsPopup(root, title="Multi Exodus Settings", text_color="#FFFFFF", fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141")),
        pystray.MenuItem("Quit", lambda: on_quit()),
    )

    image = Image.open(constants.APP_ICON) # load tray icon image

    icon = pystray.Icon( # create tray icon
        "MultiExodus",
        image,
        "MultiExodus",
        menu
    )
    
    tray_icon = icon # assign to global variable

    threading.Thread(target=icon.run, daemon=True).start() # run the tray icon in a separate thread

def restart_tray(root, first_wallet): # function to restart the tray icon
    global tray_icon # use the global tray_icon variable
    if tray_icon is not None: # if tray_icon exists, stop it
        tray_icon.stop() # stop the existing tray icon

    create(root, first_wallet) # create a new tray icon