from flask import Flask, request, jsonify
import sys
import io
import traceback
import contextlib
import subprocess
import pkg_resources
import os
import tempfile

app = Flask(__name__)

# Manual CORS implementation
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,HEAD')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,HEAD')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

@app.route('/', methods=['GET', 'OPTIONS'])
def welcome():
    return jsonify({"message": "Welcome to the Python Code Executor API", "status": "running"})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "python_version": sys.version})

@app.route('/packages', methods=['GET'])
def list_packages():
    """List installed packages"""
    try:
        installed_packages = []
        for d in pkg_resources.working_set:
            try:
                installed_packages.append({
                    'name': d.project_name,
                    'version': d.version
                })
            except:
                installed_packages.append({
                    'name': d.project_name,
                    'version': 'unknown'
                })
        
        return jsonify({
            'packages': sorted(installed_packages, key=lambda x: x['name']),
            'count': len(installed_packages),
            'python_version': sys.version
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@app.route('/install', methods=['POST'])
def install_package():
    """Install a package using pip (may not work in serverless environment)"""
    try:
        data = request.get_json()
        if not data or 'package' not in data:
            return jsonify({'error': 'No package specified in request body'}), 400
        
        package = data['package'].strip()
        if not package:
            return jsonify({'error': 'Package name cannot be empty'}), 400
        
        # Check environment
        is_vercel = os.environ.get('VERCEL') == '1'
        
        if is_vercel:
            return jsonify({
                'success': False,
                'error': 'Package installation is not supported in Vercel serverless environment',
                'suggestion': 'Add packages to requirements.txt and redeploy',
                'environment': 'vercel_serverless'
            }), 400
        
        # Try to install the package
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', package, '--user'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return jsonify({
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode,
            'package': package
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Installation timeout (30 seconds)',
            'package': package
        }), 408
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@app.route('/code', methods=['POST'])
def execute_code():
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON with Content-Type: application/json'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON in request body'
            }), 400
            
        if 'code' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing "code" field in request body'
            }), 400
        
        code = data.get('code', '').strip()
        if not code:
            return jsonify({
                'success': False,
                'error': 'Code cannot be empty'
            }), 400
        
        # Security checks
        dangerous_keywords = ['import os', 'import subprocess', 'import sys', '__import__', 'exec(', 'eval(']
        if any(keyword in code.lower() for keyword in dangerous_keywords):
            return jsonify({
                'success': False,
                'error': 'Code contains potentially dangerous operations',
                'security_warning': True
            }), 400
        
        # Create string buffers to capture output
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        # Create a restricted globals dictionary
        restricted_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'reversed': reversed,
                'type': type,
                'isinstance': isinstance,
                'hasattr': hasattr,
                'getattr': getattr,
                'bool': bool,
            }
        }
        
        # Redirect stdout and stderr
        with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
            try:
                # Execute the code with restricted globals
                exec(code, restricted_globals)
                
                # Get the outputs
                stdout_output = stdout_buffer.getvalue()
                stderr_output = stderr_buffer.getvalue()
                
                return jsonify({
                    'success': True,
                    'stdout': stdout_output,
                    'stderr': stderr_output if stderr_output else None,
                    'execution_info': {
                        'python_version': sys.version.split()[0],
                        'code_length': len(code)
                    }
                })
                
            except ImportError as e:
                missing_module = str(e).split("'")[1] if "'" in str(e) else "unknown"
                error_traceback = traceback.format_exc()
                stderr_output = stderr_buffer.getvalue()
                
                return jsonify({
                    'success': False,
                    'error': f'Module not available: {str(e)}',
                    'error_type': 'ImportError',
                    'missing_module': missing_module,
                    'suggestion': f'The module "{missing_module}" is not installed or available in this environment',
                    'traceback': error_traceback,
                    'stderr': stderr_output if stderr_output else None
                })
                
            except SyntaxError as e:
                return jsonify({
                    'success': False,
                    'error': f'Syntax Error: {str(e)}',
                    'error_type': 'SyntaxError',
                    'line_number': getattr(e, 'lineno', None),
                    'error_position': getattr(e, 'offset', None)
                })
                
            except Exception as e:
                error_traceback = traceback.format_exc()
                stderr_output = stderr_buffer.getvalue()
                
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'traceback': error_traceback,
                    'stderr': stderr_output if stderr_output else None
                })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'error_type': type(e).__name__
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /',
            'GET /health',
            'GET /packages',
            'POST /install',
            'POST /code'
        ]
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method not allowed for this endpoint'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on the server'
    }), 500

# For Vercel deployment
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))