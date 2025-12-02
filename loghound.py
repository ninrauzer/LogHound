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
            
            response = input(f"\n⚠️  Proceed with download? (Y/N): ").strip().upper()
            if response != 'Y':
                print(f"\n[INFO] Download cancelled. Using existing logs.\n")
            else:
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
       
        # Ask for time range
        print("Select time range for analysis:")
        print("  0) Todos los logs (sin filtro)")
        print("  1) Hoy (today)")
        print("  2) Ayer (yesterday)")
        print("  3) Última hora (last 1h)")
        print("  4) Últimas 12 horas (last 12h)")
        print("  5) Personalizado (custom)")
        choice = input("Enter option [0-5]: ").strip()
        import datetime
        tz_utc = datetime.timezone.utc
        tz_offset = datetime.timedelta(hours=-5)
        now_utc = datetime.datetime.now(tz_utc)
        now_local = now_utc + tz_offset
        now_local = now_local.replace(tzinfo=None)
        start_local = None
        end_local = None
        if choice == '1':
            start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
            end_local = now_local
        elif choice == '2':
            yesterday = now_local - datetime.timedelta(days=1)
            start_local = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_local = start_local + datetime.timedelta(days=1)
        elif choice == '3':
            start_local = now_local - datetime.timedelta(hours=1)
            end_local = now_local
        elif choice == '4':
            start_local = now_local - datetime.timedelta(hours=12)
            end_local = now_local
        elif choice == '5':
            s = input("Start (YYYY-MM-DD HH:MM:SS, local): ").strip()
            e = input("End   (YYYY-MM-DD HH:MM:SS, local): ").strip()
            try:
                start_local = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
                end_local = datetime.datetime.strptime(e, "%Y-%m-%d %H:%M:%S")
            except Exception:
                print("[ERROR] Invalid date format. Aborting.")
                return 1
        elif choice == '0':
            # No filter: analyze all logs
            start_local = None
            end_local = None
        else:
            print("[ERROR] Invalid option. Aborting.")
            return 1

        # Pass range (in local time) to scanner
        scanner = LogScanner(config, start_local, end_local, tz_offset)
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
