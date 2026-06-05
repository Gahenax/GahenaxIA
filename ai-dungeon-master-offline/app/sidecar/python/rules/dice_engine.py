import re
import random
from typing import Dict, Any, List

class DiceEngine:
    DICE_REGEX = re.compile(
        r'^\s*(?P<num>\d+)?d(?P<sides>\d+)\s*(?:(?P<mod_sign>[+-])\s*(?P<mod_val>\d+))?\s*$',
        re.IGNORECASE
    )

    @staticmethod
    def roll(formula: str, advantage_mode: str = "normal") -> Dict[str, Any]:
        """
        Rolls dice based on a D&D formula (e.g., '1d20+5', '2d6-1').
        advantage_mode can be: 'normal', 'advantage' (roll 2 d20 and keep highest), 'disadvantage' (keep lowest).
        """
        formula_clean = formula.replace(" ", "").lower()
        match = DiceEngine.DICE_REGEX.match(formula_clean)
        
        if not match:
            # Fallback if parsing fails: assume a simple 1d20 roll
            return DiceEngine._generate_result(1, 20, 0, "+", advantage_mode, formula)

        num = int(match.group("num")) if match.group("num") else 1
        sides = int(match.group("sides"))
        mod_sign = match.group("mod_sign") if match.group("mod_sign") else "+"
        mod_val = int(match.group("mod_val")) if match.group("mod_val") else 0

        return DiceEngine._generate_result(num, sides, mod_val, mod_sign, advantage_mode, formula)

    @staticmethod
    def _generate_result(num: int, sides: int, mod_val: int, mod_sign: str, advantage_mode: str, original_formula: str) -> Dict[str, Any]:
        dice_rolls = []
        
        # In D&D, advantage/disadvantage typically only applies to the primary d20 roll
        if sides == 20 and num == 1 and advantage_mode in ("advantage", "disadvantage"):
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            dice_rolls = [roll1, roll2]
            if advantage_mode == "advantage":
                selected_result = max(roll1, roll2)
                reason = "Advantage (max of {} and {})".format(roll1, roll2)
            else:
                selected_result = min(roll1, roll2)
                reason = "Disadvantage (min of {} and {})".format(roll1, roll2)
        else:
            dice_rolls = [random.randint(1, sides) for _ in range(num)]
            selected_result = sum(dice_rolls)
            reason = "Standard roll"

        modifier = mod_val if mod_sign == "+" else -mod_val
        total = selected_result + modifier

        return {
            "formula": original_formula,
            "rolls": dice_rolls,
            "selected_raw": selected_result,
            "modifier": modifier,
            "total": total,
            "sides": sides,
            "num_dice": num,
            "advantage_mode": advantage_mode,
            "reason": reason,
            "is_critical_hit": selected_result == 20 if sides == 20 else False,
            "is_critical_fail": selected_result == 1 if sides == 20 else False
        }
