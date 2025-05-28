// simple_medical_test.js
// Test medical diagnosis with single expressions only

async function testSimpleMedical() {
    const url = "http://127.0.0.1:3000/";
    
    console.log("=== Testing Medical Diagnosis System ===\n");
    
    try {
        // Step 1: Create knowledge base and add facts in separate calls
        console.log("1. Creating knowledge base...");
        let payload = { expr: "FolKB()" };
        let res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        console.log("KB Created:", await res.json());
        
        // Step 2: Test adding a simple fact and rule
        console.log("\n2. Testing complete diagnosis flow...");
        const completeTest = `
kb = FolKB()
kb.tell(expr("Fever(Ahmad)"))
kb.tell(expr("Cough(Ahmad)"))
kb.tell(expr("Fever(x) & Cough(x) ==> HasFlu(x)"))
list(fol_fc_ask(kb, expr("HasFlu(x)")))
        `.trim();
        
        payload = { expr: completeTest };
        res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        let result = await res.json();
        console.log("Diagnosis result:", result);
        
        // Step 3: Test backward chaining
        console.log("\n3. Testing backward chaining...");
        const backwardTest = `
kb = FolKB()
kb.tell(expr("Fever(Ahmad)"))
kb.tell(expr("Cough(Ahmad)"))
kb.tell(expr("SoreThroat(Ahmad)"))
kb.tell(expr("Fever(x) & Cough(x) & SoreThroat(x) ==> HasStrepThroat(x)"))
list(fol_bc_ask(kb, expr("HasStrepThroat(Ahmad)")))
        `.trim();
        
        payload = { expr: backwardTest };
        res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        result = await res.json();
        console.log("Backward chaining result:", result);
        
        // Step 4: Test multiple patients
        console.log("\n4. Testing multiple patients...");
        const multiPatientTest = `
kb = FolKB()
kb.tell(expr("Rash(Fatima)"))
kb.tell(expr("JointPain(Fatima)"))
kb.tell(expr("ShortnessOfBreath(Leila)"))
kb.tell(expr("ChestPain(Leila)"))
kb.tell(expr("Rash(x) & JointPain(x) ==> HasLymeDisease(x)"))
kb.tell(expr("ShortnessOfBreath(x) & ChestPain(x) ==> HasPneumonia(x)"))
[list(fol_fc_ask(kb, expr("HasLymeDisease(x)"))), list(fol_fc_ask(kb, expr("HasPneumonia(x)")))]
        `.trim();
        
        payload = { expr: multiPatientTest };
        res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        result = await res.json();
        console.log("Multiple patients result:", result);
        
    } catch (error) {
        console.error("Error:", error);
    }
}

testSimpleMedical().catch(console.error);