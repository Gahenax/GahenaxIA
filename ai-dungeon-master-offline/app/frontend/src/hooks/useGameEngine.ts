import { useState, useCallback } from "react";
import { processAction, rollDice } from "../api/client";

interface GameState {
  hp: number;
  maxHp: number;
  ac: number;
  level: number;
  xp?: number;
  room?: string;
}

interface ActionResult {
  success: boolean;
  message: string;
  narrative: string;
  game_state?: GameState;
}

export function useGameEngine() {
  const [gameState, setGameState] = useState<GameState>({
    hp: 10,
    maxHp: 10,
    ac: 10,
    level: 1,
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
        if (result?.game_state) {
          setGameState(prev => ({ ...prev, ...result.game_state }));
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
