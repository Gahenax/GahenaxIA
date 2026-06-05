import React, { useState, useEffect, useRef } from 'react';
import './index.css';

interface Campaign {
  id: string;
  name: string;
  system: string;
  tone: string;
}

interface Character {
  id: string;
  name: string;
  class: string;
  race: string;
  hp_current: number;
  hp_max: number;
  armor_class: number;
}


function App() {
  // Navigation & Setup State
  const [status, setStatus] = useState<any>(null);
  const [modelInfo, setModelInfo] = useState<{active_model: string, is_qwen25: boolean} | null>(null);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [characterXP, setCharacterXP] = useState<{xp: number, level: number}>({xp: 0, level: 1});
  
  // Creation Modals State
  const [newCampaignName, setNewCampaignName] = useState('');
  const [newCampaignTone, setNewCampaignTone] = useState('Epic & Dark Fantasy');
  const [newCharName, setNewCharName] = useState('');
  const [newCharClass, setNewCharClass] = useState('Fighter');
  const [newCharRace, setNewCharRace] = useState('Human');

  // Quiz State
  const [quizMode, setQuizMode] = useState(false);
  const [manualMode, setManualMode] = useState(false);
  const [quizQuestions, setQuizQuestions] = useState<any[]>([]);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [quizAnswers, setQuizAnswers] = useState<Record<number, number>>({});
  const [quizResult, setQuizResult] = useState<any>(null);

  // Game Board State (Infinite Book & Random RPG Generator amalgamation)
  const [bookPages, setBookPages] = useState<any[]>([]);
  const [currentPageIdx, setCurrentPageIdx] = useState(0);
  const [dungeonMap, setDungeonMap] = useState<any[]>([]);
  const [playerCoords, setPlayerCoords] = useState<{x: number, y: number}>({x: 2, y: 4});
  const [showDecisionTree, setShowDecisionTree] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [diceRollResult, setDiceRollResult] = useState<any>(null);

  // Audio Recording references
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    fetchStatus();
    fetchModelInfo();
    fetchCampaigns();

    // Initialize Web Speech API for native local browser transcription
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.lang = 'es-ES';
      rec.interimResults = false;

      rec.onresult = async (event: any) => {
        const transcript = event.results[0][0].transcript;
        console.log("Speech recognition transcript:", transcript);
        if (transcript) {
          // Auto submit
          submitPlayerAction(transcript);
        }
      };

      rec.onend = () => {
        setIsRecording(false);
      };

      rec.onerror = (e: any) => {
        console.error("Speech recognition error", e);
        setIsRecording(false);
      };

      recognitionRef.current = rec;
    }
  }, []);

  const startQuiz = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/quiz/questions');
      const data = await res.json();
      setQuizQuestions(data);
      setCurrentQuestionIdx(0);
      setQuizAnswers({});
      setQuizResult(null);
      setQuizMode(true);
      setManualMode(false);
    } catch (e) {
      console.error(e);
    }
  };

  const handleAnswerQuizQuestion = async (optIdx: number) => {
    const questionId = quizQuestions[currentQuestionIdx].id;
    const newAnswers = { ...quizAnswers, [questionId]: optIdx };
    setQuizAnswers(newAnswers);

    if (currentQuestionIdx + 1 < quizQuestions.length) {
      setCurrentQuestionIdx(currentQuestionIdx + 1);
    } else {
      // Evaluate quiz!
      try {
        setIsProcessing(true);
        const res = await fetch('http://127.0.0.1:8000/quiz/evaluate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ answers: newAnswers })
        });
        const data = await res.json();
        setQuizResult(data);
        setNewCharClass(data.class);
        setNewCharRace(data.race);
      } catch (e) {
        console.error(e);
      } finally {
        setIsProcessing(false);
      }
    }
  };

  const handleConfirmQuizCharacter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCampaign || !newCharName || !quizResult) return;
    try {
      const res = await fetch('http://127.0.0.1:8000/characters', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          campaign_id: selectedCampaign.id,
          name: newCharName,
          class: quizResult.class,
          race: quizResult.race,
          background: quizResult.background,
          hp_max: quizResult.hp_max,
          armor_class: quizResult.armor_class,
          stats: quizResult.stats,
          inventory: { gold: 15, items: ["Espada corta", "Raciones", "Parchamento"] }
        })
      });
      if (!res.ok) {
        const errData = await res.json();
        alert(errData.detail || "Error al crear personaje");
        return;
      }
      const data = await res.json();
      setCharacters([data, ...characters]);
      setSelectedCharacter(data);
      setNewCharName('');
      setQuizMode(false);
      setQuizResult(null);
    } catch (e) {
      console.error(e);
    }
  };


  const fetchStatus = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/status');
      const data = await res.json();
      setStatus(data);
    } catch (e) {
      console.error("Backend offline", e);
    }
  };

  const fetchModelInfo = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/model/status');
      if (res.ok) {
        const data = await res.json();
        setModelInfo(data);
      }
    } catch (e) {
      console.error("Model status check failed", e);
    }
  };

  const fetchCampaigns = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/campaigns');
      const data = await res.json();
      setCampaigns(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateCampaign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCampaignName) return;
    try {
      const res = await fetch('http://127.0.0.1:8000/campaigns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newCampaignName, system: 'D&D 5.5 (2024)', tone: newCampaignTone })
      });
      const data = await res.json();
      setCampaigns([data, ...campaigns]);
      setSelectedCampaign(data);
      setNewCampaignName('');
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateCharacter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCampaign || !newCharName) return;
    try {
      const res = await fetch('http://127.0.0.1:8000/characters', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          campaign_id: selectedCampaign.id,
          name: newCharName,
          char_class: newCharClass,
          race: newCharRace,
          background: 'Outlander',
          hp_max: 12,
          armor_class: 15,
          stats: { STR: 16, DEX: 14, CON: 15, INT: 10, WIS: 12, CHA: 8 },
          inventory: { gold: 15, items: ["Iron Sword", "Shield", "Parchment Map"] }
        })
      });
      if (!res.ok) {
        const errData = await res.json();
        alert(errData.detail || "Error al crear personaje");
        return;
      }
      const data = await res.json();
      setCharacters([data, ...characters]);
      setSelectedCharacter(data);
      setNewCharName('');
    } catch (e) {
      console.error(e);
    }
  };

  const fetchCharacters = async (campId: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/campaigns/${campId}/characters`);
      const data = await res.json();
      setCharacters(data);
      if (data.length > 0) {
        setSelectedCharacter(data[0]);
      } else {
        setSelectedCharacter(null);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchPages = async (campId: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/campaigns/${campId}/pages`);
      const data = await res.json();
      if (data && data.length > 0) {
        setBookPages(data);
        setCurrentPageIdx(data.length - 1);
        const lastPage = data[data.length - 1];
        setPlayerCoords(lastPage.coordinates || { x: 2, y: 4 });
      } else {
        const initialPage = {
          page_number: 1,
          player_text: "",
          dm_text: "El portal de piedra se cierra a tus espaldas con un eco ensordecedor. El aire de la cripta es helado y húmedo. Te encuentras en la entrada, sosteniendo tu antorcha. ¿Qué deseas hacer?",
          coordinates: { x: 2, y: 4 },
          choices: ["Moverse al Norte", "Moverse al Sur", "Moverse al Este", "Moverse al Oeste", "Registrar la habitación"],
          mechanics: ""
        };
        setBookPages([initialPage]);
        setCurrentPageIdx(0);
        setPlayerCoords({ x: 2, y: 4 });
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchMap = async (campId: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/campaigns/${campId}/map`);
      const data = await res.json();
      setDungeonMap(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSelectCampaign = (camp: Campaign) => {
    setSelectedCampaign(camp);
    setQuizMode(false);
    setManualMode(false);
    setQuizResult(null);
    fetchCharacters(camp.id);
    fetchPages(camp.id);
    fetchMap(camp.id);
  };

  const submitPlayerAction = async (text: string) => {
    if (!selectedCampaign || !selectedCharacter || isProcessing) return;
    setIsProcessing(true);

    try {
      const res = await fetch('http://127.0.0.1:8000/turn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          campaign_id: selectedCampaign.id,
          character_id: selectedCharacter.id,
          text_input: text
        })
      });
      const data = await res.json();
      
      const newPage = {
        page_number: data.page_number,
        player_text: data.player_text,
        dm_text: data.narrative,
        coordinates: data.coordinates,
        choices: data.choices,
        mechanics: data.mechanics
      };

      setBookPages((prev) => {
        const updated = [...prev];
        const existingIdx = updated.findIndex(p => p.page_number === data.page_number);
        if (existingIdx >= 0) {
          updated[existingIdx] = newPage;
        } else {
          updated.push(newPage);
        }
        return updated;
      });

      setCurrentPageIdx(data.page_number - 1);
      setPlayerCoords(data.coordinates);
      
      if (data.xp_gained && data.xp_gained > 0) {
        setCharacterXP(prev => ({ xp: prev.xp + data.xp_gained, level: prev.level }));
      }

      if (data.roll) {
        setDiceRollResult(data.roll);
      }
      
      if (data.audio_file) {
        const url = `http://127.0.0.1:8000/audio?path=${encodeURIComponent(data.audio_file)}`;
        setAudioUrl(url);
        const audio = new Audio(url);
        audio.play().catch(err => console.error("Audio autoplay failed:", err));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const playPageTTS = async (text: string) => {
    if (!text || isProcessing) return;
    try {
      setIsProcessing(true);
      const url = `http://127.0.0.1:8000/tts?text=${encodeURIComponent(text)}`;
      const audio = new Audio(url);
      await audio.play();
    } catch (e) {
      console.error("TTS playback failed", e);
    } finally {
      setIsProcessing(false);
    }
  };

  // Text Turn Submission
  const handleSendText = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!textInput || isProcessing) return;

    const playerMsg = textInput;
    setTextInput('');
    await submitPlayerAction(playerMsg);
  };

  const handleRollback = async (pageNumber: number) => {
    if (!selectedCampaign || isProcessing) return;
    if (!window.confirm(`¿Estás seguro de que quieres viajar en el tiempo a la Página ${pageNumber}? Las decisiones posteriores se desactivarán.`)) return;
    setIsProcessing(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/campaigns/${selectedCampaign.id}/rollback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ page_number: pageNumber })
      });
      if (res.ok) {
        await fetchPages(selectedCampaign.id);
        setShowDecisionTree(false);
      }
    } catch (e) {
      console.error("Rollback failed", e);
    } finally {
      setIsProcessing(false);
    }
  };

  // Voice recording handlers
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await uploadAudio(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access denied", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const uploadAudio = async (blob: Blob) => {
    if (!selectedCampaign || !selectedCharacter) return;
    setIsProcessing(true);

    const formData = new FormData();
    formData.append('campaign_id', selectedCampaign.id);
    formData.append('character_id', selectedCharacter.id);
    formData.append('audio', blob, 'turn_audio.wav');

    try {
      const res = await fetch('http://127.0.0.1:8000/turn/audio', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();

      const newPage = {
        page_number: data.page_number,
        player_text: data.player_text,
        dm_text: data.narrative,
        coordinates: data.coordinates,
        choices: data.choices,
        mechanics: data.mechanics
      };

      setBookPages((prev) => {
        const updated = [...prev];
        const existingIdx = updated.findIndex(p => p.page_number === data.page_number);
        if (existingIdx >= 0) {
          updated[existingIdx] = newPage;
        } else {
          updated.push(newPage);
        }
        return updated;
      });

      setCurrentPageIdx(data.page_number - 1);
      setPlayerCoords(data.coordinates);

      if (data.roll) {
        setDiceRollResult(data.roll);
      }

      if (data.audio_file) {
        const url = `http://127.0.0.1:8000/audio?path=${encodeURIComponent(data.audio_file)}`;
        setAudioUrl(url);
        const audio = new Audio(url);
        audio.play().catch(err => console.error("Audio autoplay failed:", err));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header & Status Panel */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--color-gold-dim)', paddingBottom: '15px' }}>
        <div>
          <h1 style={{ fontFamily: 'var(--font-serif-dec)', color: 'var(--color-gold)', margin: 0, fontSize: '32px' }}>CRIPTA</h1>
          <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>Dungeon Master Virtual Offline</span>
        </div>
        <div style={{ display: 'flex', gap: '15px', fontSize: '13px', alignItems: 'center' }}>
          {modelInfo && (
            <span style={{
              display: 'inline-flex', alignItems: 'center', gap: '5px',
              padding: '3px 10px', borderRadius: '12px',
              backgroundColor: modelInfo.is_qwen25 ? 'rgba(139, 92, 246, 0.2)' : 'rgba(59, 130, 246, 0.2)',
              border: `1px solid ${modelInfo.is_qwen25 ? '#8b5cf6' : '#3b82f6'}`,
              fontSize: '11px', fontFamily: 'monospace', color: modelInfo.is_qwen25 ? '#c4b5fd' : '#93c5fd'
            }}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '13px', height: '13px', display: 'inline-block', verticalAlign: 'middle', marginRight: '4px' }}>
                <rect x="4" y="4" width="16" height="16" rx="2" />
                <path d="M9 9h6v6H9z" />
                <path d="M9 1v3" />
                <path d="M15 1v3" />
                <path d="M9 20v3" />
                <path d="M15 20v3" />
                <path d="M20 9h3" />
                <path d="M20 15h3" />
                <path d="M1 9h3" />
                <path d="M1 15h3" />
              </svg>
              {modelInfo.active_model}
            </span>
          )}
          {status ? (
            <>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#22c55e' }}></span>
                Backend Online 
                {audioUrl ? (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '14px', height: '14px', display: 'inline-block', verticalAlign: 'middle', marginLeft: '5px' }}>
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                    <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" />
                  </svg>
                ) : ''}
              </span>
              <span>Ollama: {status.ollama_available ? 'Conectado' : 'Desconectado'}</span>
              <span>Whisper: {status.whisper_available ? 'Listo' : 'Simulador'}</span>
              <span>Piper: {status.piper_binary_exists ? 'Listo' : 'Simulador'}</span>
            </>
          ) : (
            <span style={{ color: '#ef4444' }}>Backend Desconectado</span>
          )}
        </div>
      </header>
      {/* Main Campaign Selector / Lobby */}
      {!selectedCampaign ? (
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '30px', marginTop: '40px' }}>
          <div className="medieval-border" style={{ padding: '20px', backgroundColor: 'var(--color-stone-medium)' }}>
            <h2 style={{ fontFamily: 'var(--font-serif)', color: 'var(--color-gold)' }}>Seleccionar Campaña</h2>
            {campaigns.length === 0 ? (
              <p style={{ color: 'var(--color-text-muted)' }}>No hay campañas guardadas. Crea una nueva a la derecha.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {campaigns.map((camp) => (
                  <li key={camp.id} style={{ margin: '10px 0' }}>
                    <button
                      className="btn-medieval"
                      style={{ width: '100%', padding: '15px', textAlign: 'left', display: 'flex', justifyContent: 'space-between' }}
                      onClick={() => handleSelectCampaign(camp)}
                    >
                      <span>{camp.name}</span>
                      <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>{camp.tone}</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="medieval-border" style={{ padding: '20px', backgroundColor: 'var(--color-stone-medium)' }}>
            <h2 style={{ fontFamily: 'var(--font-serif)', color: 'var(--color-gold)' }}>Nueva Gesta</h2>
            <form onSubmit={handleCreateCampaign}>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px' }}>Nombre de la Campaña</label>
                <input
                  type="text"
                  value={newCampaignName}
                  onChange={(e) => setNewCampaignName(e.target.value)}
                  style={{ width: '100%', padding: '10px', backgroundColor: 'var(--color-stone-light)', border: '1px solid var(--color-gold-dim)', color: '#fff' }}
                  placeholder="La Cripta del Orco"
                />
              </div>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px' }}>Tono narrativo</label>
                <select
                  value={newCampaignTone}
                  onChange={(e) => setNewCampaignTone(e.target.value)}
                  style={{ width: '100%', padding: '10px', backgroundColor: 'var(--color-stone-light)', border: '1px solid var(--color-gold-dim)', color: '#fff' }}
                >
                  <option>Epic & Dark Fantasy</option>
                  <option>High Fantasy Comedy</option>
                  <option>Grimdark & Gritty</option>
                </select>
              </div>
              <button type="submit" className="btn-medieval" style={{ width: '100%', padding: '12px' }}>Crear Campaña</button>
            </form>
          </div>
        </div>
      ) : (
        /* Game Board Layout - Amalgamated Infinite Book & Random RPG Generator */
        <div style={{ marginTop: '20px' }}>
          {/* Top Info Bar */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <span style={{ fontSize: '14px', color: 'var(--color-text-muted)' }}>
              Campaña: <strong style={{ color: 'var(--color-gold)', fontFamily: 'var(--font-serif)' }}>{selectedCampaign.name}</strong>
            </span>
            <button className="btn-medieval" style={{ padding: '6px 15px', fontSize: '12px' }} onClick={() => setSelectedCampaign(null)}>
              Volver al Lobby
            </button>
          </div>

          <div className="book-container">
            <div className="book-spine"></div>

            {/* PAGE LEFT: Narrative, History and Text */}
            <div className="book-page-left">
              <div className="book-page-header">
                <span>{selectedCampaign.name}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  {bookPages[currentPageIdx] && (
                    <button 
                      onClick={() => playPageTTS(bookPages[currentPageIdx].dm_text)}
                      className="btn-medieval"
                      style={{ padding: '2px 8px', fontSize: '10px', textTransform: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}
                      title="Escuchar Narración"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '12px', height: '12px' }}>
                        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                        <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" />
                      </svg>
                      Escuchar
                    </button>
                  )}
                  <span>Página {currentPageIdx + 1} de {bookPages.length}</span>
                </div>
              </div>

              {bookPages[currentPageIdx] && (
                <div style={{ minHeight: '400px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    {bookPages[currentPageIdx].player_text && (
                      <div style={{ 
                        fontStyle: 'italic', 
                        color: 'rgba(30, 29, 26, 0.6)', 
                        marginBottom: '20px',
                        borderLeft: '3px solid var(--color-gold-dim)',
                        paddingLeft: '12px',
                        fontSize: '14px'
                      }}>
                        &ldquo;{bookPages[currentPageIdx].player_text}&rdquo;
                      </div>
                    )}
                    
                    <div style={{ 
                      fontSize: '17px', 
                      lineHeight: '1.6', 
                      fontFamily: 'var(--font-readable)',
                      color: '#1a1815',
                      whiteSpace: 'pre-line'
                    }}>
                      {bookPages[currentPageIdx].dm_text}
                    </div>

                    {bookPages[currentPageIdx].mechanics && (
                      <div style={{ 
                        marginTop: '25px', 
                        padding: '10px 15px',
                        backgroundColor: 'rgba(140, 110, 51, 0.08)',
                        borderRadius: '4px',
                        fontSize: '12px', 
                        fontFamily: 'monospace', 
                        color: '#5a4a35',
                        border: '1px solid rgba(140, 110, 51, 0.15)'
                      }}>
                        <strong>
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '14px', height: '14px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
                            <circle cx="12" cy="12" r="3" />
                            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
                          </svg>
                          Mecánicas:
                        </strong> {bookPages[currentPageIdx].mechanics}
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="book-page-footer">
                <button 
                  className="btn-medieval" 
                  style={{ padding: '3px 10px', fontSize: '11px', textTransform: 'none' }}
                  disabled={currentPageIdx === 0}
                  onClick={() => setCurrentPageIdx(idx => Math.max(0, idx - 1))}
                >
                  &larr; Página Anterior
                </button>
                <span style={{ fontSize: '13px' }}>~ {currentPageIdx + 1} ~</span>
                <button 
                  className="btn-medieval" 
                  style={{ padding: '3px 10px', fontSize: '11px', textTransform: 'none' }}
                  disabled={currentPageIdx === bookPages.length - 1}
                  onClick={() => setCurrentPageIdx(idx => Math.min(bookPages.length - 1, idx + 1))}
                >
                  Página Siguiente &rarr;
                </button>
              </div>
            </div>

            {/* PAGE RIGHT: Map, Controls, Choices & Characters */}
            <div className="book-page-right">
              <div className="book-page-header">
                <span>El Destino del Héroe</span>
                <span>Exploración</span>
              </div>
              {/* Navigation Tabs (Map vs Decision Tree) */}
              <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                <button
                  className="btn-medieval"
                  style={{ 
                    flex: 1, 
                    padding: '8px', 
                    fontSize: '11px',
                    backgroundColor: !showDecisionTree ? 'var(--color-gold-dim)' : '#f7eed7',
                    color: !showDecisionTree ? '#fff' : '#5a4a35'
                  }}
                  onClick={() => setShowDecisionTree(false)}
                >
                  Ver Mapa
                </button>
                <button
                  className="btn-medieval"
                  style={{ 
                    flex: 1, 
                    padding: '8px', 
                    fontSize: '11px',
                    backgroundColor: showDecisionTree ? 'var(--color-gold-dim)' : '#f7eed7',
                    color: showDecisionTree ? '#fff' : '#5a4a35'
                  }}
                  onClick={() => setShowDecisionTree(true)}
                >
                  Árbol de Decisiones
                </button>
              </div>

              {/* Side-by-side Layout or Decision Tree on the right page */}
              {!showDecisionTree ? (
                <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '20px', marginBottom: '20px' }}>
                  {/* Procedural Map */}
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontFamily: 'var(--font-serif)', fontSize: '11px', color: '#8c6e33', marginBottom: '8px', letterSpacing: '1px' }}>
                      MAPA PROCEDURAL (REJILLA)
                    </div>
                    <div className="dungeon-map-grid">
                      {Array.from({ length: 5 }).map((_, yIdx) => (
                        Array.from({ length: 5 }).map((_, xIdx) => {
                          const isCurrent = playerCoords.x === xIdx && playerCoords.y === yIdx;
                          const isVisited = bookPages.some(p => p.coordinates && p.coordinates.x === xIdx && p.coordinates.y === yIdx);
                          const roomInfo = dungeonMap.find(r => r.x === xIdx && r.y === yIdx);

                          let symbol = "";
                          if (isVisited && roomInfo) {
                            if (roomInfo.type === "start") symbol = "IN";
                            else if (roomInfo.type === "boss") symbol = "BS";
                            else if (roomInfo.type === "combat") symbol = "CBT";
                            else if (roomInfo.type === "trap") symbol = "TRP";
                            else if (roomInfo.type === "loot") symbol = "Loot";
                            else symbol = ".";
                          }

                          return (
                            <div
                              key={`${xIdx}-${yIdx}`}
                              className={`dungeon-map-cell ${isCurrent ? 'current' : isVisited ? 'visited' : 'unvisited'}`}
                              style={{ fontSize: '10px', fontFamily: 'monospace', fontWeight: 'bold' }}
                              title={isVisited && roomInfo ? `${roomInfo.name} (${roomInfo.type})` : 'Sin explorar'}
                              onClick={() => {
                                if (isVisited && roomInfo) {
                                  alert(`Habitación: ${roomInfo.name}\nTipo: ${roomInfo.type}\nDescripción: ${roomInfo.description}`);
                                }
                              }}
                            >
                              {isCurrent ? "POS" : symbol}
                            </div>
                          );
                        })
                      ))}
                    </div>
                  </div>

                  {/* Character Status Card */}
                  <div style={{ 
                    backgroundColor: 'rgba(0,0,0,0.03)', 
                    border: '1px solid rgba(140, 110, 51, 0.2)',
                    borderRadius: '6px',
                    padding: '12px',
                    fontSize: '13px'
                  }}>
                    <div style={{ fontFamily: 'var(--font-serif)', fontSize: '11px', color: '#8c6e33', borderBottom: '1px solid rgba(140,110,51,0.15)', paddingBottom: '4px', marginBottom: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>FICHA SIMPLIFICADA</span>
                      {characters.length > 0 && selectedCharacter && characters.length < 6 && (
                        <button 
                          onClick={() => setSelectedCharacter(null)}
                          className="btn-medieval"
                          style={{ padding: '2px 6px', fontSize: '9px', textTransform: 'none' }}
                        >
                          + Nuevo
                        </button>
                      )}
                    </div>
                    {characters.length > 0 && selectedCharacter && (
                      <div style={{ marginBottom: '10px' }}>
                        <select
                          value={selectedCharacter.id}
                          onChange={(e) => {
                            const found = characters.find(c => c.id === e.target.value);
                            if (found) setSelectedCharacter(found);
                          }}
                          style={{ width: '100%', padding: '4px', fontSize: '11px', backgroundColor: '#f7eed7', border: '1px solid rgba(140,110,51,0.3)', color: '#5a4a35' }}
                        >
                          {characters.map(c => (
                            <option key={c.id} value={c.id}>{c.name} ({c.race} {c.class})</option>
                          ))}
                        </select>
                      </div>
                    )}
                    {selectedCharacter ? (
                      <div>
                        <strong style={{ fontSize: '14px', color: '#1e1d1a' }}>{selectedCharacter.name}</strong>
                        <div style={{ color: '#6b7280', fontSize: '11px', marginBottom: '8px' }}>
                          {selectedCharacter.race} {selectedCharacter.class} (Nv. {characterXP.level})
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                          <span>Puntos de Vida:</span>
                          <strong>{selectedCharacter.hp_current} / {selectedCharacter.hp_max} HP</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                          <span>Armadura (CA):</span>
                          <strong>{selectedCharacter.armor_class} CA</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span>Experiencia:</span>
                          <strong>{characterXP.xp} XP</strong>
                        </div>
                      </div>
                    ) : (
                      <div>
                        {!quizMode && !manualMode ? (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', textAlign: 'center' }}>
                            <p style={{ fontSize: '11px', color: '#6b7280', margin: '0 0 5px 0' }}>Crea tu héroe por entrevista o manualmente.</p>
                            <button className="btn-medieval" onClick={startQuiz} style={{ padding: '6px', fontSize: '11px' }}>
                              Iniciar Entrevista
                            </button>
                            <button className="btn-medieval" onClick={() => setManualMode(true)} style={{ padding: '4px', fontSize: '10px', opacity: 0.8 }}>
                              Crear Ficha Manualmente
                            </button>
                            {characters.length > 0 && (
                              <button className="btn-medieval" onClick={() => setSelectedCharacter(characters[0])} style={{ padding: '4px', fontSize: '10px', opacity: 0.8 }}>
                                Cancelar
                              </button>
                            )}
                          </div>
                        ) : quizMode ? (
                          <div>
                            {!quizResult ? (
                              <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#6b7280', marginBottom: '4px' }}>
                                  <span>ENTREVISTA</span>
                                  <span>{currentQuestionIdx + 1}/{quizQuestions.length}</span>
                                </div>
                                {quizQuestions.length > 0 && (
                                  <div>
                                    <div style={{ fontSize: '12px', marginBottom: '8px', color: '#1a1815' }}>
                                      {quizQuestions[currentQuestionIdx].question}
                                    </div>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                      {quizQuestions[currentQuestionIdx].options.map((opt: any, idx: number) => (
                                        <button
                                          key={idx}
                                          className="btn-medieval"
                                          style={{ textAlign: 'left', padding: '6px 8px', fontSize: '11px', textTransform: 'none' }}
                                          onClick={() => handleAnswerQuizQuestion(idx)}
                                        >
                                          {opt.text}
                                        </button>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            ) : (
                              <form onSubmit={handleConfirmQuizCharacter}>
                                <div style={{ fontSize: '11px', fontWeight: 'bold', color: '#b45309', marginBottom: '4px' }}>
                                  {quizResult.race_es} {quizResult.class_es}
                                </div>
                                <input
                                  type="text"
                                  value={newCharName}
                                  onChange={(e) => setNewCharName(e.target.value)}
                                  placeholder="Nombre..."
                                  style={{ width: '100%', padding: '4px', boxSizing: 'border-box', marginBottom: '8px' }}
                                  required
                                />
                                <button type="submit" className="btn-medieval" style={{ width: '100%', padding: '4px', fontSize: '11px' }}>Confirmar</button>
                              </form>
                            )}
                          </div>
                        ) : (
                          <form onSubmit={handleCreateCharacter}>
                            <input
                              type="text"
                              value={newCharName}
                              onChange={(e) => setNewCharName(e.target.value)}
                              placeholder="Nombre..."
                              style={{ width: '100%', padding: '4px', boxSizing: 'border-box', marginBottom: '4px' }}
                              required
                            />
                            <div style={{ display: 'flex', gap: '4px', marginBottom: '4px' }}>
                              <select
                                value={newCharClass}
                                onChange={(e) => setNewCharClass(e.target.value)}
                                style={{ width: '50%', padding: '4px' }}
                              >
                                <option value="Fighter">Guerrero</option>
                                <option value="Wizard">Mago</option>
                                <option value="Rogue">Pícaro</option>
                                <option value="Cleric">Clérigo</option>
                              </select>
                              <select
                                value={newCharRace}
                                onChange={(e) => setNewCharRace(e.target.value)}
                                style={{ width: '50%', padding: '4px' }}
                              >
                                <option value="Human">Humano</option>
                                <option value="Elf">Elfo</option>
                                <option value="Dwarf">Enano</option>
                              </select>
                            </div>
                            <button type="submit" className="btn-medieval" style={{ width: '100%', padding: '4px', fontSize: '11px' }}>Crear Ficha</button>
                          </form>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                /* Decision Tree Timeline View */
                <div style={{ 
                  maxHeight: '260px', 
                  overflowY: 'auto', 
                  backgroundColor: 'rgba(0,0,0,0.03)', 
                  border: '1px solid rgba(140, 110, 51, 0.2)',
                  borderRadius: '6px',
                  padding: '15px',
                  marginBottom: '20px'
                }}>
                  <div style={{ fontFamily: 'var(--font-serif)', fontSize: '11px', color: '#8c6e33', borderBottom: '1px solid rgba(140,110,51,0.15)', paddingBottom: '4px', marginBottom: '10px' }}>
                    ÁRBOL NARRATIVO Y CHECKPOINTS
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {bookPages.map((page) => (
                      <div 
                        key={page.page_number} 
                        style={{ 
                          padding: '10px', 
                          border: '1px solid rgba(140, 110, 51, 0.15)', 
                          backgroundColor: '#f7eed7',
                          borderRadius: '4px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}
                      >
                        <div>
                          <div style={{ fontWeight: 'bold', fontSize: '12px', color: '#8c6e33' }}>Página {page.page_number}</div>
                          <div style={{ fontSize: '11px', color: '#6b7280', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {page.player_text || 'Entrada / Inicio'}
                          </div>
                        </div>
                        <button
                          className="btn-medieval"
                          style={{ padding: '4px 10px', fontSize: '10px', textTransform: 'none' }}
                          disabled={isProcessing || page.page_number === bookPages.length}
                          onClick={() => handleRollback(page.page_number)}
                        >
                          Restaurar
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* RPG Dice Rolls Result */}
              {diceRollResult && (
                <div style={{ 
                  padding: '8px 15px', 
                  backgroundColor: 'rgba(229, 193, 125, 0.15)', 
                  borderRadius: '4px', 
                  border: '1px solid rgba(193, 154, 75, 0.3)',
                  marginBottom: '15px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}>
                  <span style={{ fontSize: '12px', color: '#5a4a35' }}>Dado del Destino ({diceRollResult.formula}):</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '11px', color: '#6b7280' }}>[{diceRollResult.rolls.join(', ')}] + {diceRollResult.modifier}</span>
                    <strong style={{ fontSize: '20px', color: '#8c6e33', fontFamily: 'var(--font-serif)' }}>{diceRollResult.total}</strong>
                  </div>
                </div>
              )}

              {/* Branching choices (Infinite Book Style) */}
              <div style={{ borderTop: '1px solid rgba(140, 110, 51, 0.2)', paddingTop: '15px' }}>
                <div style={{ fontFamily: 'var(--font-serif)', fontSize: '12px', color: '#8c6e33', marginBottom: '10px', letterSpacing: '1px' }}>
                  DECISIONES DE LA PÁGINA
                </div>
                
                {bookPages[currentPageIdx] && bookPages[currentPageIdx].choices && bookPages[currentPageIdx].choices.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '15px' }}>
                    {bookPages[currentPageIdx].choices.map((choice: string, idx: number) => (
                      <button
                        key={idx}
                        className="btn-medieval"
                        style={{ 
                          textAlign: 'left', 
                          padding: '10px 15px', 
                          fontSize: '13px', 
                          textTransform: 'none',
                          backgroundColor: '#f7eed7',
                          color: '#5a4a35',
                          border: '1px solid rgba(140, 110, 51, 0.3)'
                        }}
                        disabled={isProcessing || currentPageIdx !== bookPages.length - 1}
                        onClick={() => {
                          setTextInput('');
                          submitPlayerAction(choice);
                        }}
                      >
                        {idx + 1}. {choice}
                      </button>
                    ))}
                  </div>
                ) : (
                  <p style={{ fontSize: '12px', color: '#6b7280', fontStyle: 'italic' }}>No hay opciones predefinidas para esta página.</p>
                )}
              </div>

              {/* Dynamic Console Input */}
              {currentPageIdx === bookPages.length - 1 && (
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginTop: '15px' }}>
                  <button
                    className="btn-medieval"
                    style={{
                      borderRadius: '50%',
                      width: '45px',
                      height: '45px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: isRecording ? '#ef4444' : '#f7eed7',
                      borderColor: isRecording ? '#ef4444' : '#8c6e33',
                      flexShrink: 0
                    }}
                    onMouseDown={startRecording}
                    onMouseUp={stopRecording}
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '18px', height: '18px' }}>
                      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                      <line x1="12" y1="19" x2="12" y2="23" />
                      <line x1="8" y1="23" x2="16" y2="23" />
                    </svg>
                  </button>

                  <form onSubmit={handleSendText} style={{ display: 'flex', gap: '8px', width: '100%' }}>
                    <input
                      type="text"
                      value={textInput}
                      onChange={(e) => setTextInput(e.target.value)}
                      placeholder="Escribe otra acción personalizada..."
                      style={{
                        flexGrow: 1,
                        padding: '10px 12px',
                        backgroundColor: '#f7eed7',
                        border: '1px solid rgba(140, 110, 51, 0.3)',
                        color: '#1a1815',
                        borderRadius: '4px',
                        fontSize: '13px'
                      }}
                      disabled={isProcessing}
                    />
                    <button 
                      type="submit" 
                      className="btn-medieval" 
                      style={{ padding: '0 15px', fontSize: '12px' }} 
                      disabled={isProcessing}
                    >
                      Enviar
                    </button>
                  </form>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
