class DiagnosisEngine:
    def __init__(self):
        self.result = []
        self.disease_profiles = {
            "Flu": {
                "symptoms": ["fever", "cough", "sore throat", "fatigue", "body aches"],
                "advice": "advice_flu"
            },
            "COVID-19": {
                "symptoms": ["fever", "cough", "shortness of breath", "loss of taste or smell", "fatigue"],
                "advice": "advice_covid"
            },
            "Diabetes": {
                "symptoms": ["frequent urination", "increased thirst", "unexplained weight loss", "extreme hunger"],
                "advice": "advice_diabetes"
            },
            "Hypertension": {
                "symptoms": ["headache", "dizziness", "blurred vision", "chest pain"],
                "advice": "advice_hypertension"
            },
            "Migraine": {
                "symptoms": ["headache", "nausea", "sensitivity to light", "blurred vision"],
                "advice": "advice_migraine"
            },
            # Added more diseases with their symptoms and advice keys
            "Asthma": {
                "symptoms": ["shortness of breath", "cough", "chest pain", "wheezing"],
                "advice": "advice_asthma"
            },
            "Tuberculosis": {
                "symptoms": ["cough", "chest pain", "fever", "night sweats", "unexplained weight loss"],
                "advice": "advice_tuberculosis"
            },
            "Malaria": {
                "symptoms": ["fever", "headache", "fatigue", "body aches", "nausea"],
                "advice": "advice_malaria"
            },
            "Depression": {
                "symptoms": ["fatigue", "sleep disturbance", "loss of interest", "persistent sadness"],
                "advice": "advice_depression"
            },
            "Anxiety": {
                "symptoms": ["excessive worry", "restlessness", "fatigue", "difficulty concentrating"],
                "advice": "advice_anxiety"
            },
            "Arthritis": {
                "symptoms": ["joint pain", "joint stiffness", "swelling", "reduced range of motion"],
                "advice": "advice_arthritis"
            },
            "Gastritis": {
                "symptoms": ["abdominal pain", "nausea", "vomiting", "feeling of fullness"],
                "advice": "advice_gastritis"
            },
            "Pneumonia": {
                "symptoms": ["cough", "fever", "shortness of breath", "chest pain", "fatigue"],
                "advice": "advice_pneumonia"
            },
            "Hepatitis": {
                "symptoms": ["fatigue", "nausea", "abdominal pain", "jaundice", "dark urine"],
                "advice": "advice_hepatitis"
            }
        }

    def calculate_confidence(self, selected_symptoms):
        results = {}
        for disease, profile in self.disease_profiles.items():
            symptoms = profile["symptoms"]
            weight = len(symptoms)  # Weight based on the number of symptoms
            match_count = sum(1 for symptom in selected_symptoms if symptom in symptoms)
            confidence = (match_count / weight) * 100
            results[disease] = round(confidence, 2)
        return results

    def run_diagnosis(self, symptoms):
        self.result.clear()

        input_symptoms = [k for k, v in symptoms.items() if v]
        results = self.calculate_confidence(input_symptoms)
        
        for disease, confidence in results.items():
            if confidence >= 50:
                advice = self.disease_profiles[disease]["advice"]
                self.result.append((disease, confidence, advice))

        return sorted(self.result, key=lambda x: x[1], reverse=True)
