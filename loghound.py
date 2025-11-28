"""
loghound.py
-----------
Main LogHound executable.
EFT/SFTP log analyzer that detects errors, warnings, and abnormal patterns.

Usage:
    python loghound.py
    
Configuration:
    Edit config.json to customize paths, extensions, and searches.
"""

import sys
import os
from colorama import init
from banner import show_banner
from config_loader import load_config
from scanner import LogScanner
from reporter import LogReporter
from log_downloader import LogDownloader

# Initialize colorama for Windows
init()


def main():
    """Main program function."""
    try:
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Show banner
        show_banner()
        
        # Load configuration
        config = load_config("config.json")
        
        # Download fresh logs if enabled
        if config.get('refresh_logs', False):
            print(f"\n{'='*60}")
            print(f"⚠️  LOG REFRESH ENABLED")
            print(f"{'='*60}")
            print(f"LogHound will download fresh logs from the EFT server.")
            print(f"This process may take several minutes.")
            input(f"\nPress ENTER to continue...")

            
            downloader = LogDownloader(config)
            downloader.download_fresh_logs()
        
        # Display active configuration
        print(f"Configuration:")
        print(f"  • Base path: {config['base_path']}")
        print(f"  • Extensions: {', '.join(config['extensions'])}")
        print(f"  • Verbose mode: {config['verbose']}")
        if config.get('search_string'):
            print(f"  • Search: '{config['search_string']}'")
        print()
       
        # Scan logs
        scanner = LogScanner(config)
        scanner.scan()
        
        # Get results
        results = scanner.get_results()
        
        # Generate report
        reporter = LogReporter(config, results)
        reporter.generate_report()
        
        print("[OK] Analysis completed successfully.\n")
        return 0
    
    except KeyboardInterrupt:
        print("\n\n[WARNING] Operation cancelled by user.\n")
        return 1
    
    except Exception as e:
        print(f"\n[ERROR] Critical error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
