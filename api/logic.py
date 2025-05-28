from http.server import BaseHTTPRequestHandler
import json
import sys
import traceback

# Try to import aima3, fall back to mock implementations if not available
try:
    from aima3.logic import *
    from aima3.utils import expr
    AIMA_AVAILABLE = True
except ImportError:
    AIMA_AVAILABLE = False
    print("AIMA3 not available, using mock implementations")

# Mock implementations when aima3 is not available
if not AIMA_AVAILABLE:
    class MockExpr:
        def __init__(self, s):
            self.s = s
        def __str__(self):
            return self.s
        def __repr__(self):
            return f"expr('{self.s}')"
        def __eq__(self, other):
            return isinstance(other, MockExpr) and self.s == other.s
        def __hash__(self):
            return hash(self.s)

    def expr(s):
        return MockExpr(s)

    def pl_true(kb, query):
        return f"pl_true({kb}, {query})"

    class PropKB:
        def __init__(self):
            self.clauses = []
        def tell(self, sentence):
            self.clauses.append(sentence)
        def ask(self, query):
            return f"PropKB.ask({query})"
        def __str__(self):
            return f"PropKB({len(self.clauses)} clauses)"

    class FolKB:
        def __init__(self):
            self.clauses = []
        def tell(self, sentence):
            self.clauses.append(sentence)
        def ask(self, query):
            return f"FolKB.ask({query})"
        def __str__(self):
            return f"FolKB({len(self.clauses)} clauses)"

    def fol_fc_ask(kb, query):
        return f"fol_fc_ask({kb}, {query})"

    def fol_bc_ask(kb, query):
        return f"fol_bc_ask({kb}, {query})"

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                try:
                    body = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError as e:
                    self.send_error_response({"error": "Invalid JSON", "details": str(e)})
                    return
            else:
                body = {}

            expr_str = body.get("expr")
            if not expr_str:
                self.send_error_response({"error": 'Missing "expr" parameter'})
                return

            # Create safe execution environment
            safe_globals = {
                '__builtins__': {
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'all': all,
                    'any': any,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round,
                    'print': print,
                },
                'expr': expr,
                'pl_true': pl_true,
                'PropKB': PropKB,
                'FolKB': FolKB,
                'fol_fc_ask': fol_fc_ask,
                'fol_bc_ask': fol_bc_ask,
            }

        
            if AIMA_AVAILABLE:
                try:
                    safe_globals.update({
                        'pl_resolution': pl_resolution,
                        'dpll_satisfiable': dpll_satisfiable,
                        'walksat': walksat,
                        'unify': unify,
                        'substitute': substitute,
                        'standardize_variables': standardize_variables,
                    })
                except NameError:
                    pass  # Some functions might not be available

            # Execute the expression
            local_vars = {}
            try:
                # Handle multi-line expressions
                if '\n' in expr_str.strip():
                    lines = [line.strip() for line in expr_str.strip().split('\n') if line.strip()]
                    if len(lines) > 1:
                        # Execute all lines except the last one
                        for line in lines[:-1]:
                            exec(line, safe_globals, local_vars)
                        # Evaluate the last line and return the result
                        result = eval(lines[-1], {**safe_globals, **local_vars}, {})
                    else:
                        result = eval(lines[0], safe_globals, local_vars)
                else:
                    # Single expression
                    result = eval(expr_str, safe_globals, local_vars)

                # Convert result to serializable format
                if hasattr(result, '__dict__'):
                    # Custom object - try to serialize important attributes
                    if hasattr(result, '__str__'):
                        result = str(result)
                    else:
                        result = repr(result)
                elif hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
                    # Iterable (list, tuple, set, etc.)
                    try:
                        result = list(result)
                        # Convert each item to string if necessary
                        result = [str(item) if hasattr(item, '__str__') and not isinstance(item, (int, float, bool, str)) else item for item in result]
                    except:
                        result = str(result)
                elif not isinstance(result, (int, float, bool, str, type(None))):
                    result = str(result)

                self.send_success_response({
                    "result": result,
                    "aima_available": AIMA_AVAILABLE,
                    "expression": expr_str
                })

            except SyntaxError as e:
                self.send_error_response({
                    "error": "Syntax Error",
                    "details": str(e),
                    "line": getattr(e, 'lineno', None),
                    "offset": getattr(e, 'offset', None)
                })
            except NameError as e:
                self.send_error_response({
                    "error": "Name Error",
                    "details": str(e),
                    "suggestion": "Check if all variables and functions are defined"
                })
            except Exception as e:
                self.send_error_response({
                    "error": type(e).__name__,
                    "details": str(e),
                    "traceback": traceback.format_exc()
                })

        except Exception as e:
            self.send_error_response({
                "error": "Request Processing Error",
                "details": str(e),
                "traceback": traceback.format_exc()
            })

    def send_success_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_json.encode('utf-8'))

    def send_error_response(self, data):
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_json.encode('utf-8'))

    def do_GET(self):
        self.send_success_response({
            "message": "Python Logic Compiler API",
            "aima_available": AIMA_AVAILABLE,
            "usage": "Send POST requests with { expr: 'your_python_expression' }",
            "examples": [
                "expr('P & Q')",
                "kb = PropKB(); kb.tell(expr('P')); kb.ask(expr('P'))",
                "pl_true({expr('P'): True}, expr('P & Q'))"
            ]
        })