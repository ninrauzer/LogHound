import paramiko
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv
import os

load_dotenv()

# =============================================
# CONFIG (EDIT THESE)
# =============================================
HOST = "eft-na.wtwco.com"
PORT = 22

#USERNAME = "Renan3695_adm"      # Will be replaced at runtime or via env vars
#PASSWORD = "U9IH8Jmk"      # Same as above

USERNAME = os.getenv("EFT_USER")
PASSWORD = os.getenv("EFT_PASS")


REMOTE_BASE = "/Logs"
FOLDERS = ["vmswtwna1000004", "vmswtwna1000005"]

LOCAL_BASE = r"C:\LogOps"            # GitHub-safe path

DAYS = 2                 # How many days back to download
FRESH_MINUTES = 3        # Skip logs being currently written
MAX_RETRIES = 3          # Retry attempts when downloading a file
RETRY_DELAY = 2          # Seconds between retries


# filters for log files
FILTERS = [
    lambda name: name.startswith("c") and name.endswith(".log"),
    lambda name: name.startswith("u_ex") and name.endswith(".log"),
    # lambda name: name.startswith("[") and name.endswith("-#0.log"),
]


# =============================================
# HELPERS
# =============================================
def log(msg):
    print(msg)

def matches_filters(fname: str) -> bool:
    return any(f(fname) for f in FILTERS)

def connect_sftp():
    """Create SFTP client connection via paramiko."""
    transport = paramiko.Transport((HOST, PORT))
    transport.connect(username=USERNAME, password=PASSWORD)
    return paramiko.SFTPClient.from_transport(transport)

def is_recent(mtime: datetime) -> bool:
    """Detect files too new (likely write-locked by EFT)."""
    return (datetime.now() - mtime) < timedelta(minutes=FRESH_MINUTES)


# =============================================
# CLEANUP OLD LOGS
# =============================================
def cleanup_old_logs(days_to_keep):
    """Remove local log files older than specified days."""
    log(f"\n🧹 Cleaning up logs older than {days_to_keep} days...")
    cutoff = datetime.now() - timedelta(days=days_to_keep)
    total_deleted = 0
    
    for folder in FOLDERS:
        local_path = os.path.join(LOCAL_BASE, folder)
        
        if not os.path.exists(local_path):
            continue
        
        for fname in os.listdir(local_path):
            if not matches_filters(fname):
                continue
            
            file_path = os.path.join(local_path, fname)
            
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if mtime < cutoff:
                    os.remove(file_path)
                    log(f"  🗑️  Deleted: {fname} (modified: {mtime.strftime('%Y-%m-%d')})")
                    total_deleted += 1
            
            except Exception as e:
                log(f"  ⚠️  Error deleting {fname}: {e}")
    
    log(f"✅ Cleanup complete: {total_deleted} file(s) removed.\n")


# =============================================
# SAFE DOWNLOAD
# =============================================
def safe_download(sftp, remote_file, local_file):
    """Download a file with retry logic and graceful error handling."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            sftp.get(remote_file, local_file)
            return True

        except FileNotFoundError:
            log(f"   ⚠ Skipping {os.path.basename(remote_file)} (locked or rotated).")
            return False

        except Exception as e:
            log(f"   ⚠ Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            time.sleep(RETRY_DELAY)

    log(f"   ❌ Permanent failure: {os.path.basename(remote_file)}")
    return False


# =============================================
# MAIN PROCESS
# =============================================
def download_logs():
    log(f"\n=== EFT Log Downloader (last {DAYS} days) ===")
    
    # Clean up old logs before downloading
    cleanup_old_logs(DAYS)
    
    cutoff = datetime.now() - timedelta(days=DAYS)

    sftp = connect_sftp()

    for folder in FOLDERS:
        remote_path = f"{REMOTE_BASE}/{folder}"
        local_path = os.path.join(LOCAL_BASE, folder)
        os.makedirs(local_path, exist_ok=True)

        log(f"\nProcessing folder: {folder}")

        try:
            files = sftp.listdir_attr(remote_path)
        except Exception as e:
            log(f"  ❌ Cannot read {remote_path}: {e}")
            continue

        for f in files:
            fname = f.filename

            if not matches_filters(fname):
                continue

            mtime = datetime.fromtimestamp(f.st_mtime)

            if mtime < cutoff:
                continue

            if is_recent(mtime):
                log(f"   ⏳ {fname} is being written (too recent). Skipped.")
                continue

            remote_file = f"{remote_path}/{fname}"
            local_file = os.path.join(local_path, fname)

            log(f"  📥 {fname} (mtime: {mtime})")
            safe_download(sftp, remote_file, local_file)

    sftp.close()
    log("\n=== DONE ===")


if __name__ == "__main__":
    download_logs()
