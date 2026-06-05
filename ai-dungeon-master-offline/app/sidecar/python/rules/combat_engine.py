import re
from typing import List, Dict, Any, Optional
from rules.dice_engine import DiceEngine

class CombatEngine:
    @staticmethod
    def roll_initiative(combatants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rolls initiative for all combatants and sorts them in descending order.
        Each combatant in list should have:
            - 'id': str
            - 'name': str
            - 'dex_mod': int (DEX modifier for initiative)
            - 'entity_type': 'character' or 'npc'
        """
        active_combatants = []
        for c in combatants:
            roll = DiceEngine.roll("1d20")
            roll_val = roll["selected_raw"]
            dex_mod = c.get("dex_mod", 0)
            total_initiative = roll_val + dex_mod
            
            active_combatants.append({
                "entity_id": c["id"],
                "entity_type": c["entity_type"],
                "name": c["name"],
                "initiative": total_initiative,
                "hp": c.get("hp_current", c.get("hp", 10)),
                "hp_max": c.get("hp_max", 10),
                "status": "alive"
            })
            
        # Sort by initiative descending
        active_combatants.sort(key=lambda x: x["initiative"], reverse=True)
        return active_combatants

    @staticmethod
    def resolve_attack(
        attacker: Dict[str, Any],
        defender: Dict[str, Any],
        weapon: Dict[str, Any],
        advantage_mode: str = "normal"
    ) -> Dict[str, Any]:
        """
        Resolves an attack roll vs Armor Class (AC) and damage.
        attacker needs:
            - 'name': str
            - 'attack_bonus': int (proficiency + STR/DEX modifier)
        defender needs:
            - 'name': str
            - 'armor_class': int
            - 'hp': int
        weapon needs:
            - 'name': str
            - 'damage_formula': str (e.g. '1d8+3')
        """
        attack_bonus = attacker.get("attack_bonus", 0)
        sign = "+" if attack_bonus >= 0 else "-"
        formula = "1d20{}{}".format(sign, abs(attack_bonus))
        
        # Roll attack d20
        attack_roll = DiceEngine.roll(formula, advantage_mode)
        roll_total = attack_roll["total"]
        is_crit = attack_roll["is_critical_hit"]
        is_fail = attack_roll["is_critical_fail"]

        ac = defender.get("armor_class", defender.get("ac", 10))
        
        hit = False
        damage_total = 0
        damage_roll_details = None
        
        if not is_fail:
            if is_crit or roll_total >= ac:
                hit = True
                # Resolve damage
                damage_formula = weapon.get("damage_formula", "1d6")
                
                # Critical hit: D&D typically rolls damage dice twice
                if is_crit:
                    damage_formula = CombatEngine._double_damage_dice(damage_formula)
                    
                damage_roll = DiceEngine.roll(damage_formula)
                damage_total = max(1, damage_roll["total"]) # Damage cannot be less than 1 (or 0 in some cases, D&D minimum is 1)
                damage_roll_details = damage_roll

        new_hp = max(0, defender.get("hp", 10) - damage_total)
        status = "alive"
        if new_hp <= 0:
            status = "dead" if defender.get("entity_type") == "npc" else "unconscious"

        return {
            "attacker": attacker["name"],
            "defender": defender["name"],
            "hit": hit,
            "is_critical": is_crit,
            "attack_roll": attack_roll,
            "damage_total": damage_total,
            "damage_roll": damage_roll_details,
            "defender_prev_hp": defender.get("hp", 10),
            "defender_new_hp": new_hp,
            "defender_status": status,
            "narrative_hint": "Critical hit!" if is_crit else ("Hit" if hit else "Miss")
        }

    @staticmethod
    def _double_damage_dice(formula: str) -> str:
        """Helper to double the dice pool for a critical hit (e.g., '1d8+3' -> '2d8+3')."""
        match = re.match(r'^\s*(\d+)?d(\d+)(.*)$', formula, re.IGNORECASE)
        if match:
            num = int(match.group(1)) if match.group(1) else 1
            sides = match.group(2)
            rest = match.group(3)
            return "{}d{}{}".format(num * 2, sides, rest)
        return formula
