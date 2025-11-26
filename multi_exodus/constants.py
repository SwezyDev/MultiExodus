from pathlib import Path
import os

LOCAL_APPDATA = Path(os.getenv("LOCALAPPDATA")) # windows local appdata folder
ROAMING_APPDATA = Path(os.getenv("APPDATA")) # windows roaming appdata folder
MULTI_WALLET_DIR = ROAMING_APPDATA / "MultiExodus" # directory to store multiple exodus wallets

EXODUS_WALLET = ROAMING_APPDATA / "Exodus" # default exodus wallet directory
EXODUS_DIR = LOCAL_APPDATA / "exodus" # default exodus application data directory

GITHUB_REPO = "SwezyDev/MultiExodus" # github repository for multi exodus