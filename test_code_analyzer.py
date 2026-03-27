"""
Test script for the Static Code Analyzer
Tests both unsafe and safe code examples
"""

import requests
import json

def test_code_analyzer(code, language='python', expected_vulnerable=None, title="Test"):
    """Test the code analyzer with a code snippet"""
    print(f"\n{'='*70}")
    print(f"\nTest: {title}")
    print(f"Language: {language}")
    print(f"Code:\n{code}\n")

    payload = {
        "code": code,
        "language": language
    }

    try:
        response = requests.post(
            "http://127.0.0.1:5000/analyze_code",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"[OK] SUCCESS - Response Status: 200")
            print(f"\n[RESULTS] Analysis Results:")
            print(f"   Vulnerable: {result.get('vulnerable', 'N/A')}")
            print(f"   Type: {result.get('type', 'N/A')}")
            print(f"   Explanation: {result.get('explanation', 'N/A')}")
            print(f"   Vulnerabilities Found: {len(result.get('vulnerabilities', []))}")

            if result.get('vulnerabilities'):
                print(f"\n🐛 Vulnerability Details:")
                for i, vuln in enumerate(result.get('vulnerabilities', []), 1):
                    print(f"   {i}. Line {vuln.get('line', 'N/A')}: {vuln.get('mistake', 'Unknown')}")
                    print(f"      Risk: {vuln.get('explanation', 'N/A')}")

            # Verify expectation if provided
            if expected_vulnerable is not None:
                actual = result.get('vulnerable')
                if actual == expected_vulnerable:
                    print(f"\n[OK] CORRECT - Detection matched expected result (vulnerable={expected_vulnerable})")
                else:
                    print(f"\n[ERROR] INCORRECT - Expected vulnerable={expected_vulnerable}, got {actual}")
                    return False

            return True
        else:
            print(f"[ERROR] ERROR - HTTP Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] EXCEPTION: {str(e)}")
        return False

def print_test_results(passed, total):
    """Print summary of test results"""
    print(f"\n{'='*70}")
    print(f"\n[SUMMARY] TEST SUMMARY:")
    print(f"   Tests Passed: {passed}/{total}")
    print(f"   Tests Failed: {total - passed}/{total}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print(f"\n[SUCCESS] ALL TESTS PASSED! Code analyzer is working correctly.")
    else:
        print(f"\n[WARNING]  Some tests failed. Review the output above.")

if __name__ == "__main__":
    print("="*70)
    print("STATIC CODE ANALYZER TEST SUITE")
    print("="*70)

    # Check if backend is running
    try:
        health = requests.get("http://127.0.0.1:5000/", timeout=5)
        if health.status_code != 200:
            print("[ERROR] Backend is not responding at http://127.0.0.1:5000")
            print("   Please start the Flask server first: python Backend/app.py")
            exit(1)
    except Exception as e:
        print(f"[ERROR] Cannot connect to backend: {e}")
        print("   Please start the Flask server first: python Backend/app.py")
        exit(1)

    print("[OK] Backend is running\n")

    # Test cases
    tests_passed = 0
    total_tests = 0

    # === UNSAFE CODE TESTS ===
    print("\n" + "="*70)
    print("[UNSAFE] TESTING UNSAFE CODE (Should be flagged as vulnerable)")
    print("="*70)

    # Test 1: SQL Injection
    total_tests += 1
    unsafe_sql_code = '''query = "SELECT * FROM users WHERE id=" + user_input
cursor.execute(query)'''
    if test_code_analyzer(
        unsafe_sql_code,
        language='python',
        expected_vulnerable=True,
        title="SQL Injection - String concatenation"
    ):
        tests_passed += 1

    # Test 2: Command Injection
    total_tests += 1
    unsafe_cmd_code = '''import os
user_input = request.form['hostname']
os.system("ping " + user_input)'''
    if test_code_analyzer(
        unsafe_cmd_code,
        language='python',
        expected_vulnerable=True,
        title="Command Injection - os.system with user input"
    ):
        tests_passed += 1

    # Test 3: SQL Injection with document.write (JavaScript)
    total_tests += 1
    unsafe_xss_js = '''document.write(user_input)'''
    if test_code_analyzer(
        unsafe_xss_js,
        language='javascript',
        expected_vulnerable=True,
        title="XSS - document.write with user input"
    ):
        tests_passed += 1

    # Test 4: Python eval injection
    total_tests += 1
    unsafe_eval_code = '''user_input = request.form['code']
eval(user_input)'''
    if test_code_analyzer(
        unsafe_eval_code,
        language='python',
        expected_vulnerable=True,
        title="Eval Injection - eval() with user input"
    ):
        tests_passed += 1

    # === SAFE CODE TESTS ===
    print("\n" + "="*70)
    print("[SAFE] TESTING SAFE CODE (Should NOT be flagged as vulnerable)")
    print("="*70)

    # Test 5: Safe parameterized query
    total_tests += 1
    safe_sql_code = '''query = "SELECT * FROM users WHERE id=%s"
cursor.execute(query, (user_id,))'''
    if test_code_analyzer(
        safe_sql_code,
        language='python',
        expected_vulnerable=False,
        title="Safe SQL - Parameterized query"
    ):
        tests_passed += 1

    # Test 6: Safe subprocess without shell
    total_tests += 1
    safe_cmd_code = '''import subprocess
subprocess.run(["ls", "-la"], shell=False)'''
    if test_code_analyzer(
        safe_cmd_code,
        language='python',
        expected_vulnerable=False,
        title="Safe Command - subprocess without shell"
    ):
        tests_passed += 1

    # Test 7: Safe textContent (JavaScript)
    total_tests += 1
    safe_js_code = '''element.textContent = userInput'''
    if test_code_analyzer(
        safe_js_code,
        language='javascript',
        expected_vulnerable=False,
        title="Safe JS - textContent instead of innerHTML"
    ):
        tests_passed += 1

    # === SUMMARY ===
    print_test_results(tests_passed, total_tests)

    if tests_passed == total_tests:
        print("\n[DONE] All critical fixes are working correctly!")
        print("   The analyzer now:")
        print("   • Forces LLM to output JSON format")
        print("   • Falls back to rule-based detection when needed")
        print("   • Correctly identifies vulnerable code")
        print("   • Correctly identifies safe code")
        exit(0)
    else:
        print("\n[ERROR] Issues remain. Review the failed tests above.")
        exit(1)
