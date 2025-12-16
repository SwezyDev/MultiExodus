from win10toast import ToastNotifier # import the ToastNotifier class from the win10toast library
from .constants import APP_ICON # import the application icon path constant

def show_toast(title: str, message: str, icon: str = APP_ICON, duration: int = 3) -> None: # function to show a Windows toast notification
    toaster = ToastNotifier() # create an instance of ToastNotifier
    toaster.show_toast(title, message, icon, duration, True) # show the toast in a non-blocking way