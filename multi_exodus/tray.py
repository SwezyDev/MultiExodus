
from . import settings, update, info, wallet_manager, motd, ui
from PIL import Image
import threading
import pystray

def create(root, first_wallet):
    def on_quit():
        icon.stop()
        root.after(0, root.quit)

    menu = pystray.Menu(
        pystray.MenuItem("Show MultiExodus", lambda: root.after(0, root.deiconify)),
        pystray.MenuItem("────────────────", lambda: None, enabled=False),
        pystray.MenuItem("Show Information", lambda: info.InfoPopup(root, title="Multi Exodus Information", text_color="#FFFFFF", fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141")),
        pystray.MenuItem("Check for Updates", lambda: update.check_updates()),
        pystray.MenuItem("Refresh Wallets UI", lambda: ui.rebuild(root)),
        pystray.MenuItem("────────────────", lambda: None, enabled=False),
        pystray.MenuItem("Add New Wallet", lambda: wallet_manager.add_wallet(root, lambda r=root: ui.build_wallets_ui(root, *wallet_manager.detect_wallets()))),
        pystray.MenuItem("Load First Wallet", lambda: wallet_manager.load_wallet(first_wallet)),
        pystray.MenuItem("Delete First Wallet", lambda: wallet_manager.delete_wallet(first_wallet, lambda: ui.rebuild(root))),
        pystray.MenuItem("Delete All Wallets", lambda: wallet_manager.delete_all_wallets(lambda: ui.rebuild(root))),
        pystray.MenuItem("────────────────", lambda: None, enabled=False),
        pystray.MenuItem("Open Data Location", lambda: wallet_manager.open_data_location()),
        pystray.MenuItem("Show Message of the Day", lambda: motd.MotdPopup(root, title="Message of the Day", text_color="#FFFFFF", fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141")),
        pystray.MenuItem("Settings", lambda: settings.SettingsPopup(root, title="Multi Exodus Settings", text_color="#FFFFFF", fg_color="#202020", scroll_fg="#202020", scroll_bc="#414141")),
        pystray.MenuItem("Quit", lambda: on_quit()),
    )

    image = Image.open("./assets/app.ico")

    icon = pystray.Icon(
        "MultiExodus",
        image,
        "MultiExodus",
        menu
    )

    # run tray icon in its own thread
    threading.Thread(target=icon.run, daemon=True).start()
