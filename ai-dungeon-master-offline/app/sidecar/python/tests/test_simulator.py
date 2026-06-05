import unittest
from rules.story_simulator import StorySimulator

class TestStorySimulator(unittest.TestCase):
    def test_simulation_runs(self):
        res = StorySimulator.simulate_campaign_paths(num_simulations=1000)
        self.assertEqual(res["total_simulations"], 1000)
        self.assertGreaterEqual(res["survival_rate"], 0.0)
        self.assertLessEqual(res["survival_rate"], 1.0)
        self.assertIn("avg_combats_per_run", res)

    def test_difficulty_scaling(self):
        res_easy = StorySimulator.simulate_campaign_paths(num_simulations=500, difficulty="easy")
        res_hard = StorySimulator.simulate_campaign_paths(num_simulations=500, difficulty="hard")
        # Hard mode should generally have higher death rates than easy mode
        self.assertEqual(res_easy["difficulty_level"], "easy")
        self.assertEqual(res_hard["difficulty_level"], "hard")

if __name__ == "__main__":
    unittest.main()
