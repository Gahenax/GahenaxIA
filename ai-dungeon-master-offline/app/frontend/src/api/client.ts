import { invoke } from "@tauri-apps/api/core";

export async function processAction(payload: { action_type: string; description: string; character_id: string }) {
  try {
    const res = await invoke<any>("process_turn", {
      campaignId: "default_campaign",
      characterId: payload.character_id,
      textInput: payload.description,
      audioBytes: null
    });
    
    return {
      success: true,
      message: "Turn processed",
      narrative: res.narrative || "La mazmorra permanece en silencio...",
      game_state: {
        hp: res.hp_current || 10,
        maxHp: res.hp_max || 10,
        ac: res.armor_class || 10,
        level: res.level || 1
      }
    };
  } catch (error) {
    console.error("Action error:", error);
    throw error;
  }
}

export async function rollDice(notation: string) {
  return {
    formula: notation,
    rolls: [10],
    modifier: 0,
    total: 10
  };
}
