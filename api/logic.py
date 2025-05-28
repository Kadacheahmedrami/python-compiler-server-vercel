from http.server import BaseHTTPRequestHandler
import json
import sys
import traceback
import re

# Try to import aima3, fall back to mock implementations if not available
try:
    from aima3.logic import *
    from aima3.utils import expr
    AIMA_AVAILABLE = True
    print("AIMA3 successfully loaded")
except ImportError:
    AIMA_AVAILABLE = False
    print("AIMA3 not available, using enhanced mock implementations")

# Enhanced mock implementations when aima3 is not available
if not AIMA_AVAILABLE:
    class MockExpr:
        def __init__(self, s):
            self.s = str(s).strip()
            # Parse basic logical operators
            self.parsed = self._parse_expression(self.s)
        
        def _parse_expression(self, expr_str):
            # Simple parser for basic logical expressions
            return {
                'original': expr_str,
                'operators': self._find_operators(expr_str),
                'variables': self._find_variables(expr_str)
            }
        
        def _find_operators(self, expr_str):
            operators = []
            if '&' in expr_str: operators.append('&')
            if '|' in expr_str: operators.append('|')
            if '>>' in expr_str: operators.append('>>')
            if '~' in expr_str: operators.append('~')
            return operators
        
        def _find_variables(self, expr_str):
            # Extract variables (letters that aren't operators)
            import re
            variables = re.findall(r'\b[A-Z][a-zA-Z0-9_]*\b', expr_str)
            return list(set(variables))
        
        def __str__(self):
            return self.s
        
        def __repr__(self):
            return f"expr('{self.s}')"
        
        def __eq__(self, other):
            return isinstance(other, MockExpr) and self.s == other.s
        
        def __hash__(self):
            return hash(self.s)
        
        def __and__(self, other):
            return MockExpr(f"({self.s} & {other.s})")
        
        def __or__(self, other):
            return MockExpr(f"({self.s} | {other.s})")
        
        def __rshift__(self, other):
            return MockExpr(f"({self.s} >> {other.s})")
        
        def __invert__(self):
            return MockExpr(f"~{self.s}")

    def expr(s):
        return MockExpr(s)

    def pl_true(sentence, model):
        """Mock implementation of pl_true"""
        if isinstance(sentence, MockExpr):
            expr_str = sentence.s
            # Simple evaluation for basic cases
            if expr_str in model:
                return model[expr_str]
            
            # Handle simple conjunctions and disjunctions
            if '&' in expr_str:
                parts = [p.strip().strip('()') for p in expr_str.split('&')]
                return all(model.get(p, False) for p in parts)
            elif '|' in expr_str:
                parts = [p.strip().strip('()') for p in expr_str.split('|')]
                return any(model.get(p, False) for p in parts)
            elif expr_str.startswith('~'):
                inner = expr_str[1:].strip()
                return not model.get(inner, False)
        
        return None

    class PropKB:
        def __init__(self):
            self.clauses = []
            self.facts = set()
        
        def tell(self, sentence):
            """Add a sentence to the knowledge base"""
            self.clauses.append(sentence)
            if isinstance(sentence, MockExpr):
                # Extract simple facts
                if sentence.s and not any(op in sentence.s for op in ['&', '|', '>>', '~']):
                    self.facts.add(sentence.s)
        
        def ask(self, query):
            """Query the knowledge base"""
            if isinstance(query, MockExpr):
                query_str = query.s
                
                # Simple fact checking
                if query_str in self.facts:
                    return [query]
                
                # Check if we can derive the query from known facts
                # This is a very simplified inference
                for clause in self.clauses:
                    if isinstance(clause, MockExpr):
                        clause_str = clause.s
                        # Handle simple implications: P >> Q
                        if '>>' in clause_str:
                            parts = clause_str.split('>>')
                            if len(parts) == 2:
                                antecedent = parts[0].strip().strip('()')
                                consequent = parts[1].strip().strip('()')
                                if antecedent in self.facts and consequent == query_str:
                                    return [query]
            
            return []
        
        def __str__(self):
            return f"PropKB({len(self.clauses)} clauses: {[str(c) for c in self.clauses]})"
        
        def __repr__(self):
            return self.__str__()

    class FolKB:
        def __init__(self):
            self.clauses = []
        
        def tell(self, sentence):
            self.clauses.append(sentence)
        
        def ask(self, query):
            return f"FolKB.ask({query}) - {len(self.clauses)} clauses available"
        
        def __str__(self):
            return f"FolKB({len(self.clauses)} clauses)"

    def fol_fc_ask(kb, query):
        return f"fol_fc_ask result for {query} in KB with {len(kb.clauses) if hasattr(kb, 'clauses') else 0} clauses"

    def fol_bc_ask(kb, query):
        return f"fol_bc_ask result for {query} in KB with {len(kb.clauses) if hasattr(kb, 'clauses') else 0} clauses"

    def dpll_satisfiable(sentence):
        """Mock DPLL satisfiability checker"""
        if isinstance(sentence, MockExpr):
            expr_str = sentence.s
            # Check for obvious contradictions
            if 'P & ~P' in expr_str or '~P & P' in expr_str:
                return False
            # Simple cases
            if '&' in expr_str and '~' not in expr_str:
                return True  # Simple conjunctions are usually satisfiable
        return True

    def unify(x, y, s=None):
        """Mock unification"""
        if s is None:
            s = {}
        return f"unify({x}, {y}) -> {s}"

    def substitute(s, x):
        """Mock substitution"""
        return f"substitute({s}, {x})"

    def standardize_variables(sentence):
        """Mock variable standardization"""
        return sentence

    def pl_resolution(kb, alpha):
        """Mock resolution"""
        return f"pl_resolution({kb}, {alpha})"

    def walksat(clauses):
        """Mock WalkSAT"""
        return f"walksat({clauses})"

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
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

            # Clean up the expression - remove problematic import statements
            clean_expr = self._clean_expression(expr_str)

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
                    'True': True,
                    'False': False,
                    'None': None,
                },
                'expr': expr,
                'pl_true': pl_true,
                'PropKB': PropKB,
                'FolKB': FolKB,
                'fol_fc_ask': fol_fc_ask,
                'fol_bc_ask': fol_bc_ask,
                'dpll_satisfiable': dpll_satisfiable,
                'unify': unify,
                'substitute': substitute,
                'standardize_variables': standardize_variables,
                'pl_resolution': pl_resolution,
                'walksat': walksat,
            }

            # Execute the expression
            local_vars = {}
            try:
                # Handle multi-line expressions
                if '\n' in clean_expr.strip():
                    lines = [line.strip() for line in clean_expr.strip().split('\n') if line.strip()]
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
                    result = eval(clean_expr, safe_globals, local_vars)

                # Convert result to serializable format
                serialized_result = self._serialize_result(result)

                self.send_success_response({
                    "result": serialized_result,
                    "aima_available": AIMA_AVAILABLE,
                    "expression": expr_str,
                    "cleaned_expression": clean_expr if clean_expr != expr_str else None
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

    def _clean_expression(self, expr_str):
        """Remove problematic import statements and clean up expression"""
        lines = expr_str.strip().split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip import statements
            if line.startswith('from ') and 'import' in line:
                continue
            if line.startswith('import '):
                continue
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def _serialize_result(self, result):
        """Convert result to JSON-serializable format"""
        if result is None:
            return None
        elif isinstance(result, (int, float, bool, str)):
            return result
        elif hasattr(result, '__dict__'):
            # Custom object - try to serialize important attributes
            if hasattr(result, '__str__'):
                return str(result)
            else:
                return repr(result)
        elif hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
            # Iterable (list, tuple, set, etc.)
            try:
                result_list = list(result)
                # Convert each item to string if necessary
                return [self._serialize_result(item) for item in result_list]
            except:
                return str(result)
        else:
            return str(result)

    def send_success_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_json.encode('utf-8'))

    def send_error_response(self, data):
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        response_json = json.dumps(data, ensure_ascii_false, indent=2)
        self.wfile.write(response_json.encode('utf-8'))

    def do_GET(self):
        self.send_success_response({
            "message": "Enhanced Python Logic Compiler API",
            "aima_available": AIMA_AVAILABLE,
            "usage": "Send POST requests with { expr: 'your_python_expression' }",
            "features": [
                "Enhanced mock implementations when AIMA3 not available",
                "Automatic import statement filtering",
                "Better knowledge base operations",
                "Improved logical expression parsing"
            ],
            "examples": [
                "expr('P & Q')",
                "kb = PropKB(); kb.tell(expr('P')); kb.ask(expr('P'))",
                "pl_true(expr('P'), {'P': True})",
                "dpll_satisfiable(expr('P & Q'))"
            ]
        })