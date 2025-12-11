from .constants import CLIENT_ID, GITHUB_REPO # import constants
import pypresence # for discord rpc
import asyncio # for async operations
import time # for time operations

RPC = None # global rpc client
start_time = int(time.time()) # rpc start time

def start_rpc(intx): # function to start the rpc client
    global RPC # use the global rpc variable

    loop = asyncio.new_event_loop() # create a new asyncio event loop
    asyncio.set_event_loop(loop) # set the new event loop as the current one

    RPC = pypresence.Presence(CLIENT_ID) # create rpc client
    for i in range(5): # try to connect to rpc server with retries
        try: # attempt to connect
            RPC.connect() # connect to rpc server
            break # exit loop on success
        except Exception as e: # on connection failure
            time.sleep(2) # wait before retrying
    else: # if all retries fail
        return # exit function

    RPC.update( # update rpc presence
        details=f"Managing {intx} Exodus Wallet{'s' if intx != 1 else ''}",
        large_image="multiexodus-logo",
        large_text="MultiExodus - Manage Multiple Exodus Wallets",
        small_image="github-logo",
        small_text="Free and Open Source on GitHub",
        start=start_time,
        buttons=[{"label": "Download MultiExodus", "url": f"https://github.com/{GITHUB_REPO}"}, 
                 {"label": "Download Exodus", "url": "https://www.exodus.com/download/"}
                ]
    )

def stop_rpc(): # function to stop the rpc client
    global RPC # use the global rpc variable
    if RPC is not None: # if rpc client exists
        try: # attempt to clear and close rpc client
            RPC.clear() # clear rpc presence
            RPC.close() # close rpc connection
            RPC = None # reset rpc variable
        except Exception as e: # on failure
            pass # ignore errors

def restart_rpc(intx): # function to restart the rpc client
    stop_rpc() # stop the rpc client
    time.sleep(1) # wait before restarting
    start_rpc(intx) # start the rpc client with new intx

