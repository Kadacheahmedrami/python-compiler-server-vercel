from flask import Flask, request, jsonify
import sys
import io
import traceback
import contextlib
import subprocess
import pkg_resources

app = Flask(__name__)

# Manual CORS implementation
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/', methods=['OPTIONS'])
@app.route('/packages', methods=['OPTIONS'])
@app.route('/install', methods=['OPTIONS'])
@app.route('/code', methods=['OPTIONS'])
def handle_options():
    """Handle preflight OPTIONS requests"""
    return '', 204

@app.route('/')
def welcome():
    return "Welcome to the Python App"

@app.route('/packages', methods=['GET'])
def list_packages():
    """List installed packages"""
    try:
        installed_packages = [d.project_name for d in pkg_resources.working_set]
        return jsonify({
            'packages': sorted(installed_packages),
            'count': len(installed_packages)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/install', methods=['POST'])
def install_package():
    """Install a package using pip"""
    try:
        data = request.get_json()
        if not data or 'package' not in data:
            return jsonify({'error': 'No package specified'}), 400
        
        package = data['package']
        
        # Install the package
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', package],
            capture_output=True,
            text=True
        )
        
        return jsonify({
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/code', methods=['POST'])
def execute_code():
    try:
        # Get the code from the request
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({
                'error': 'No code provided. Send JSON with "code" field.'
            }), 400
        
        code = data['code']
        
        # Create string buffers to capture output
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        # Redirect stdout and stderr
        with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
            try:
                # Execute the code
                exec(code)
                
                # Get the outputs
                stdout_output = stdout_buffer.getvalue()
                stderr_output = stderr_buffer.getvalue()
                
                return jsonify({
                    'success': True,
                    'stdout': stdout_output,
                    'stderr': stderr_output if stderr_output else None
                })
                
            except ImportError as e:
                # Special handling for import errors
                missing_module = str(e).split("'")[1] if "'" in str(e) else "unknown"
                error_traceback = traceback.format_exc()
                stderr_output = stderr_buffer.getvalue()
                
                return jsonify({
                    'success': False,
                    'error': f'Import Error: {str(e)}',
                    'error_type': 'ImportError',
                    'missing_module': missing_module,
                    'suggestion': f'Try installing the missing module: pip install {missing_module}',
                    'traceback': error_traceback,
                    'stderr': stderr_output if stderr_output else None
                })
                
            except Exception as e:
                # Get the error traceback
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
            'error': f'Server error: {str(e)}'
        }), 500

# For Vercel deployment
if __name__ == '__main__':
    app.run(debug=True)