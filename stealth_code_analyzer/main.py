import os
import sys
from core.ast_parser import CodeParser

def scan_directory(path, language):
    parser = CodeParser(language)
    all_vulnerabilities = []
    
    for root, _, files in os.walk(path):
        for file in files:
            if language == 'python' and file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"[*] Scanning {file_path}...")
                vulns = parser.parse_file(file_path)
                all_vulnerabilities.extend(vulns)
    
    return all_vulnerabilities

def print_report(vulnerabilities):
    if not vulnerabilities:
        print("\n[+] No vulnerabilities found. Stealth mode maintained.")
        return

    print("\n" + "="*40)
    print("      GAHENAX SAST VULNERABILITY REPORT")
    print("="*40)
    for vuln in vulnerabilities:
        print(f"\n[!] Type: {vuln['type']}")
        print(f"    File: {vuln['file']}")
        print(f"    Line: {vuln['line']}")
        print(f"    Sink: {vuln['sink']}")
        print(f"    Details: {vuln['details']}")
    print("\n" + "="*40)
    print(f"Total vulnerabilities found: {len(vulnerabilities)}")
    print("="*40)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <path_to_code> <language>")
        sys.exit(1)
        
    code_path = sys.argv[1]
    lang = sys.argv[2].lower()
    
    if not os.path.isdir(code_path):
        print(f"[-] Error: Directory '{code_path}' not found.")
        sys.exit(1)
        
    print(f" Starting Stealth SAST Analysis on: {code_path} ({lang})")
    findings = scan_directory(code_path, lang)
    print_report(findings)
