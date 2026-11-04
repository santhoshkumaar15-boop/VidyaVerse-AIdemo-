"""
Simple, Safe Strands Coding Lab Tool for EduMateAI
Evaluates hands-on Python functions and in-memory SQLite SQL queries deterministically.
"""

import json
import sqlite3
from strands import tool

CODING_CHALLENGES = [
    {
        "id": "py_two_sum",
        "language": "Python",
        "difficulty": "Easy",
        "title": "1. Pair Target Sum (`two_sum_exists`)",
        "prompt": (
            "Write a function `two_sum_exists(nums, target)` that returns `True` if **any two distinct elements** "
            "in `nums` add up to `target`, and `False` otherwise."
        ),
        "starter_code": (
            "def two_sum_exists(nums, target):\n"
            "    seen = set()\n"
            "    for n in nums:\n"
            "        # Check if complement was already seen\n"
            "        pass\n"
            "    return False\n"
        ),
        "hint": "For each number `n`, check if `target - n` is already in `seen`; if not, `seen.add(n)`.",
    },
    {
        "id": "py_brackets",
        "language": "Python",
        "difficulty": "Medium",
        "title": "2. Balanced Brackets Validator (`is_balanced`)",
        "prompt": (
            "Write a function `is_balanced(s)` that returns `True` if all parentheses `()`, `[]`, and `{}` "
            "in string `s` are properly matched and nested, or `False` otherwise."
        ),
        "starter_code": (
            "def is_balanced(s):\n"
            "    stack = []\n"
            "    pairs = {')': '(', ']': '[', '}': '{'}\n"
            "    # Push opening brackets and match closing brackets\n"
            "    return len(stack) == 0\n"
        ),
        "hint": "Push `(` `[` `{` onto `stack`. When seeing a closing bracket `ch`, fail if `not stack or stack.pop() != pairs[ch]`.",
    },
    {
        "id": "py_top_word",
        "language": "Python",
        "difficulty": "Medium",
        "title": "3. Most Frequent Keyword (`top_word`)",
        "prompt": (
            "Write a function `top_word(words)` that takes a non-empty list of lowercase strings "
            "and returns the string that appears most frequently."
        ),
        "starter_code": (
            "def top_word(words):\n"
            "    counts = {}\n"
            "    # Count occurrences of each word and return the max\n"
            "    return words[0]\n"
        ),
        "hint": "Populate `counts[w] = counts.get(w, 0) + 1`, then return `max(counts, key=counts.get)`.",
    },
    {
        "id": "sql_honour_roll",
        "language": "SQL",
        "difficulty": "Easy",
        "title": "4. Honour Roll Filter (`SELECT` + `ORDER BY`)",
        "prompt": (
            "Given table `students(id, name, major, score)`, write a `SELECT` query returning `name` and `score` "
            "for all students with `score >= 85`, ordered by `score` **descending**."
        ),
        "schema_preview": "students: (1,'Aarav','CS',92), (2,'Meera','AI',88), (3,'Rohan','CS',74), (4,'Diya','DS',96)",
        "starter_code": "SELECT name, score\nFROM students\nWHERE score >= 85\nORDER BY score DESC;",
        "hint": "Select `name, score` from `students`, filter `WHERE score >= 85`, and sort `ORDER BY score DESC`.",
    },
    {
        "id": "sql_dept_avg",
        "language": "SQL",
        "difficulty": "Medium",
        "title": "5. High-Performing Departments (`GROUP BY` + `HAVING`)",
        "prompt": (
            "Given table `employees(id, name, department, salary)`, return `department` and `AVG(salary)` "
            "for departments whose average salary is **strictly greater than 75000**, ordered by `AVG(salary)` descending."
        ),
        "schema_preview": "employees: Engineering (85k, 95k), Design (70k, 72k), AI_Research (105k, 95k)",
        "starter_code": (
            "SELECT department, AVG(salary) AS avg_salary\n"
            "FROM employees\n"
            "-- Add GROUP BY, HAVING, and ORDER BY below\n"
        ),
        "hint": "Use `GROUP BY department HAVING AVG(salary) > 75000 ORDER BY avg_salary DESC`.",
    },
    {
        "id": "sql_customer_join",
        "language": "SQL",
        "difficulty": "Hard",
        "title": "6. Top Customer Spend (`INNER JOIN` + `SUM`)",
        "prompt": (
            "Given `customers(id, name)` and `orders(id, customer_id, amount)`, write a query returning "
            "`name` and total order spend `SUM(amount)` for each customer with orders, ordered from highest spend to lowest."
        ),
        "schema_preview": "customers(1:'Ananya', 2:'Vikram', 3:'Sara') + orders(c1: 300+200, c2: 150, c3: 700)",
        "starter_code": (
            "SELECT c.name, SUM(o.amount) AS total_spent\n"
            "FROM customers c\n"
            "JOIN orders o ON c.id = o.customer_id\n"
            "-- Group by customer and order descending\n"
        ),
        "hint": "Add `GROUP BY c.name ORDER BY total_spent DESC;`.",
    },
]


