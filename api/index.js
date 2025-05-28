import { spawn } from "child_process";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ error: "Only POST allowed" });
    return;
  }

  try {
    const input = JSON.stringify(req.body);

    const pythonProcess = spawn("python3", ["api/logic.py"]);

    let output = "";
    let errorOutput = "";

    pythonProcess.stdout.on("data", (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      errorOutput += data.toString();
    });

    pythonProcess.on("close", (code) => {
      if (code !== 0) {
        res.status(500).json({ error: "Python script failed", details: errorOutput });
        return;
      }
      try {
        const jsonOutput = JSON.parse(output);
        res.status(200).json(jsonOutput);
      } catch (parseError) {
        res.status(500).json({ error: "Failed to parse Python output", details: output });
      }
    });

    // Send input to python stdin
    pythonProcess.stdin.write(input);
    pythonProcess.stdin.end();
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
}
