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
    
    # ASCII Dog Art and Figlet side by side
    dog_art = [
        "      / \\__",
        "     (    @\\___",
        "     /         O",
        "   /   (_____/",
        "  /_____/   U"
    ]
    
    figlet_lines = figlet_format('LOGHOUND', font='slant').split('\n')
    
    # Print dog and figlet side by side
    max_lines = max(len(dog_art), len(figlet_lines))
    for i in range(max_lines):
        dog_line = dog_art[i] if i < len(dog_art) else ""
        figlet_line = figlet_lines[i] if i < len(figlet_lines) else ""
        print(f"{Fore.YELLOW}{dog_line:<20}{Style.RESET_ALL}{Fore.CYAN}{figlet_line}{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}[+] EFT/SFTP Log Analyzer{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  ✅ Detects errors and warnings{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  🔍 Identifies suspicious IPs{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  📊 Generates detailed reports{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  👨‍💻 Crafted by: Renan Ruiz{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  🎯 Pretending to control the chaos{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    response = input(f"\n⏸️  Continue? (Y/N): ").strip().upper()
    if response != 'Y':
        print(f"\n[INFO] Operation cancelled by user.\n")
        exit(0)