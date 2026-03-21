import re
from utils.code_patterns import get_vulnerability_patterns

def analyze_static_code(code, language):
    """Main function to analyze code for vulnerabilities"""
    lines = code.split('\n')
    vulnerabilities = []
    
    # Get patterns for the specified language
    patterns = get_vulnerability_patterns(language)
    
    for line_num, line in enumerate(lines, 1):
        line_vulns = check_line_for_vulnerabilities(line, line_num, patterns)
        vulnerabilities.extend(line_vulns)
    
    return vulnerabilities

def check_line_for_vulnerabilities(line, line_num, patterns):
    """Check a single line for various vulnerabilities"""
    vulnerabilities = []
    
    for pattern in patterns:
        try:
            if pattern['pattern'].search(line):
                vulnerabilities.append({
                    'line': line_num,
                    'mistake': pattern['mistake'],
                    'explanation': pattern['explanation'],
                    'solution': pattern['solution'],
                    'example': pattern['example']
                })
        except Exception as e:
            print(f"Error checking pattern: {e}")
            continue
    
    return vulnerabilities

def extract_context(code, line_num, context_lines=2):
    """Extract context around a line for better reporting"""
    lines = code.split('\n')
    start = max(0, line_num - context_lines - 1)
    end = min(len(lines), line_num + context_lines)
    context = lines[start:end]
    return context