import sys
import json
from aima3.utils import expr
from aima3.logic import *

def main():
    try:
        # Read JSON string from stdin
        data = sys.stdin.read()
        body = json.loads(data)

        expr_str = body.get("expr")
        if not expr_str:
            print(json.dumps({"error": 'Missing "expr"'}))
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

        print(json.dumps({"result": result}))

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(json.dumps({"error": str(e), "traceback": tb}))

if __name__ == "__main__":
    main()
