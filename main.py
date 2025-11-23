from multi_exodus import main, constants
import ctypes
import os

if __name__ == '__main__': 
    print("Welcome to MultiExodus Wallet Manager!")
    print("-------------------------------------")
    print("Made with love by Swezy <3")
    print("https://github.com/SwezyDev")
    print("-------------------------------------")
    print("Contact: https://t.me/Swezy")
    # print some info to the console about the project :)

    if not constants.MULTI_WALLET_DIR.exists(): # check if the MultiExodus directory exists
        constants.MULTI_WALLET_DIR.mkdir(parents=True, exist_ok=True) # create the directory if it doesnt exist

    if not constants.EXODUS_DIR.exists(): # check if the Exodus directory exists
        ctypes.windll.user32.MessageBoxW(0, f"Exodus directory not found! Please install Exodus wallet first.", "MultiExodus", 0x03 | 0x30) # show backup confirmation dialog
        os.system("start https://www.exodus.com/download/") # open Exodus download page
        os._exit(0) # exit the application if Exodus is not installed

    main() # Start the MultiExodus application