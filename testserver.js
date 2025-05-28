async function testPythonCompiler() {
    const url = 'https://python-compiler-server-vercel-pqcjelwye.vercel.app/';
    
    const payload = {
      expr: 'pl_true("P")'  // example expression from aima3 logic
    };
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Response from Python backend:', data);
    } catch (err) {
      console.error('Error:', err);
    }
  }
  
  testPythonCompiler();
  