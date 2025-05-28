export default async function handler(req, res) {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
    if (req.method === 'OPTIONS') {
      res.status(200).end();
      return;
    }
  
    if (req.method !== "POST") {
      res.status(405).json({ error: "Only POST allowed" });
      return;
    }
  
    try {
      // Get the base URL dynamically
      const protocol = req.headers['x-forwarded-proto'] || 'https';
      const host = req.headers.host;
      const baseUrl = `${protocol}://${host}`;
      
      // Call the Python function directly
      const pythonResponse = await fetch(`${baseUrl}/api/logic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(req.body)
      });
  
      if (!pythonResponse.ok) {
        const errorData = await pythonResponse.json();
        res.status(pythonResponse.status).json(errorData);
        return;
      }
  
      const result = await pythonResponse.json();
      res.status(200).json(result);
  
    } catch (error) {
      console.error('Error calling Python function:', error);
      res.status(500).json({ 
        error: "Failed to process request", 
        details: error.message 
      });
    }
  }