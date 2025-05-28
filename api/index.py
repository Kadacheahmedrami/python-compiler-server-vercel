import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

# Since aima3 might not be available, let's create a minimal implementation
class MockExpr:
    def __init__(self, s):
        self.s = s
    def __str__(self):
        return self.s
    def __repr__(self):
        return f"expr('{self.s}')"

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

class FolKB:
    def __init__(self):
        self.clauses = []
    def tell(self, sentence):
        self.clauses.append(sentence)
    def ask(self, query):
        return f"FolKB.ask({query})"

def fol_fc_ask(kb, query):
    return f"fol_fc_ask({kb}, {query})"

def fol_bc_ask(kb, query):
    return f"fol_bc_ask({kb}, {query})"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))

            expr_str = body.get("expr")
            if not expr_str:
                self.send_error_response({"error": 'Missing "expr"'})
                return

            safe_globals = {
                '__builtins__': {},
                'expr': expr,
                'pl_true': pl_true,
                'PropKB': PropKB,
                'FolKB': FolKB,
                'fol_fc_ask': fol_fc_ask,
                'fol_bc_ask': fol_bc_ask,
                'list': list,
            }

            if '\n' in expr_str.strip() or ';' in expr_str:
                local_vars = {}
                lines = [line.strip() for line in expr_str.strip().split('\n') if line.strip()]
                if len(lines) > 1:
                    for line in lines[:-1]:
                        exec(line, safe_globals, local_vars)
                    result = eval(lines[-1], {**safe_globals, **local_vars}, {})
                else:
                    result = eval(lines[0], safe_globals, local_vars)
            else:
                result = eval(expr_str, safe_globals, {})

            # Convert result to string if it's an object
            if hasattr(result, '__str__'):
                result = str(result)

            self.send_success_response({"result": result})

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self.send_error_response({"error": str(e), "traceback": tb})

    def send_success_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_error_response(self, data):
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()