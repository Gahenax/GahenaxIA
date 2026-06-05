import random
from typing import Dict, Any, List

class StorySimulator:
    """
    Monte Carlo simulator to evaluate campaign pacing, branching probabilities,
    and character survival rates across procedural storylines.
    """

    @staticmethod
    def simulate_campaign_paths(
        num_simulations: int = 10000,
        initial_hp: int = 12,
        armor_class: int = 15,
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """
        Runs Monte Carlo simulations over procedural story nodes:
        - Exploration (Trap/Puzzle) -> 30% chance
        - Combat (Goblin/Orc fight) -> 40% chance
        - Social / Rest -> 30% chance
        """
        outcomes = {
            "survival_count": 0,
            "death_count": 0,
            "total_combat_encounters": 0,
            "total_traps_encountered": 0,
            "total_rests": 0,
            "hp_remaining_distribution": []
        }

        # Difficulty scaling
        combat_damage_multiplier = 1.0
        if difficulty == "hard":
            combat_damage_multiplier = 1.5
        elif difficulty == "easy":
            combat_damage_multiplier = 0.7

        for _ in range(num_simulations):
            hp = initial_hp
            combat_count = 0
            trap_count = 0
            rest_count = 0
            is_alive = True

            # Simulate a standard 5-room/encounter dungeon arc
            for room in range(5):
                if not is_alive:
                    break

                # Determine room event type procedurally
                event_roll = random.random()
                
                if event_roll < 0.30:
                    # Exploration / Trap Event (DEX Saving Throw DC 12)
                    trap_count += 1
                    dex_save = random.randint(1, 20) + 2 # DEX mod +2
                    if dex_save < 12:
                        damage = random.randint(1, 6) # 1d6 trap damage
                        hp -= damage
                        if hp <= 0:
                            is_alive = False

                elif event_roll < 0.70:
                    # Combat Event (Goblin attack)
                    combat_count += 1
                    # Goblin attack roll: 1d20+4 vs Player AC
                    goblin_hit_roll = random.randint(1, 20) + 4
                    if goblin_hit_roll >= armor_class:
                        damage = int((random.randint(1, 6) + 2) * combat_damage_multiplier) # 1d6+2 damage
                        hp -= damage
                        if hp <= 0:
                            is_alive = False

                else:
                    # Social / Rest event (heals player 1d4 HP)
                    rest_count += 1
                    heal = random.randint(1, 4)
                    hp = min(initial_hp, hp + heal)

            if is_alive:
                outcomes["survival_count"] += 1
                outcomes["hp_remaining_distribution"].append(hp)
            else:
                outcomes["death_count"] += 1

            outcomes["total_combat_encounters"] += combat_count
            outcomes["total_traps_encountered"] += trap_count
            outcomes["total_rests"] += rest_count

        # Compute averages
        total_runs = num_simulations
        avg_hp_remaining = sum(outcomes["hp_remaining_distribution"]) / len(outcomes["hp_remaining_distribution"]) if outcomes["hp_remaining_distribution"] else 0
        
        return {
            "total_simulations": total_runs,
            "survival_rate": outcomes["survival_count"] / total_runs,
            "death_rate": outcomes["death_count"] / total_runs,
            "avg_combats_per_run": outcomes["total_combat_encounters"] / total_runs,
            "avg_traps_per_run": outcomes["total_traps_encountered"] / total_runs,
            "avg_rests_per_run": outcomes["total_rests"] / total_runs,
            "avg_hp_remaining_survivors": avg_hp_remaining,
            "difficulty_level": difficulty
        }
