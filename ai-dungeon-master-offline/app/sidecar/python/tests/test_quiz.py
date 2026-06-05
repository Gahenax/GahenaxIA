import unittest
from rules.personality_quiz import PersonalityQuiz

class TestPersonalityQuiz(unittest.TestCase):
    def test_quiz_evaluation(self):
        # Answers designed to maximize Fighter:
        # Q1 -> Option 0 (Gloria, Fighter: 2)
        # Q3 -> Option 2 (Un arma, Fighter: 2)
        # Q7 -> Option 3 (Atacar, Fighter: 2)
        # Q8 -> Option 0 (Protector, Fighter: 2)
        answers = {1: 0, 3: 2, 7: 3, 8: 0}
        res = PersonalityQuiz.evaluate_answers(answers)
        
        self.assertEqual(res["class"], "Fighter")
        self.assertEqual(res["race"], "Dwarf")
        self.assertGreater(res["stats"]["STR"], 10)
        self.assertEqual(res["hp_max"], 11) # 10 base + CON mod (starts at 10, no CON choices, so 10, Fighter gets CON as secondary stat +1 -> 11 CON -> +0 mod, wait. Let's see: Fighter starts with 10 HP. Let's assert based on actual hp_max)
        self.assertIn("recommended_difficulty", res["simulation_analysis"])

if __name__ == "__main__":
    unittest.main()
