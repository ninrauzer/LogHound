"""
parser.py
---------
Interprets log lines and extracts relevant information.
Detects EFT codes, dates, IPs, and file paths.
Supports multiple log formats: CL (CSV), EX (W3C), TED6.
"""

import re
import datetime


class LogParser:
    """Parser for analyzing EFT/SFTP log lines."""
    
    def __init__(self):
        # EX log pattern: Detects 3, 4, or 5 digit codes (FTP, HTTP, Winsock)
        # Uses negative lookbehind/lookahead to avoid dates and IPs
        self.code_pattern_ex = re.compile(r'(?<![:\d.\-])\b(\d{3,5})\b(?![:\d.\-])')
        
        # CL log pattern: CSV format ending with "; code;"
        self.code_pattern_cl = re.compile(r';\s*(\d+)\s*;?\s*$')
        
        self.date_pattern = re.compile(r"\b(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
        self.ip_pattern = re.compile(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b")
        self.path_pattern = re.compile(r"/[\w\-/\.\+]+")
    
    def extract_code(self, linea):
        """
        Extracts code from log line using format-specific logic.
        
        CL logs (CSV): "Time; Protocol; Host; Port; User; LocalPath; RemotePath; Operation; RESULT_CODE;"
                       RESULT_CODE = 0 (success), FTP codes (200-599), or Winsock errors (10000+)
        EX logs (W3C): "Time IP User [Session]Action Result ... FTP_CODE"
        TED6 logs: Mixed format (client commands and responses)
        
        Args:
            linea: Log line to analyze
        
        Returns:
            int or None: Found code or None
        """
        # Detect CL format (CSV with semicolons)
        if ';' in linea:
            # Split by semicolon and get fields
            fields = linea.split(';')
            
            # CL logs: field 8 = RESULT_CODE (0=success, or error code)
            if len(fields) >= 9:
                try:
                    code = int(fields[8].strip())
                    # 0 = success, no error to report
                    if code == 0:
                        return None
                    # Valid error codes: FTP (200-599) or Winsock (10000+)
                    if (200 <= code <= 599) or (code >= 10000):
                        return code
                except (ValueError, IndexError):
                    pass
        
        # EX/TED6 format: space-separated, use regex pattern
        matches = self.code_pattern_ex.findall(linea)
        for match in matches:
            code = int(match)
            # Filter out session IDs (usually 5-6 digits)
            if code < 100000:
                return code
        
        return None
    
    def format_date(self, linea):
        """
        Extract and format the date from a line.
        
        Args:
            linea: Log line to analyze
        
        Returns:
            str: Formatted date or placeholder
        """
        match = self.date_pattern.search(linea)
        if not match:
            return "????-??-?? ??:??:??"
        try:
            dt = datetime.datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return match.group(1)
    
    def extract_ip(self, linea):
        """
        Extract the IP address from a line.
        
        Args:
            linea: Log line to analyze
        
        Returns:
            str or None: Found IP or None
        """
        match = self.ip_pattern.search(linea)
        return match.group(1) if match else None
    
    def extract_path(self, linea):
        """
        Extract file paths from a line.
        
        Args:
            linea: Log line to analyze
        
        Returns:
            str or None: Found path or None
        """
        match = self.path_pattern.search(linea)
        return match.group(0) if match else None
    
    def search_string(self, linea, search_string):
        """
        Search for a specific string in the line (case-insensitive).
        
        Args:
            linea: Log line to analyze
            search_string: String to search for
        
        Returns:
            bool: True if string is found
        """
        if not search_string:
            return False
        return search_string.lower() in linea.lower()
