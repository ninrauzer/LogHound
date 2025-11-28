"""
reporter.py
-----------
Generates the final report with the log analysis summary.
Creates a text file with statistics, detected patterns, and anomalies.
"""

import datetime
import os
from colorama import Fore, Style
from eft_codes import ALL_CODES


class LogReporter:
    """Log analysis report generator."""
    
    def __init__(self, config, resultados):
        """
        Initialize the report generator.
        
        Args:
            config: Dictionary with configuration settings
            resultados: Dictionary with scan results
        """
        # Generate timestamped report filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = config.get("report_dir", r"C:\BrainStein\LogHound\reports")
        self.reporte_path = os.path.join(report_dir, f"LogHound_{timestamp}.txt")
        
        self.base_path = config["base_path"]
        
        # Handle search_string as either string or array
        search_config = config.get("search_string", "")
        if isinstance(search_config, list):
            self.search_patterns = [s for s in search_config if s]
        elif search_config:
            self.search_patterns = [search_config]
        else:
            self.search_patterns = []
        
        self.ip_threshold = config.get("ip_suspicious_threshold", 50)
        self.resultados = resultados
        
        # Create report directory if it doesn't exist
        os.makedirs(report_dir, exist_ok=True)
    
    def generate_report(self):
        """Generate the complete report and save it to file."""
        try:
            with open(self.reporte_path, "w", encoding="utf-8") as r:
                self._escribir_encabezado(r)
                self._escribir_errores(r)
                self._escribir_warnings(r)
                self._escribir_info(r)
                self._escribir_ips(r)
                self._escribir_archivos(r)
                self._escribir_patrones(r)
                
                if self.search_patterns:
                    self._escribir_busqueda(r)
                
                r.write("\n=== END OF REPORT ===\n")
            
            print(f"\n{Fore.GREEN}[OK] Report generated successfully:{Style.RESET_ALL}")
            print(f"  Report: {self.reporte_path}\n")
        
        except Exception as e:
            print(f"\n{Fore.RED}[ERROR] Error generating report: {e}{Style.RESET_ALL}\n")
    
    def _escribir_encabezado(self, r):
        """Write the report header."""
        r.write("=" * 60 + "\n")
        r.write("    [LOGHOUND] - ANALYSIS SUMMARY\n")
        r.write("=" * 60 + "\n\n")
        r.write(f"Analysis date: {datetime.datetime.now()}\n")
        r.write(f"Scanned directory: {self.base_path}\n")
        if self.search_patterns:
            r.write(f"Search patterns: {self.search_patterns}\n")
        r.write("\n")
    
    def _escribir_errores(self, r):
        """Write the errors section."""
        r.write("=" * 60 + "\n")
        r.write("[ERROR] ERRORS\n")
        r.write("=" * 60 + "\n")
        error_counts = self.resultados["error_counts"]
        
        if error_counts:
            for code, cnt in error_counts.most_common():
                r.write(f"  {code} - {ALL_CODES.get(code, 'Unknown')} → {cnt} occurrences\n")
        else:
            r.write("  [OK] No errors detected.\n")
        r.write("\n")
    
    def _escribir_warnings(self, r):
        """Write the warnings section."""
        r.write("=" * 60 + "\n")
        r.write("[WARNING] WARNINGS\n")
        r.write("=" * 60 + "\n")
        warning_counts = self.resultados["warning_counts"]
        
        if warning_counts:
            for code, cnt in warning_counts.most_common():
                r.write(f"  {code} - {ALL_CODES.get(code, 'Unknown')} → {cnt} occurrences\n")
        else:
            r.write("  [OK] No warnings detected.\n")
        r.write("\n")
    
    def _escribir_info(self, r):
        """Write the information section."""
        r.write("=" * 60 + "\n")
        r.write("[INFO] INFORMATION\n")
        r.write("=" * 60 + "\n")
        info_counts = self.resultados["info_counts"]
        
        if info_counts:
            for code, cnt in info_counts.most_common():
                r.write(f"  {code} - {ALL_CODES.get(code, 'Unknown')} → {cnt} occurrences\n")
        else:
            r.write("  No informational events recorded.\n")
        r.write("\n")
    
    def _escribir_ips(self, r):
        """Write the section of IPs with most activity."""
        r.write("=" * 60 + "\n")
        r.write("[NETWORK] IPs WITH MOST ACTIVITY (Top 10)\n")
        r.write("=" * 60 + "\n")
        ips = self.resultados["ips_frecuentes"]
        
        for ip, cnt in ips.most_common(10):
            r.write(f"  {ip} → {cnt} events\n")
        r.write("\n")
    
    def _escribir_archivos(self, r):
        """Write the section of most transferred files."""
        r.write("=" * 60 + "\n")
        r.write("[FILES] MOST TRANSFERRED FILES (Top 10)\n")
        r.write("=" * 60 + "\n")
        archivos = self.resultados["archivos_con_muchos_eventos"]
        
        for arch, cnt in archivos.most_common(10):
            r.write(f"  {arch} → {cnt} actions\n")
        r.write("\n")
    
    def _escribir_patrones(self, r):
        """Write the detected patterns section."""
        r.write("=" * 60 + "\n")
        r.write("[PATTERNS] DETECTED PATTERNS\n")
        r.write("=" * 60 + "\n")
        
        ips = self.resultados["ips_frecuentes"]
        sospechosas = [ip for ip, c in ips.items() if c > self.ip_threshold]
        
        if sospechosas:
            r.write(f"[ALERT] Suspicious IPs due to abnormal activity (>{self.ip_threshold} events):\n")
            for ip in sospechosas:
                r.write(f"  • {ip} ({ips[ip]} events)\n")
        else:
            r.write("  [OK] No suspicious IPs detected.\n")
        r.write("\n")
    
    def _escribir_busqueda(self, r):
        """Write the custom search results grouped by error code."""
        r.write("=" * 60 + "\n")
        r.write(f"[SEARCH] SEARCH: {self.search_patterns}\n")
        r.write("=" * 60 + "\n")
        
        search_results = self.resultados["search_results"]
        
        if search_results:
            # Group results by error code
            results_with_errors = []
            results_with_warnings = []
            results_success = []
            
            for item in search_results:
                # Handle new format (5 items: path, idx, line, pattern, code)
                if len(item) == 5:
                    full_path, idx, linea, matched_pattern, codigo = item
                elif len(item) == 4:
                    # Fallback for old format
                    full_path, idx, linea, matched_pattern = item
                    codigo = None
                else:
                    continue
                
                # Classification logic for CL logs:
                # - codigo = None or 0 → Success
                # - codigo = 331 → Warning (needs password)
                # - Any other code → Error
                if codigo:
                    if codigo == 331:  # Warning: User needs password
                        results_with_warnings.append((full_path, idx, linea, matched_pattern, codigo))
                    else:  # Any non-zero code is an error
                        results_with_errors.append((full_path, idx, linea, matched_pattern, codigo))
                else:
                    # codigo = None means code was 0 (success)
                    results_success.append((full_path, idx, linea, matched_pattern, None))
            
            total = len(results_with_errors) + len(results_with_warnings) + len(results_success)
            r.write(f"  Total matches: {total}\n")
            r.write(f"    • With ERRORS: {len(results_with_errors)}\n")
            r.write(f"    • With WARNINGS: {len(results_with_warnings)}\n")
            r.write(f"    • Successful: {len(results_success)}\n\n")
            
            # Write ERRORS section
            if results_with_errors:
                r.write("  " + "-" * 56 + "\n")
                r.write("  [ERROR] LINES WITH ERRORS:\n")
                r.write("  " + "-" * 56 + "\n")
                for full_path, idx, linea, matched_pattern, codigo in results_with_errors:
                    code_desc = ALL_CODES.get(codigo, 'Unknown') if codigo else ''
                    r.write(f"\n  [{matched_pattern}] {full_path}:{idx}\n")
                    r.write(f"    CODE {codigo}: {code_desc}\n")
                    r.write(f"    → {linea}\n")
                r.write("\n")
            
            # Write WARNINGS section
            if results_with_warnings:
                r.write("  " + "-" * 56 + "\n")
                r.write("  [WARNING] LINES WITH WARNINGS:\n")
                r.write("  " + "-" * 56 + "\n")
                for full_path, idx, linea, matched_pattern, codigo in results_with_warnings:
                    code_desc = ALL_CODES.get(codigo, 'Unknown') if codigo else ''
                    r.write(f"\n  [{matched_pattern}] {full_path}:{idx}\n")
                    r.write(f"    CODE {codigo}: {code_desc}\n")
                    r.write(f"    → {linea}\n")
                r.write("\n")
            
            # Write SUCCESS section (limit to 20 examples)
            if results_success:
                r.write("  " + "-" * 56 + "\n")
                r.write("  [SUCCESS] LINES WITHOUT ERRORS (showing first 20):\n")
                r.write("  " + "-" * 56 + "\n")
                for full_path, idx, linea, matched_pattern, codigo in results_success[:20]:
                    code_desc = ALL_CODES.get(codigo, 'Unknown') if codigo else 'No code'
                    r.write(f"\n  [{matched_pattern}] {full_path}:{idx}\n")
                    if codigo:
                        r.write(f"    CODE {codigo}: {code_desc}\n")
                    r.write(f"    → {linea}\n")
                
                if len(results_success) > 20:
                    r.write(f"\n  ... and {len(results_success) - 20} more successful operations.\n")
                r.write("\n")
        else:
            r.write(f"  No matches found.\n")
        r.write("\n")
