from datetime import datetime


def now_str(milliseconds: bool = False) -> str:
    """
    Returns current local time as string.

    Args:
        milliseconds (bool): If True, include milliseconds.

    Returns:
        str: formatted as "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DD HH:MM:SS.mmm"
    """
    now = datetime.now()
    if milliseconds:
        # include milliseconds
        return now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # take only first 3 digits of microseconds
    else:
        # without milliseconds
        return now.strftime("%Y-%m-%d %H:%M:%S")
