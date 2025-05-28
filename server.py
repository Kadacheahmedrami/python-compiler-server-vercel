from flask import Flask, request, jsonify
import traceback

# Explicitly import from aima3
from aima3.utils import expr
from aima3.logic import *

app = Flask(__name__)

@app.route("/", methods=["POST"])
def handler():
    try:
        body = request.get_json()
        if not body or 'expr' not in body:
            return jsonify({"error": 'Missing "expr" in request body'}), 400

        expr_str = body['expr']

        # Extend safe globals with specific functions
        safe_globals = {
            '__builtins__': {},
            'expr': expr,
            'pl_true': pl_true,
            'PropKB': PropKB,
            'FolKB': FolKB,
            'fol_fc_ask': fol_fc_ask,
            'fol_bc_ask': fol_bc_ask,
            'list': list,  # Need this for converting generators to lists
        }

        # Check if it's a single expression or multiple statements
        if '\n' in expr_str.strip() or ';' in expr_str:
            # Use exec for multiple statements
            local_vars = {}
            
            # Split into lines and execute all but the last
            lines = [line.strip() for line in expr_str.strip().split('\n') if line.strip()]
            
            if len(lines) > 1:
                # Execute all lines except the last one
                for line in lines[:-1]:
                    exec(line, safe_globals, local_vars)
                
                # Evaluate the last line as an expression
                result = eval(lines[-1], {**safe_globals, **local_vars}, {})
            else:
                # Single line, just evaluate it
                result = eval(lines[0], safe_globals, local_vars)
        else:
            # Use eval for single expressions
            result = eval(expr_str, safe_globals, {})

        try:
            return jsonify({"result": result}), 200
        except (TypeError, OverflowError):
            return jsonify({"result": repr(result)}), 200

    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"error": str(e), "traceback": tb}), 500

if __name__ == "__main__":
    app.run(port=3000, debug=True)