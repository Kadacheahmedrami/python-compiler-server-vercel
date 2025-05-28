from aima3.utils import expr
from aima3.logic import *
import traceback
import json

def handler(request):
    try:
        # Parse body
        body = request.get("body")
        if isinstance(body, str):
            body = json.loads(body)

        if not body or 'expr' not in body:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": 'Missing "expr" in request body'})
            }

        expr_str = body['expr']

        # Define safe environment
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

        # Eval logic
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

        return {
            "statusCode": 200,
            "body": json.dumps({"result": result})
        }

    except Exception as e:
        tb = traceback.format_exc()
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e), "traceback": tb})
        }
