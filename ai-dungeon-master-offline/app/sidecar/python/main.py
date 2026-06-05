import os
import sys
import shutil
import uuid

# Force UTF-8 stdout/stderr on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from memory.db_manager import DatabaseManager
from memory.repositories import CampaignRepository, CharacterRepository, MessageRepository
from rules.story_simulator import StorySimulator
from rules.personality_quiz import PersonalityQuiz
from orchestrator import Orchestrator

app = FastAPI(
    title="Cripta Sidecar Server",
    version="1.0",
    default_response_class=JSONResponse
)

# CORS middleware config to allow Tauri app to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and managers
db_manager = DatabaseManager()
campaign_repo = CampaignRepository(db_manager)
character_repo = CharacterRepository(db_manager)
message_repo = MessageRepository(db_manager)
orchestrator = Orchestrator(db_manager)

class CampaignCreate(BaseModel):
    name: str
    system: str
    tone: str

from pydantic import BaseModel, Field

class CharacterCreate(BaseModel):
    campaign_id: str
    name: str
    char_class: str = Field(..., alias="class")
    race: str
    background: str
    hp_max: int
    armor_class: int
    stats: Dict[str, int]
    inventory: Dict[str, Any]

    model_config = {
        "populate_by_name": True
    }

class TurnRequest(BaseModel):
    campaign_id: str
    character_id: str
    text_input: Optional[str] = None

class RollbackRequest(BaseModel):
    page_number: int

@app.get("/status")
def get_status():
    """Returns diagnostics of local dependencies."""
    ollama_ok = orchestrator.ollama.is_available()
    return {
        "status": "online",
        "ollama_available": ollama_ok,
        "ollama_model": orchestrator.ollama.default_model,
        "whisper_available": (orchestrator.whisper.python_model is not None) or os.path.exists(orchestrator.whisper.binary_path),
        "piper_binary_exists": os.path.exists(orchestrator.piper.binary_path)
    }

@app.get("/model/status")
def get_model_status():
    """Returns the currently active Ollama model and all installed models."""
    import requests as req
    active_model = orchestrator.ollama.default_model
    installed = []
    try:
        res = req.get(f"{orchestrator.ollama.host}/api/tags", timeout=2.0)
        if res.status_code == 200:
            installed = [m.get("name") for m in res.json().get("models", [])]
    except Exception:
        pass
    return {
        "active_model": active_model,
        "installed_models": installed,
        "is_qwen25": active_model.startswith("qwen2.5")
    }

@app.post("/campaigns")
def create_campaign(campaign: CampaignCreate):
    return campaign_repo.create(campaign.name, campaign.system, campaign.tone)

@app.get("/campaigns")
def list_campaigns():
    return campaign_repo.list_all()

@app.post("/characters")
def create_character(char: CharacterCreate):
    existing = character_repo.get_by_campaign(char.campaign_id)
    if len(existing) >= 6:
        raise HTTPException(status_code=400, detail="La campaña ya tiene el límite máximo de 6 personajes.")
    return character_repo.create(
        char.campaign_id, char.name, char.char_class, char.race, char.background,
        char.hp_max, char.armor_class, char.stats, char.inventory
    )

@app.get("/campaigns/{campaign_id}/characters")
def list_characters(campaign_id: str):
    return character_repo.get_by_campaign(campaign_id)

@app.get("/campaigns/{campaign_id}/history")
def get_campaign_history(campaign_id: str, limit: int = 20):
    """Returns the narrative history for a campaign."""
    return message_repo.get_recent_history(campaign_id, limit=limit)

@app.get("/campaigns/{campaign_id}/pages")
def get_campaign_pages(campaign_id: str):
    """Returns all aggregated pages of the campaign book."""
    return message_repo.get_pages(campaign_id)

@app.get("/campaigns/{campaign_id}/map")
def get_campaign_map(campaign_id: str):
    """Returns the generated procedural dungeon map."""
    from rules.map_generator import ProceduralDungeon
    dungeon = ProceduralDungeon(campaign_id)
    return dungeon.serialize()

@app.post("/campaigns/{campaign_id}/rollback")
def rollback_campaign(campaign_id: str, payload: RollbackRequest):
    """Deactivates all campaign pages after the specified page number."""
    try:
        deactivated_count = message_repo.rollback_to_page(campaign_id, payload.page_number)
        return {
            "status": "success",
            "deactivated_pages": deactivated_count,
            "rollback_to": payload.page_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/turn")
def process_turn(request: TurnRequest):
    """Processes a text-only turn."""
    try:
        result = orchestrator.process_player_turn(
            campaign_id=request.campaign_id,
            character_id=request.character_id,
            text_input=request.text_input
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/turn/audio")
async def process_turn_audio(
    campaign_id: str = Form(...),
    character_id: str = Form(...),
    audio: UploadFile = File(...)
):
    """Processes an audio turn."""
    # Temporary save uploaded audio
    temp_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_audio_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{audio.filename}")
    try:
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
            
        result = orchestrator.process_player_turn(
            campaign_id=campaign_id,
            character_id=character_id,
            audio_path=temp_audio_path
        )
        
        # Clean up temp audio file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            
        return result
    except Exception as e:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio")
def get_audio_file(path: str):
    """Serves local WAV file generated by Piper TTS."""
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(path, media_type="audio/wav")

@app.get("/tts")
def synthesize_tts(text: str):
    """Synthesizes arbitrary text using Piper and returns WAV stream."""
    temp_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "temp_tts")
    os.makedirs(temp_dir, exist_ok=True)
    out_path = os.path.join(temp_dir, f"tts_{uuid.uuid4().hex}.wav")
    try:
        orchestrator.piper.synthesize(text, out_path)
        if not os.path.exists(out_path):
            raise HTTPException(status_code=500, detail="Fallo la sintesis de voz.")
        return FileResponse(out_path, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/simulate/story")
def run_story_simulation(
    num_simulations: int = 10000,
    initial_hp: int = 12,
    armor_class: int = 15,
    difficulty: str = "medium"
):
    """Runs a Monte Carlo simulation of story progression for balancing."""
    return StorySimulator.simulate_campaign_paths(
        num_simulations=num_simulations,
        initial_hp=initial_hp,
        armor_class=armor_class,
        difficulty=difficulty
    )

class QuizAnswers(BaseModel):
    answers: Dict[int, int]

@app.get("/quiz/questions")
def get_quiz_questions():
    """Returns the personality quiz questions for character creation."""
    # Hide points to prevent player cheating from the response
    questions_masked = []
    for q in PersonalityQuiz.QUESTIONS:
        options = [{"text": o["text"]} for o in q["options"]]
        questions_masked.append({
            "id": q["id"],
            "question": q["question"],
            "options": options
        })
    return questions_masked

@app.post("/quiz/evaluate")
def evaluate_quiz(payload: QuizAnswers):
    """Evaluates answers and returns character stats, class, and auto-calibrated game difficulty."""
    try:
        return PersonalityQuiz.evaluate_answers(payload.answers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
