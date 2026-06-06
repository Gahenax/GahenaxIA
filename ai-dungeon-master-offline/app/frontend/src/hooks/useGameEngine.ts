import { useState, useCallback } from "react";
import { processAction, rollDice } from "../api/client";

interface GameState {
  hp: number;
  maxHp: number;
  ac: number;
  level: number;
  xp: number;
  room: string;
}

interface ActionResult {
  success: boolean;
  message: string;
  narrative: string;
  state?: any;
}

export function useGameEngine() {
  const [gameState, setGameState] = useState<GameState>({
    hp: 10,
    maxHp: 10,
    ac: 12,
    level: 1,
    xp: 0,
    room: "Entrada de la Cripta"
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const performAction = useCallback(
    async (actionType: string, description: string): Promise<ActionResult | null> => {
      setLoading(true);
      setError(null);
      try {
        const result = await processAction({
          action_type: actionType,
          description,
          character_id: "player_1",
        });

        if (result?.state) {
          const s = result.state;
          setGameState(prev => ({
            ...prev,
            hp: s.enemy_damage_to_player !== undefined
              ? Math.max(0, prev.hp - (s.enemy_damage_to_player || 0))
              : prev.hp,
            xp: s.xp !== undefined ? s.xp : prev.xp,
            room: s.room || prev.room,
          }));
        }

        return result;
      } catch (err) {
        setError(String(err));
        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const roll = useCallback(async (notation: string) => {
    try {
      return await rollDice(notation);
    } catch (err) {
      setError(String(err));
      return null;
    }
  }, []);

  return { gameState, loading, error, performAction, roll };
}