def _run_python_tests(challenge_id: str, code_str: str) -> dict:
    banned = ["import os", "import sys", "subprocess", "open(", "__import__", "eval(", "exec("]
    for token in banned:
        if token in code_str:
            return {"passed": False, "feedback": f"Restricted statement `{token}` is not allowed in the sandbox.", "results": []}

    safe_builtins = {
        "len": len, "range": range, "set": set, "dict": dict, "list": list, "tuple": tuple,
        "max": max, "min": min, "sum": sum, "sorted": sorted, "enumerate": enumerate,
        "zip": zip, "abs": abs, "bool": bool, "int": int, "str": str, "True": True, "False": False, "None": None,
    }
    env: dict = {"__builtins__": safe_builtins}
    try:
        exec(code_str, env, env)
    except Exception as e:
        return {"passed": False, "feedback": f"Syntax / Runtime Error: {e}", "results": []}

    test_suites = {
        "py_two_sum": (
            "two_sum_exists",
            [
                (([2, 7, 11, 15], 9), True, "two_sum_exists([2, 7, 11, 15], 9) -> True"),
                (([3, 3], 6), True, "two_sum_exists([3, 3], 6) -> True"),
                (([1, 2, 4], 10), False, "two_sum_exists([1, 2, 4], 10) -> False"),
            ],
        ),
        "py_brackets": (
            "is_balanced",
            [
                (("({[]})",), True, "is_balanced('({[]})') -> True"),
                (("([)]",), False, "is_balanced('([)]') -> False"),
                (("(((",), False, "is_balanced('(((') -> False"),
            ],
        ),
        "py_top_word": (
            "top_word",
            [
                ((["ai", "python", "ai", "sql"],), "ai", "top_word(['ai','python','ai','sql']) -> 'ai'"),
                ((["tree", "graph", "graph"],), "graph", "top_word(['tree','graph','graph']) -> 'graph'"),
                ((["solo"],), "solo", "top_word(['solo']) -> 'solo'"),
            ],
        ),
    }

    fn_name, cases = test_suites[challenge_id]
    fn = env.get(fn_name)
    if not callable(fn):
        return {"passed": False, "feedback": f"Function `{fn_name}` was not found. Keep the starter function name.", "results": []}

    results = []
    all_ok = True
    for args, expected, desc in cases:
        try:
            actual = fn(*args)
            ok = actual == expected
        except Exception as err:
            actual = f"Error: {err}"
            ok = False
        if not ok:
            all_ok = False
        results.append({"case": desc, "passed": ok, "actual": str(actual), "expected": str(expected)})

    msg = "All 3 Python unit test cases passed!" if all_ok else "Some test cases did not match expected output. Check the breakdown below."
    return {"passed": all_ok, "feedback": msg, "results": results}


def _run_sql_tests(challenge_id: str, query_str: str) -> dict:
    clean_sql = query_str.strip()
    non_comment_lines = [
        ln.strip() for ln in clean_sql.splitlines() if ln.strip() and not ln.strip().startswith("--")
    ]
    first_stmt = non_comment_lines[0].lower() if non_comment_lines else ""
    if not first_stmt.startswith(("select", "with")):
        return {"passed": False, "feedback": "Only `SELECT` read queries are permitted in the SQL sandbox.", "rows": [], "columns": []}

    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE students (id INTEGER, name TEXT, major TEXT, score INTEGER);
        INSERT INTO students VALUES (1,'Aarav','CS',92), (2,'Meera','AI',88), (3,'Rohan','CS',74), (4,'Diya','DS',96);

        CREATE TABLE employees (id INTEGER, name TEXT, department TEXT, salary REAL);
        INSERT INTO employees VALUES
            (1,'Kiran','Engineering',85000), (2,'Neha','Engineering',95000),
            (3,'kabir','Design',70000), (4,'Tara','Design',72000),
            (5,'Dev','AI_Research',105000), (6,'Zoya','AI_Research',95000);

        CREATE TABLE customers (id INTEGER, name TEXT);
        INSERT INTO customers VALUES (1,'Ananya'), (2,'Vikram'), (3,'Sara');

        CREATE TABLE orders (id INTEGER, customer_id INTEGER, amount REAL);
        INSERT INTO orders VALUES (101,1,300), (102,1,200), (103,2,150), (104,3,700);
        """
    )

    expected_queries = {
        "sql_honour_roll": "SELECT name, score FROM students WHERE score >= 85 ORDER BY score DESC",
        "sql_dept_avg": "SELECT department, AVG(salary) FROM employees GROUP BY department HAVING AVG(salary) > 75000 ORDER BY AVG(salary) DESC",
        "sql_customer_join": "SELECT c.name, SUM(o.amount) FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.name ORDER BY SUM(o.amount) DESC",
    }

    try:
        user_rows = cur.execute(clean_sql).fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        exp_rows = cur.execute(expected_queries[challenge_id]).fetchall()
    except Exception as e:
        conn.close()
        return {"passed": False, "feedback": f"SQL Error: {e}", "rows": [], "columns": []}

    conn.close()
    passed = user_rows == exp_rows
    feedback = (
        "Exact match! Your SQL query returned the expected result set."
        if passed
        else f"Query ran cleanly ({len(user_rows)} rows), but output differed from expected {exp_rows}."
    )
    return {
        "passed": passed,
        "feedback": feedback,
        "columns": cols,
        "rows": [list(r) for r in user_rows],
    }


@tool
def evaluate_code_challenge(challenge_id: str, student_code: str) -> str:
    """
    Evaluates a student's Python or SQL challenge submission against deterministic unit test cases.
    """
    challenge = next((c for c in CODING_CHALLENGES if c["id"] == challenge_id), None)
    if not challenge:
        return json.dumps({"passed": False, "feedback": "Unknown challenge ID."})

    if challenge["language"] == "Python":
        res = _run_python_tests(challenge_id, student_code)
    else:
        res = _run_sql_tests(challenge_id, student_code)

    res["challenge_id"] = challenge_id
    res["language"] = challenge["language"]
    return json.dumps(res, indent=2)
