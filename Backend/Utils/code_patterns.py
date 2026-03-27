import re

def get_vulnerability_patterns(language):
    """Return vulnerability patterns for the specified language"""
    if language == 'python':
        return get_python_patterns()
    elif language == 'javascript':
        return get_javascript_patterns()
    else:
        return []

def get_python_patterns():
    """Python-specific vulnerability patterns"""
    return [
        # SQL Injection patterns
        {
            'pattern': re.compile(r'input\s*\(.*\)\s*\+\s*[\'"]SELECT', re.IGNORECASE),
            'mistake': 'String concatenation with user input in SQL query',
            'explanation': 'Directly concatenating user input into SQL queries allows attackers to inject malicious SQL commands',
            'solution': 'Use parameterized queries or prepared statements',
            'example': 'cursor.execute("SELECT * FROM users WHERE name = %s", (user_input,))'
        },
        {
            'pattern': re.compile(r'\.execute\s*\(.*\+\s*.*input', re.IGNORECASE),
            'mistake': 'Direct string concatenation in database execute method',
            'explanation': 'Unsanitized user input in SQL execution can lead to SQL injection',
            'solution': 'Use query parameters or ORM with built-in sanitization',
            'example': 'Use SQLAlchemy or Django ORM with parameterized queries'
        },
        {
            'pattern': re.compile(r'["\']\s*\+\s*\w+_input', re.IGNORECASE),
            'mistake': 'String concatenation with user input variable in SQL query',
            'explanation': 'Directly concatenating user input variables into SQL queries allows attackers to inject malicious SQL commands',
            'solution': 'Use parameterized queries or prepared statements',
            'example': 'cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))'
        },
        # Command Injection patterns
        {
            'pattern': re.compile(r'os\.system\s*\(.*input', re.IGNORECASE),
            'mistake': 'Using os.system() with user input',
            'explanation': 'Allows command injection attacks where attackers can execute system commands',
            'solution': 'Use subprocess.run() with proper argument handling',
            'example': 'subprocess.run(["ls", "-la"], shell=False)'
        },
        {
            'pattern': re.compile(r'subprocess\.call\s*\(.*shell\s*=\s*True.*input', re.IGNORECASE),
            'mistake': 'Using subprocess with shell=True and user input',
            'explanation': 'Shell=True with user input enables command injection attacks',
            'solution': 'Use shell=False and pass arguments as list',
            'example': 'subprocess.run(["echo", user_input], shell=False)'
        },
        # Eval Injection patterns
        {
            'pattern': re.compile(r'eval\s*\(.*input', re.IGNORECASE),
            'mistake': 'Using eval() with user input',
            'explanation': 'eval() executes arbitrary code, allowing attackers to run malicious commands',
            'solution': 'Avoid eval() or use ast.literal_eval() for safe evaluation',
            'example': 'Use ast.literal_eval() for safe evaluation'
        },
        {
            'pattern': re.compile(r'exec\s*\(.*input', re.IGNORECASE),
            'mistake': 'Using exec() with user input',
            'explanation': 'exec() can execute arbitrary Python code, leading to code injection',
            'solution': 'Avoid exec() with user input or use restricted environments',
            'example': 'Use safer alternatives like function calls'
        },
        # File path traversal
        {
            'pattern': re.compile(r'open\s*\(.*input.*\)', re.IGNORECASE),
            'mistake': 'Using user input directly in file open()',
            'explanation': 'Allows path traversal attacks to access sensitive files',
            'solution': 'Validate and sanitize file paths, use safe path joining',
            'example': 'Use os.path.join() with a safe base directory'
        },
        # Pickle deserialization
        {
            'pattern': re.compile(r'pickle\.loads\s*\(.*input', re.IGNORECASE),
            'mistake': 'Unsafe deserialization with pickle',
            'explanation': 'Pickle can execute arbitrary code during deserialization',
            'solution': 'Use JSON or other safe serialization formats',
            'example': 'Use json.loads() instead of pickle.loads()'
        }
    ]

def get_javascript_patterns():
    """JavaScript-specific vulnerability patterns"""
    return [
        # XSS patterns
        {
            'pattern': re.compile(r'innerHTML\s*=\s*.*(input|value|\.value)', re.IGNORECASE),
            'mistake': 'Setting innerHTML with user input',
            'explanation': 'Allows XSS attacks where attackers can inject malicious scripts',
            'solution': 'Use textContent or proper DOM manipulation methods',
            'example': 'element.textContent = userInput'
        },
        {
            'pattern': re.compile(r'outerHTML\s*=\s*.*(input|value|\.value)', re.IGNORECASE),
            'mistake': 'Setting outerHTML with user input',
            'explanation': 'Allows XSS attacks and DOM manipulation',
            'solution': 'Use textContent or proper DOM manipulation methods',
            'example': 'Use element.replaceWith() with safe content'
        },
        {
            'pattern': re.compile(r'document\.write\s*\(.*(input|value|\.value)', re.IGNORECASE),
            'mistake': 'Using document.write() with user input',
            'explanation': 'Can lead to XSS attacks and page hijacking',
            'solution': 'Use DOM manipulation methods instead',
            'example': 'document.createElement() and appendChild()'
        },
        # Eval injection
        {
            'pattern': re.compile(r'eval\s*\(.*(input|value|\.value)', re.IGNORECASE),
            'mistake': 'Using eval() with user input',
            'explanation': 'eval() executes arbitrary JavaScript code, leading to code injection',
            'solution': 'Avoid eval() and use JSON.parse() for JSON data',
            'example': 'const data = JSON.parse(userInput)'
        },
        {
            'pattern': re.compile(r'new Function\s*\(.*(input|value|\.value)', re.IGNORECASE),
            'mistake': 'Using Function constructor with user input',
            'explanation': 'Creates functions from strings, allowing code injection',
            'solution': 'Avoid Function constructor with user input',
            'example': 'Define functions normally instead'
        },
        {
            'pattern': re.compile(r'setTimeout\s*\(.*(input|value|\.value)', re.IGNORECASE),
            'mistake': 'Using setTimeout with string from user input',
            'explanation': 'Can execute arbitrary code if input contains JavaScript',
            'solution': 'Use function references instead of strings',
            'example': 'setTimeout(() => { /* code */ }, delay)'
        },
        # Unsafe DOM methods
        {
            'pattern': re.compile(r'\.insertAdjacentHTML\s*\(.*(input|value|\.value)', re.IGNORECASE),
            'mistake': 'Using insertAdjacentHTML with user input',
            'explanation': 'Can lead to XSS if input contains malicious HTML',
            'solution': 'Create elements and append them safely',
            'example': 'Use createElement() and appendChild()'
        },
        # JQuery unsafe methods
        {
            'pattern': re.compile(r'\$\(.*\)\.html\s*\(.*(input|value|\.value)', re.IGNORECASE),
            'mistake': 'Using jQuery.html() with user input',
            'explanation': 'Can lead to XSS attacks',
            'solution': 'Use jQuery.text() or proper sanitization',
            'example': '$("#element").text(userInput)'
        },
        {
            'pattern': re.compile(r'\$\(.*\)\.append\s*\(.*(input|value|\.value)', re.IGNORECASE),
            'mistake': 'Using jQuery.append() with user input containing HTML',
            'explanation': 'Can lead to XSS if input contains malicious HTML',
            'solution': 'Sanitize input or create elements safely',
            'example': 'Create element with jQuery: $("<div>").text(userInput)'
        }
    ]