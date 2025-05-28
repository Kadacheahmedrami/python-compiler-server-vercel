from aima3.logic import FolKB, expr, fol_fc_ask, fol_bc_ask

# Let's create our medical diagnosis system
medical_kb = FolKB()

# Adding my patients data - everyone came in with different symptoms
# Ahmad came in with flu-like symptoms
medical_kb.tell(expr("Fever(Ahmad)"))
medical_kb.tell(expr("Cough(Ahmad)"))
medical_kb.tell(expr("SoreThroat(Ahmad)"))

# Fatima has some strange skin issues and joint pain
medical_kb.tell(expr("Fatigue(Fatima)"))
medical_kb.tell(expr("Rash(Fatima)"))
medical_kb.tell(expr("JointPain(Fatima)"))

# Leila is having breathing problems - really concerning
medical_kb.tell(expr("ShortnessOfBreath(Leila)"))
medical_kb.tell(expr("ChestPain(Leila)"))
medical_kb.tell(expr("Cough(Leila)"))

# Omar came in with bad headache
medical_kb.tell(expr("Headache(Omar)"))
medical_kb.tell(expr("Fever(Omar)"))
medical_kb.tell(expr("Fatigue(Omar)"))

# Youssef has stomach issues
medical_kb.tell(expr("Nausea(Youssef)"))
medical_kb.tell(expr("Vomiting(Youssef)"))
medical_kb.tell(expr("AbdominalPain(Youssef)"))

# My diagnostic rules based on medical textbooks
# Classic flu symptoms
medical_kb.tell(expr("Fever(x) & Cough(x) ==> HasFlu(x)"))

# Strep needs the sore throat with fever
medical_kb.tell(expr("Fever(x) & Cough(x) & SoreThroat(x) ==> HasStrepThroat(x)"))

# These breathing symptoms usually indicate pneumonia
medical_kb.tell(expr("ShortnessOfBreath(x) & ChestPain(x) ==> HasPneumonia(x)"))

# Rash with joint pain is classic for Lyme
medical_kb.tell(expr("Rash(x) & JointPain(x) ==> HasLymeDisease(x)"))

# Basic gastro diagnosis
medical_kb.tell(expr("Nausea(x) & Vomiting(x) ==> HasGastroenteritis(x)"))

# Need to watch for meningitis with these symptoms
medical_kb.tell(expr("Headache(x) & Fever(x) ==> HasMeningitis(x)"))

# Mono often presents like this
medical_kb.tell(expr("Fatigue(x) & Fever(x) ==> HasMononucleosis(x)"))

# Bronchitis diagnosis
medical_kb.tell(expr("Cough(x) & ShortnessOfBreath(x) ==> HasBronchitis(x)"))

# Run forward chaining to see what illnesses our patients might have
def find_diagnoses(kb):
    print("Possible diagnoses based on symptoms:")
    
    # All the conditions we can diagnose
    possible_conditions = [
        "HasFlu", "HasStrepThroat", "HasPneumonia", "HasLymeDisease",
        "HasGastroenteritis", "HasMeningitis", "HasMononucleosis", "HasBronchitis"
    ]
    
    # Check each condition
    for condition in possible_conditions:
        query = expr(f"{condition}(x)")
        matches = fol_fc_ask(kb, query)
        
        for match in matches:
            if 'x' in match:
                patient_name = match['x']
                # Strip the "Has" prefix for readability
                condition_name = condition[3:] 
                print(f"{patient_name} likely has {condition_name}")

# Check a specific diagnosis with backward chaining
def verify_diagnosis(kb, patient_name, disease):
    print(f"\nIs {patient_name} likely to have {disease}?")
    query = expr(f"Has{disease}({patient_name})")
    evidence = list(fol_bc_ask(kb, query))
    
    if evidence:
        print(f"Yes - {patient_name}'s symptoms match {disease}")
    else:
        print(f"No - {patient_name} probably doesn't have {disease}")

# Let's diagnose our patients
find_diagnoses(medical_kb)

# Double-check some specific cases
verify_diagnosis(medical_kb, "Ahmad", "StrepThroat")
verify_diagnosis(medical_kb, "Leila", "Pneumonia")
verify_diagnosis(medical_kb, "Omar", "Flu")
verify_diagnosis(medical_kb, "Youssef", "Meningitis")  # This one shouldn't match
