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
      // Process the logic directly in this handler instead of calling another endpoint
      const expr_str = req.body?.expr;
      
      if (!expr_str) {
        res.status(400).json({ error: 'Missing "expr" parameter' });
        return;
      }

      // Mock implementations for logic operations
      const createMockExpr = (s) => ({
        s: s,
        toString: () => s,
        valueOf: () => s
      });

      const safeGlobals = {
        expr: createMockExpr,
        pl_true: (kb, query) => `pl_true(${kb}, ${query})`,
        PropKB: class {
          constructor() { this.clauses = []; }
          tell(sentence) { this.clauses.push(sentence); }
          ask(query) { return `PropKB.ask(${query})`; }
        },
        FolKB: class {
          constructor() { this.clauses = []; }
          tell(sentence) { this.clauses.push(sentence); }
          ask(query) { return `FolKB.ask(${query})`; }
        },
        fol_fc_ask: (kb, query) => `fol_fc_ask(${kb}, ${query})`,
        fol_bc_ask: (kb, query) => `fol_bc_ask(${kb}, ${query})`,
        list: Array
      };

      // Simple expression evaluator
      let result;
      try {
        // For security, we'll handle only basic expressions
        // In a real implementation, you'd want a proper expression parser
        if (expr_str.includes('expr(')) {
          const match = expr_str.match(/expr\(['"]([^'"]+)['"]\)/);
          if (match) {
            result = createMockExpr(match[1]);
          } else {
            result = `Processed: ${expr_str}`;
          }
        } else {
          result = `Processed: ${expr_str}`;
        }
      } catch (evalError) {
        res.status(400).json({ 
          error: "Expression evaluation failed", 
          details: evalError.message 
        });
        return;
      }

      // Ensure result is serializable
      const serializedResult = typeof result === 'object' && result !== null 
        ? (result.toString ? result.toString() : JSON.stringify(result))
        : String(result);

      res.status(200).json({ result: serializedResult });

    } catch (error) {
      console.error('Error processing request:', error);
      res.status(500).json({ 
        error: "Failed to process request", 
        details: error.message 
      });
    }
}