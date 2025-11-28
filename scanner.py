"""
scanner.py
----------
Scans directories for log files.
Recursively traverses folders and filters by configured extensions.
"""

import os
from collections import defaultdict, Counter
from colorama import Fore, Style
from parser import LogParser
from eft_codes import EFT_CODES, ALL_CODES


class LogScanner:
    """Log file scanner with event analysis."""
    
    def __init__(self, config):
        """
        Initialize the scanner with the provided configuration.
        
        Args:
            config: Dictionary with configuration settings
        """
        self.base_path = config["base_path"]
        self.extensions = tuple(config["extensions"])
        self.verbose = config["verbose"]
        
        # Configure log type filters
        log_types = config.get("log_types", ["ALL"])
        self.log_patterns = self._build_log_patterns(log_types)
        
        # Handle search_string as either string or array
        search_config = config.get("search_string", "")
        if isinstance(search_config, list):
            self.search_patterns = [s for s in search_config if s]  # Filter empty strings
        elif search_config:
            self.search_patterns = [search_config]
        else:
            self.search_patterns = []
        
        self.parser = LogParser()
        
        # Accumulators
        self.error_counts = Counter()
        self.warning_counts = Counter()
        self.info_counts = Counter()
        self.ips_frecuentes = Counter()
        self.archivos_con_muchos_eventos = Counter()
        self.eventos_por_codigo = defaultdict(list)
        self.search_results = []
    
    def _build_log_patterns(self, log_types):
        """
        Build filename patterns based on selected log types.
        
        Args:
            log_types: List of log types ['ALL'], ['CL', 'EX'], etc.
        
        Returns:
            dict: Patterns for each log type
        """
        patterns = {
            "CL": "cl",      # CL logs: cl[yymmdd].log (outbound transfers)
            "EX": "u_ex",    # EX logs: u_ex[yymmdd].log (inbound transfers)
            "TED6": "_u."    # TED6 logs: [YY.MM.DD_HH.mm]-#_u.log (client connections)
        }
        
        if "ALL" in log_types:
            return patterns
        
        # Return only selected types
        return {k: v for k, v in patterns.items() if k in log_types}
    
    def _matches_log_type(self, filename):
        """
        Check if filename matches configured log type patterns.
        
        Args:
            filename: Name of the log file
        
        Returns:
            bool: True if matches any configured pattern
        """
        if not self.log_patterns:
            return False
        
        filename_lower = filename.lower()
        return any(pattern in filename_lower for pattern in self.log_patterns.values())
    
    def scan(self):
        """
        Scan all log files in base_path.
        Process each line and accumulate statistics.
        """
        print(f"\n{Fore.CYAN}Scanning {self.base_path}...{Style.RESET_ALL}\n")
        
        archivos_procesados = 0
        lineas_procesadas = 0
        
        for root, dirs, files in os.walk(self.base_path):
            for f in files:
                if not f.lower().endswith(self.extensions):
                    continue
                
                # Filter by log type
                if not self._matches_log_type(f):
                    continue
                
                full_path = os.path.join(root, f)
                archivos_procesados += 1
                
                try:
                    # Try UTF-16 LE first (Windows CL logs), fallback to UTF-8
                    encodings = ['utf-16-le', 'utf-8', 'latin-1']
                    fh = None
                    for enc in encodings:
                        try:
                            fh = open(full_path, "r", encoding=enc)
                            # Test read first line to validate encoding
                            fh.readline()
                            fh.seek(0)
                            break
                        except (UnicodeDecodeError, UnicodeError):
                            if fh:
                                fh.close()
                            continue
                    
                    if not fh:
                        fh = open(full_path, "r", errors="ignore")
                    
                    with fh:
                        for idx, line in enumerate(fh, start=1):
                            lineas_procesadas += 1
                            linea = line.strip()
                            
                            # If search patterns are configured, filter lines
                            matched_pattern = None
                            if self.search_patterns:
                                for pattern in self.search_patterns:
                                    if self.parser.search_string(linea, pattern):
                                        matched_pattern = pattern
                                        break
                                
                                if not matched_pattern:
                                    continue  # Skip lines that don't match any pattern
                            
                            # Detect EFT/HTTP/Winsock code
                            codigo = self.parser.extract_code(linea)
                            
                            # Store search result with code
                            if matched_pattern:
                                self.search_results.append((full_path, idx, linea, matched_pattern, codigo))
                            
                            # Display search results with color coding
                            if self.search_patterns:
                                if codigo in ALL_CODES:
                                    if codigo >= 500 or codigo in (530, 550, 426, 421, 11):
                                        codigo_color = f"{Fore.RED}{codigo}{Style.RESET_ALL}"
                                    elif codigo in (331,):
                                        codigo_color = f"{Fore.YELLOW}{codigo}{Style.RESET_ALL}"
                                    else:
                                        codigo_color = f"{Fore.GREEN}{codigo}{Style.RESET_ALL}"
                                    
                                    linea_display = linea[:80].replace(str(codigo), codigo_color)
                                    print(f"{Fore.MAGENTA}[SEARCH: {matched_pattern}] {full_path}:{idx} → {linea_display}...{Style.RESET_ALL}")
                                else:
                                    print(f"{Fore.MAGENTA}[SEARCH: {matched_pattern}] {full_path}:{idx} → {linea[:80]}...{Style.RESET_ALL}")
                            
                            if codigo in ALL_CODES:
                                self._procesar_codigo(codigo, full_path, idx, linea)
                            
                            # Capture IP
                            ip = self.parser.extract_ip(linea)
                            if ip:
                                self.ips_frecuentes[ip] += 1
                            
                            # Capture paths
                            ruta = self.parser.extract_path(linea)
                            if ruta:
                                self.archivos_con_muchos_eventos[ruta] += 1
                
                except Exception as e:
                    print(f"{Fore.RED}[ERROR] Error reading {full_path}: {e}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}[OK] Scan completed:{Style.RESET_ALL}")
        print(f"  • Files processed: {archivos_procesados}")
        print(f"  • Lines analyzed: {lineas_procesadas}")
        if self.search_patterns:
            print(f"  • Search patterns: {len(self.search_patterns)}")
            print(f"  • Search matches: {len(self.search_results)}\n")
    
    def _procesar_codigo(self, codigo, full_path, idx, linea):
        """
        Process a found EFT code and classify it.
        
        Args:
            codigo: Detected EFT code
            full_path: Full file path
            idx: Line number
            linea: Line content
        """
        self.eventos_por_codigo[codigo].append((full_path, idx, linea))
        descripcion = ALL_CODES.get(codigo, "Unknown code")
        fecha = self.parser.format_date(linea)
        
        # Classification logic for CL logs:
        # - codigo = 331 → Warning (needs password)
        # - Any other non-zero code → Error
        if codigo == 331:
            # Warning - Yellow code
            if self.verbose in ("WARNING", "ALL"):
                print(f"[{fecha}] {full_path}:{idx}  {Fore.YELLOW}CODE={codigo}{Style.RESET_ALL} {descripcion}")
            self.warning_counts[codigo] += 1
        
        else:
            # Any non-zero code is an ERROR
            if self.verbose in ("ERROR", "WARNING", "ALL"):
                print(f"[{fecha}] {full_path}:{idx}  {Fore.RED}CODE={codigo}{Style.RESET_ALL} {descripcion}")
            self.error_counts[codigo] += 1
    
    def get_results(self):
        """
        Return all scan results.
        
        Returns:
            dict: Dictionary with all counters and results
        """
        return {
            "error_counts": self.error_counts,
            "warning_counts": self.warning_counts,
            "info_counts": self.info_counts,
            "ips_frecuentes": self.ips_frecuentes,
            "archivos_con_muchos_eventos": self.archivos_con_muchos_eventos,
            "eventos_por_codigo": self.eventos_por_codigo,
            "search_results": self.search_results
        }
