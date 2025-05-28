export default async function handler(req, res) {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
    if (req.method === 'OPTIONS') {
      res.status(200).end();
      return;
    }

    if (req.method === 'GET') {
      res.status(200).json({
        message: "Logic Compiler API Gateway",
        endpoints: {
          "/": "This gateway (redirects to Python handler)",
          "/api/logic": "Python handler for AIMA3 logic processing"
        },
        usage: "Send POST requests with { expr: 'your_python_expression' }"
      });
      return;
    }
  
    if (req.method !== "POST") {
      res.status(405).json({ error: "Only POST and GET allowed" });
      return;
    }
  
    try {
      // Get the base URL dynamically
      const protocol = req.headers['x-forwarded-proto'] || 'https';
      const host = req.headers.host;
      const baseUrl = `${protocol}://${host}`;
      
      // Forward the request to the Python handler
      console.log('Forwarding request to Python handler...');
      const pythonResponse = await fetch(`${baseUrl}/api/logic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(req.body)
      });
  
      if (!pythonResponse.ok) {
        console.error('Python handler error:', pythonResponse.status, pythonResponse.statusText);
        let errorData;
        try {
          errorData = await pythonResponse.json();
        } catch (e) {
          const errorText = await pythonResponse.text();
          errorData = { 
            error: "Python handler error", 
            status: pythonResponse.status,
            details: errorText.substring(0, 200) + (errorText.length > 200 ? '...' : '')
          };
        }
        res.status(pythonResponse.status).json(errorData);
        return;
      }
  
      const result = await pythonResponse.json();
      res.status(200).json(result);
  
    } catch (error) {
      console.error('Error calling Python handler:', error);
      res.status(500).json({ 
        error: "Failed to process request", 
        details: error.message,
        suggestion: "Make sure the Python handler is properly deployed"
      });
    }
}