"""
banner.py
---------
Module to display LogHound presentation banner.
Contains the function to print the title with Figlet and program information.
"""

from colorama import Fore, Style
from pyfiglet import figlet_format


def show_banner():
    """Display LogHound's main banner with formatting and colors."""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[LOGHOUND]{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{figlet_format('LOGHOUND', font='slant')}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] EFT/SFTP Log Analyzer{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  [OK] Detects errors and warnings{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  [*] Identifies suspicious IPs{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  [*] Generates detailed reports{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  [*] Crafted by: Renan Ruiz{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  [*] Pretending to control the chaos{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    input(f"\nPress ENTER to continue...")