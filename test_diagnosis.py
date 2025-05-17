import unittest
from diagnosis_engine import DiagnosisEngine

class TestDiagnosisEngine(unittest.TestCase):
    def setUp(self):
        self.engine = DiagnosisEngine()
        
    def test_calculate_confidence(self):
        # Test with flu symptoms
        symptoms = ["fever", "cough", "sore throat"]
        results = self.engine.calculate_confidence(symptoms)
        self.assertGreaterEqual(results["Flu"], 60)
        
    def test_run_diagnosis(self):
        # Create a symptoms dictionary simulating UI input
        symptoms = {
            "fever": True,
            "cough": True,
            "sore throat": True,
            "fatigue": True,
            "headache": False
        }
        results = self.engine.run_diagnosis(symptoms)
        self.assertTrue(len(results) > 0)
        # Flu should be detected with high confidence
        self.assertEqual(results[0][0], "Flu")
        
if __name__ == "__main__":
    unittest.main()
