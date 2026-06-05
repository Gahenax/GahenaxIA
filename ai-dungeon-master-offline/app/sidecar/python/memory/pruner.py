import json
from typing import List, Dict, Any
from llm.ollama_client import OllamaClient

class ContextPruner:
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client

    def prune_history(self, campaign_id: str, pages: List[Dict[str, Any]]) -> str:
        """
        Takes list of pages and generates a short markdown summary of core events,
        allowing old detailed messages to be pruned/deactivated while keeping the memory alive.
        """
        if len(pages) <= 5:
            return ""

        # Pages to summarize: all except the last 4 pages
        pages_to_summarize = pages[:-4]
        
        # Build raw text to summarize
        summary_input = []
        for page in pages_to_summarize:
            p_num = page["page_number"]
            player = page["player_text"]
            dm = page["dm_text"]
            summary_input.append(f"Página {p_num} - Jugador: {player}\nDM: {dm}")

        raw_history_text = "\n\n".join(summary_input)
        
        prompt = (
            "Eres el cronista del Dungeon Master. Lee los siguientes acontecimientos de una aventura de rol "
            "y escribe un resumen de no más de 3 párrafos en español. Destaca únicamente los logros, "
            "tesoros obtenidos, trampas activadas, daños significativos y enemigos derrotados. Mantén el tono fantástico "
            "pero sé extremadamente conciso.\n\n"
            f"{raw_history_text}\n\n"
            "Resumen de la Crónica:"
        )

        try:
            summary = self.ollama.generate_chat([
                {"role": "system", "content": "Eres un cronista preciso y literario. Resumes historias de rol en español."},
                {"role": "user", "content": prompt}
            ])
            return summary.strip()
        except Exception as e:
            # Fallback local heuristic summary if LLM call fails
            return f"El aventurero exploró varias cámaras de la cripta, resolviendo combates y trampas en el camino."
