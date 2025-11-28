"""
log_downloader.py
-----------------
Downloads fresh EFT logs from remote server via SFTP.
Cleans up old local logs based on retention policy.
"""

import paramiko
from datetime import datetime, timedelta
import time
import os
from colorama import Fore, Style
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LogDownloader:
    """Handles downloading logs from EFT server and cleanup."""
    
    def __init__(self, config):
        """Initialize downloader with configuration."""
        self.host = os.getenv("EFT_HOST", "eft-na.wtwco.com")
        self.port = int(os.getenv("EFT_PORT", "22"))
        self.username = os.getenv("EFT_USER")
        self.password = os.getenv("EFT_PASS")
        
        self.remote_base = "/Logs"
        self.folders = ["vmswtwna1000004", "vmswtwna1000005"]
        self.local_base = config.get('base_path', r"C:\LogOps")
        
        # Get retention days from config, fallback to env var, default to 2
        self.days = config.get('log_retention_days', int(os.getenv("EFT_DAYS", "2")))
        self.fresh_minutes = 3
        self.max_retries = 3
        self.retry_delay = 2
        
        # File filters
        self.filters = [
            lambda name: name.startswith("c") and name.endswith(".log"),
            lambda name: name.startswith("u_ex") and name.endswith(".log"),
        ]
    
    def matches_filters(self, fname: str) -> bool:
        """Check if filename matches any filter."""
        return any(f(fname) for f in self.filters)
    
    def connect_sftp(self):
        """Create SFTP client connection."""
        if not self.username or not self.password:
            raise ValueError(
                "EFT credentials not found. Set EFT_USER and EFT_PASS in .env file."
            )
        
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(username=self.username, password=self.password)
        return paramiko.SFTPClient.from_transport(transport)
    
    def is_recent(self, mtime: datetime) -> bool:
        """Detect files too new (likely write-locked)."""
        return (datetime.now() - mtime) < timedelta(minutes=self.fresh_minutes)
    
    def safe_download(self, sftp, remote_file, local_file):
        """Download file with retry logic."""
        for attempt in range(1, self.max_retries + 1):
            try:
                sftp.get(remote_file, local_file)
                return True
            
            except FileNotFoundError:
                return False
            
            except Exception:
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    return False
        
        return False
    
    def cleanup_old_logs(self):
        """Remove local log files older than retention period."""
        print(f"\n{Fore.CYAN}🧹 Cleaning up logs older than {self.days} days...{Style.RESET_ALL}")
        cutoff = datetime.now() - timedelta(days=self.days)
        total_deleted = 0
        
        for folder in self.folders:
            local_path = os.path.join(self.local_base, folder)
            
            if not os.path.exists(local_path):
                continue
            
            for fname in os.listdir(local_path):
                if not self.matches_filters(fname):
                    continue
                
                file_path = os.path.join(local_path, fname)
                
                try:
                    # Extract date from filename (e.g., cl251127.log -> 2025-11-27)
                    # Format: cl[YY][MM][DD].log or u_ex[YY][MM][DD].log
                    date_part = None
                    if fname.startswith("cl") and len(fname) >= 10:
                        date_part = fname[2:8]  # Extract YYMMDD
                    elif fname.startswith("u_ex") and len(fname) >= 14:
                        date_part = fname[4:10]  # Extract YYMMDD
                    
                    if date_part and len(date_part) == 6:
                        # Parse YYMMDD format
                        file_date = datetime.strptime(date_part, "%y%m%d")
                        
                        if file_date < cutoff:
                            os.remove(file_path)
                            print(f"  {Fore.RED}🗑️{Style.RESET_ALL}  Deleted: {fname} (date: {file_date.strftime('%Y-%m-%d')})")
                            total_deleted += 1
                
                except Exception as e:
                    print(f"  {Fore.YELLOW}⚠️{Style.RESET_ALL}  Error deleting {fname}: {e}")
        
        print(f"{Fore.GREEN}✅ Cleanup complete: {total_deleted} file(s) removed.{Style.RESET_ALL}\n")
    
    def download_fresh_logs(self):
        """Download fresh logs from EFT server."""
        # Cleanup old logs first
        self.cleanup_old_logs()
        
        cutoff = datetime.now() - timedelta(days=self.days)
        total_downloaded = 0
        total_files = 0
        
        try:
            sftp = self.connect_sftp()
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Failed to connect to EFT server: {e}{Style.RESET_ALL}")
            return
        
        for folder in self.folders:
            remote_path = f"{self.remote_base}/{folder}"
            local_path = os.path.join(self.local_base, folder)
            os.makedirs(local_path, exist_ok=True)
            
            print(f"\n{Fore.CYAN}📂 Processing folder: {folder}{Style.RESET_ALL}")
            
            try:
                files = sftp.listdir_attr(remote_path)
            except Exception as e:
                print(f"  {Fore.RED}❌{Style.RESET_ALL} Cannot read {remote_path}: {e}")
                continue
            
            # Count eligible files for progress
            eligible_files = []
            for f in files:
                if self.matches_filters(f.filename):
                    mtime = datetime.fromtimestamp(f.st_mtime)
                    if mtime >= cutoff and not self.is_recent(mtime):
                        eligible_files.append(f)
            
            if not eligible_files:
                print(f"  {Fore.YELLOW}ℹ️{Style.RESET_ALL}  No new logs to download in this folder.")
                continue
            
            print(f"  {Fore.CYAN}Found {len(eligible_files)} file(s) to download...{Style.RESET_ALL}")
            total_files += len(eligible_files)
            
            for idx, f in enumerate(eligible_files, 1):
                fname = f.filename
                mtime = datetime.fromtimestamp(f.st_mtime)
                
                remote_file = f"{remote_path}/{fname}"
                local_file = os.path.join(local_path, fname)
                
                print(f"  [{idx}/{len(eligible_files)}] {Fore.GREEN}📥{Style.RESET_ALL} {fname} ({mtime.strftime('%Y-%m-%d %H:%M')})", end="")
                if self.safe_download(sftp, remote_file, local_file):
                    print(f" {Fore.GREEN}✓{Style.RESET_ALL}")
                    total_downloaded += 1
                else:
                    print()
        
        sftp.close()
        print(f"\n{Fore.GREEN}✅ Download complete: {total_downloaded} file(s) downloaded.{Style.RESET_ALL}\n")
