import getpass
import os

def get_effective_user() -> str:
    """
    Returns the effective user in the format DOMAIN\\username if available,
    otherwise just username.
    """
    username = getpass.getuser()
    domain = os.environ.get('USERDOMAIN')
    
    if domain:
        return f"{domain}\\{username}"
    return username

def print_whoami() -> None:
    """
    Prints the effective user.
    """
    print(get_effective_user())
