# 🐕 LogHound - EFT/SFTP Log Analyzer

Professional log analyzer that detects errors, warnings, suspicious IPs, and generates detailed reports.

## ✨ Features

- ✅ Automatic EFT error code detection
- 📥 **Download fresh logs from EFT server** (optional)
- 🧹 **Automatic cleanup of old logs** based on retention policy
- 📊 IP activity analysis and suspicious IP detection
- 🔍 Custom text search with pattern matching
- 📁 Most transferred files tracking
- 📝 Detailed timestamped reports

## 🚀 Quick Start

### 1. Setup Credentials (Optional - for log refresh)

If you want to download fresh logs from the EFT server:

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
EFT_USER=your_username
EFT_PASS=your_password
EFT_DAYS=2
```

### 2. Configure

Edit `config.json`:

```json
{
  "base_path": "C:\\LogOps",              // Local log directory
  "extensions": [".log", ".txt"],         // File extensions to scan
  "log_types": ["CL"],                    // CL, EX, or ALL
  "report_dir": "C:\\BrainStein\\LogHound\\reports",
  "verbose": "ERROR",                      // ERROR | WARNING | ALL
  "search_string": ["pattern1"],          // Search patterns (optional)
  "ip_suspicious_threshold": 50,          // Suspicious IP threshold
  "refresh_logs": true                    // Download fresh logs before analysis
}
```

### 3. Run

```powershell
cd C:\BrainStein\LogHound
python loghound.py
```

## 📥 Log Refresh Feature

When `"refresh_logs": true` in config.json:

1. **Downloads** fresh logs from EFT server (last N days)
2. **Cleans up** local logs older than retention period
3. **Analyzes** the refreshed logs
4. **Generates** timestamped report

**Environment Variables:**
- `EFT_HOST` - EFT server hostname (default: eft-na.wtwco.com)
- `EFT_PORT` - SFTP port (default: 22)
- `EFT_USER` - SFTP username (required)
- `EFT_PASS` - SFTP password (required)
- `EFT_DAYS` - Days to retain/download (default: 2)

## 📁 Project Structure

```
LogHound/
├─ loghound.py          → Main executable
├─ config.json          → Configuration file
├─ log_downloader.py    → SFTP log downloader
├─ scanner.py           → Log scanner
├─ parser.py            → Log parser
├─ reporter.py          → Report generator
├─ eft_codes.py         → EFT code definitions
├─ banner.py            → Banner display
├─ .env.example         → Credentials template
└─ README.md            → This file
```

## ⚙️ Verbosity Options

- **ERROR**: Only critical errors (code != 0, except 331)
- **WARNING**: Errors + warnings (code 331)
- **ALL**: All events (errors, warnings, success)

## 🔍 Custom Search

Search for specific patterns in logs using `search_string`:

```json
{
  "search_string": ["fiserv", "client_name"]
}
```

Results are grouped by ERROR/WARNING/SUCCESS in the report.

## 📊 Detected EFT Codes

**CL Logs (CSV format):**
- **0**: Success (not shown in ERROR mode)
- **331**: Warning - User needs password
- **Any other code**: ERROR

**FTP Codes:**
- **200-226**: Success
- **331**: Warning - Password required
- **421-426**: Connection errors
- **500-553**: Syntax and permission errors
- **530**: Authentication failed
- **550**: File unavailable

**Winsock Codes:**
- **10054**: Connection reset by peer
- **10060**: Connection timeout
- **10061**: Connection refused

## 🐛 Troubleshooting

**Import errors:**
```powershell
cd C:\BrainStein\LogHound
python loghound.py
```

**Missing credentials (refresh_logs=true):**
```
[ERROR] Failed to connect to EFT server: EFT credentials not found.
```
→ Create `.env` file with `EFT_USER` and `EFT_PASS`

**SFTP connection failed:**
- Verify credentials in `.env`
- Check firewall/VPN connection
- Verify EFT server hostname

## 📦 Dependencies

```bash
pip install paramiko python-dotenv colorama
```

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## 📄 License

MIT License - Feel free to use and modify.
