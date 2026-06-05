import unittest
import unittest.mock
from rules.dice_engine import DiceEngine
from rules.combat_engine import CombatEngine

class TestDndEngines(unittest.TestCase):
    def test_dice_roll_parsing(self):
        # Test standard parsing
        res = DiceEngine.roll("1d20+5")
        self.assertEqual(res["num_dice"], 1)
        self.assertEqual(res["sides"], 20)
        self.assertEqual(res["modifier"], 5)
        self.assertEqual(len(res["rolls"]), 1)
        
        # Test negative modifier
        res = DiceEngine.roll("2d6 - 2")
        self.assertEqual(res["num_dice"], 2)
        self.assertEqual(res["sides"], 6)
        self.assertEqual(res["modifier"], -2)
        self.assertEqual(len(res["rolls"]), 2)

    def test_advantage_rolls(self):
        res = DiceEngine.roll("1d20+3", advantage_mode="advantage")
        self.assertEqual(res["num_dice"], 1)
        self.assertEqual(res["sides"], 20)
        self.assertEqual(len(res["rolls"]), 2)
        self.assertEqual(res["selected_raw"], max(res["rolls"]))

    def test_double_dice_critical(self):
        doubled = CombatEngine._double_damage_dice("1d8+3")
        self.assertEqual(doubled, "2d8+3")
        
        doubled_none = CombatEngine._double_damage_dice("2d10-1")
        self.assertEqual(doubled_none, "4d10-1")

    @unittest.mock.patch("rules.dice_engine.DiceEngine.roll")
    def test_combat_resolution_hit(self, mock_roll):
        mock_roll.side_effect = [
            {
                "total": 15,
                "is_critical_hit": False,
                "is_critical_fail": False,
                "rolls": [10],
                "selected_raw": 10
            },
            {
                "total": 5,
                "rolls": [2],
                "sides": 8,
                "modifier": 3
            }
        ]
        attacker = {"name": "Warrior", "attack_bonus": 5}
        defender = {"name": "Goblin", "armor_class": 0, "hp": 10, "entity_type": "npc"}
        weapon = {"name": "Longsword", "damage_formula": "1d8+3"}
        
        res = CombatEngine.resolve_attack(attacker, defender, weapon)
        self.assertTrue(res["hit"])
        self.assertEqual(res["damage_total"], 5)
        self.assertEqual(res["defender_new_hp"], 5)

if __name__ == "__main__":
    unittest.main()
