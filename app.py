from flask import Flask, request, jsonify
import sys
import io
import traceback
import contextlib

app = Flask(__name__)

@app.route('/')
def welcome():
    return "Welcome to the Python App"

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
                
            except Exception as e:
                # Get the error traceback
                error_traceback = traceback.format_exc()
                stderr_output = stderr_buffer.getvalue()
                
                return jsonify({
                    'success': False,
                    'error': str(e),
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