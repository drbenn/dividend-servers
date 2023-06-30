import time

def get_time() -> str:
    """
    Gets the current time and returns it as a string

    Example: '14:57:03 (28/01/23)'
    """
    return time.strftime('%X (%m/%d/%y)')