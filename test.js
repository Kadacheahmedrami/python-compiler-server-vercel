import axios from 'axios';

async function testAIMA3() {
  const url = 'https://python-compiler-server-vercel.vercel.app/code';
  const codeToRun = `
# Test AIMA3 medical diagnosis system
try:
    from aima3.logic import *
    
    print("AIMA3 logic module loaded successfully!")
    
    # Create our medical knowledge base
    medical_kb = FolKB()

    # Adding patient data - everyone came in with different symptoms
    medical_kb.tell(expr("Fever(Ahmad)"))
    medical_kb.tell(expr("Cough(Ahmad)"))
    medical_kb.tell(expr("SoreThroat(Ahmad)"))

    medical_kb.tell(expr("Fatigue(Fatima)"))
    medical_kb.tell(expr("Rash(Fatima)"))
    medical_kb.tell(expr("JointPain(Fatima)"))

    medical_kb.tell(expr("ShortnessOfBreath(Leila)"))
    medical_kb.tell(expr("ChestPain(Leila)"))
    medical_kb.tell(expr("Cough(Leila)"))

    medical_kb.tell(expr("Headache(Omar)"))
    medical_kb.tell(expr("Fever(Omar)"))
    medical_kb.tell(expr("Fatigue(Omar)"))

    medical_kb.tell(expr("Nausea(Youssef)"))
    medical_kb.tell(expr("Vomiting(Youssef)"))
    medical_kb.tell(expr("AbdominalPain(Youssef)"))

    # Diagnostic rules
    medical_kb.tell(expr("Fever(x) & Cough(x) ==> HasFlu(x)"))
    medical_kb.tell(expr("Fever(x) & Cough(x) & SoreThroat(x) ==> HasStrepThroat(x)"))
    medical_kb.tell(expr("ShortnessOfBreath(x) & ChestPain(x) ==> HasPneumonia(x)"))
    medical_kb.tell(expr("Rash(x) & JointPain(x) ==> HasLymeDisease(x)"))
    medical_kb.tell(expr("Nausea(x) & Vomiting(x) ==> HasGastroenteritis(x)"))
    medical_kb.tell(expr("Headache(x) & Fever(x) ==> HasMeningitis(x)"))

    print("Knowledge base populated with patient data and rules!")
    
    # Simple diagnosis check
    print("\\nChecking specific diagnoses:")
    
    # Test Ahmad for StrepThroat
    ahmad_strep = list(fol_bc_ask(medical_kb, expr("HasStrepThroat(Ahmad)")))
    if ahmad_strep:
        print("Ahmad likely has StrepThroat")
    else:
        print("Ahmad doesn't have StrepThroat")
        
    # Test Leila for Pneumonia  
    leila_pneumonia = list(fol_bc_ask(medical_kb, expr("HasPneumonia(Leila)")))
    if leila_pneumonia:
        print("Leila likely has Pneumonia")
    else:
        print("Leila doesn't have Pneumonia")
        
    # Test Fatima for Lyme
    fatima_lyme = list(fol_bc_ask(medical_kb, expr("HasLymeDisease(Fatima)")))
    if fatima_lyme:
        print("Fatima likely has LymeDisease")
    else:
        print("Fatima doesn't have LymeDisease")

    print("\\nAIMA3 medical diagnosis test completed successfully!")
    
except Exception as e:
    print(f"AIMA3 not working properly: {e}")
    print("\\nRunning simple medical diagnosis instead...")
    
    # Simple fallback medical logic
    patients = {
        "Ahmad": ["Fever", "Cough", "SoreThroat"],
        "Fatima": ["Fatigue", "Rash", "JointPain"], 
        "Leila": ["ShortnessOfBreath", "ChestPain", "Cough"],
        "Omar": ["Headache", "Fever", "Fatigue"],
        "Youssef": ["Nausea", "Vomiting", "AbdominalPain"]
    }
    
    # Simple diagnostic rules
    rules = {
        "Flu": ["Fever", "Cough"],
        "StrepThroat": ["Fever", "Cough", "SoreThroat"],
        "Pneumonia": ["ShortnessOfBreath", "ChestPain"],
        "LymeDisease": ["Rash", "JointPain"],
        "Gastroenteritis": ["Nausea", "Vomiting"],
        "Meningitis": ["Headache", "Fever"]
    }
    
    print("Simple medical diagnosis results:")
    for patient, symptoms in patients.items():
        print(f"\\n{patient} has symptoms: {', '.join(symptoms)}")
        diagnoses = []
        for disease, required_symptoms in rules.items():
            if all(symptom in symptoms for symptom in required_symptoms):
                diagnoses.append(disease)
        
        if diagnoses:
            print(f"  Likely diagnoses: {', '.join(diagnoses)}")
        else:
            print("  No clear diagnosis from current rules")
            
    print("\\nFallback diagnosis system completed!")
`;

  try {
    const response = await axios.post(url, { code: codeToRun });
    const data = response.data;
    
    console.log('AIMA3 Test Response:', data);
    
    if (data.success) {
      console.log('Output:\n', data.stdout);
      if (data.stderr) console.log('Errors:\n', data.stderr);
    } else {
      console.error('Execution failed:', data.error);
      console.error('Traceback:', data.traceback);
    }
  } catch (error) {
    if (error.response) {
      console.error('HTTP error:', error.response.status, error.response.statusText);
      console.error('Response data:', error.response.data);
    } else {
      console.error('Request error:', error.message);
    }
  }
}

testAIMA3();