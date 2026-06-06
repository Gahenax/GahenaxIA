import { invoke } from "@tauri-apps/api/core";

export async function processAction(payload: { action_type: string; description: string; character_id: string }) {
  try {
    const res = await invoke<any>("process_turn", {
      campaignId: "default_campaign",
      characterId: payload.character_id,
      textInput: payload.description,
      audioBytes: null
    });
    
    // Parse damage to player from mechanics text if available
    let enemy_damage_to_player = 0;
    if (res.mechanics) {
      const match = res.mechanics.match(/(?:Sufres|daño).*?(\d+)/i);
      if (match) {
        enemy_damage_to_player = parseInt(match[1], 10);
      }
    }
    
    return {
      success: true,
      message: "Turn processed",
      narrative: res.narrative || "La mazmorra permanece en silencio...",
      state: {
        enemy_damage_to_player,
        xp: res.xp_gained || 0,
        room: `Sala (${res.coordinates?.x || 2}, ${res.coordinates?.y || 4})`
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
