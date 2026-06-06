import React, { useState, useEffect, useRef } from 'react';
import './index.css';
import { invoke } from '@tauri-apps/api/core';

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
  background: string;
  hp_current: number;
  hp_max: number;
  armor_class: number;
  stats?: Record<string, number>;
  inventory?: {
    gold?: number;
    items?: string[];
  };
}


function App() {
  // Navigation & Setup State
  const [status, setStatus] = useState<any>(null);
  const [modelInfo, setModelInfo] = useState<{active_model: string, is_qwen25: boolean} | null>(null);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [globalCharacters, setGlobalCharacters] = useState<Character[]>([]);
  const [characterXP, setCharacterXP] = useState<{xp: number, level: number}>({xp: 0, level: 1});
  const [appLoading, setAppLoading] = useState(true);
  
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
    const initApp = async () => {
      try {
        await Promise.all([
          fetchStatus(),
          fetchModelInfo(),
          fetchCampaigns(),
          fetchGlobalCharacters()
        ]);
      } catch (e) {
        console.error("Error during startup:", e);
      } finally {
        setTimeout(() => {
          setAppLoading(false);
        }, 2200);
      }
    };
    initApp();

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
      const data = await invoke<any>('get_quiz_questions');
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
        const data = await invoke<any>('evaluate_quiz', { answers: newAnswers });
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
    if (!newCharName || !quizResult) return;
    try {
      const data = await invoke<any>('create_character', {
        campaignId: selectedCampaign ? selectedCampaign.id : null,
        name: newCharName,
        charClass: quizResult.class,
        race: quizResult.race,
        background: quizResult.background,
        hpMax: quizResult.hp_max,
        armorClass: quizResult.armor_class,
        stats: quizResult.stats,
        inventory: { gold: 15, items: ["Espada corta", "Raciones", "Parchamento"] }
      });
      if (selectedCampaign) {
        setCharacters([data, ...characters]);
        setSelectedCharacter(data);
        await fetchPages(selectedCampaign.id);
        await fetchMap(selectedCampaign.id);
      } else {
        setGlobalCharacters([data, ...globalCharacters]);
      }
      setNewCharName('');
      setQuizMode(false);
      setQuizResult(null);
    } catch (e: any) {
      alert(e || "Error al crear personaje");
    }
  };


  const fetchStatus = async () => {
    try {
      const data = await invoke<any>('get_status');
      setStatus(data);
    } catch (e) {
      console.error("Backend offline", e);
    }
  };

  const fetchModelInfo = async () => {
    try {
      const data = await invoke<any>('get_model_status');
      setModelInfo(data);
    } catch (e) {
      console.error("Model status check failed", e);
    }
  };

  const fetchCampaigns = async () => {
    try {
      const data = await invoke<any>('list_campaigns');
      setCampaigns(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateCampaign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCampaignName) return;
    try {
      const data = await invoke<any>('create_campaign', { name: newCampaignName, system: 'D&D 5.5 (2024)', tone: newCampaignTone });
      setCampaigns([data, ...campaigns]);
      setSelectedCampaign(data);
      setNewCampaignName('');
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateCharacter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCharName) return;
    try {
      const data = await invoke<any>('create_character', {
        campaignId: selectedCampaign ? selectedCampaign.id : null,
        name: newCharName,
        charClass: newCharClass,
        race: newCharRace,
        background: 'Outlander',
        hpMax: 12,
        armorClass: 15,
        stats: { STR: 16, DEX: 14, CON: 15, INT: 10, WIS: 12, CHA: 8 },
        inventory: { gold: 15, items: ["Iron Sword", "Shield", "Parchment Map"] }
      });
      if (selectedCampaign) {
        setCharacters([data, ...characters]);
        setSelectedCharacter(data);
        await fetchPages(selectedCampaign.id);
        await fetchMap(selectedCampaign.id);
      } else {
        setGlobalCharacters([data, ...globalCharacters]);
      }
      setNewCharName('');
      setManualMode(false);
    } catch (e: any) {
      alert(e || "Error al crear personaje");
    }
  };

  const fetchGlobalCharacters = async () => {
    try {
      const data = await invoke<any>('list_all_characters', { campaignId: null, unassignedOnly: true });
      setGlobalCharacters(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleAssignCharacter = async (charId: string) => {
    if (!selectedCampaign) return;
    try {
      await invoke('assign_character', { characterId: charId, campaignId: selectedCampaign.id });
      await fetchCharacters(selectedCampaign.id);
      await fetchGlobalCharacters();
      await fetchPages(selectedCampaign.id);
      await fetchMap(selectedCampaign.id);
    } catch (e: any) {
      alert(e || "Error al reclutar héroe");
    }
  };

  const fetchCharacters = async (campId: string) => {
    try {
      const data = await invoke<any>('list_characters', { campaignId: campId });
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
      const data = await invoke<any>('get_campaign_pages', { campaignId: campId });
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
      const data = await invoke<any>('get_campaign_map', { campaignId: campId });
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
    fetchGlobalCharacters();
    fetchPages(camp.id);
    fetchMap(camp.id);
  };

  const submitPlayerAction = async (text: string) => {
    if (!selectedCampaign || !selectedCharacter || isProcessing) return;
    setIsProcessing(true);

    try {
      const data = await invoke<any>('process_turn', {
        campaignId: selectedCampaign.id,
        characterId: selectedCharacter.id,
        textInput: text,
        audioBytes: null
      });

      if (!data || typeof data.page_number === 'undefined' || !data.coordinates) {
        alert("El servidor retornó una respuesta inválida");
        return;
      }
      
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
        try {
          const audioBase64 = await invoke<string>('get_audio_base64', { path: data.audio_file });
          setAudioUrl(audioBase64);
          const audio = new Audio(audioBase64);
          audio.play().catch(err => console.error("Audio autoplay failed:", err));
        } catch (audioErr) {
          console.error("Failed to load audio base64:", audioErr);
        }
      }
    } catch (err: any) {
      console.error(err);
      alert(err || "Error al procesar el turno");
    } finally {
      setIsProcessing(false);
    }
  };

  const playPageTTS = async (text: string) => {
    if (!text || isProcessing) return;
    try {
      setIsProcessing(true);
      const path = await invoke<string>('synthesize_tts', { text });
      const audioBase64 = await invoke<string>('get_audio_base64', { path });
      const audio = new Audio(audioBase64);
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
      await invoke('rollback_campaign', { campaignId: selectedCampaign.id, pageNumber });
      await fetchPages(selectedCampaign.id);
      setShowDecisionTree(false);
    } catch (e: any) {
      console.error("Rollback failed", e);
      alert(e || "Error al realizar el viaje en el tiempo");
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

    try {
      const arrayBuffer = await blob.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);
      const audioBytes = Array.from(uint8Array);

      const data = await invoke<any>('process_turn', {
        campaignId: selectedCampaign.id,
        characterId: selectedCharacter.id,
        textInput: null,
        audioBytes: audioBytes
      });

      if (!data || typeof data.page_number === 'undefined' || !data.coordinates) {
        alert("El servidor retornó una respuesta inválida");
        return;
      }

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
        try {
          const audioBase64 = await invoke<string>('get_audio_base64', { path: data.audio_file });
          setAudioUrl(audioBase64);
          const audio = new Audio(audioBase64);
          audio.play().catch(err => console.error("Audio autoplay failed:", err));
        } catch (audioErr) {
          console.error("Failed to load audio base64:", audioErr);
        }
      }
    } catch (err: any) {
      console.error(err);
      alert(err || "Error al procesar el audio");
    } finally {
      setIsProcessing(false);
    }
  };

  if (appLoading) {
    return (
      <div className="loading-screen">
        <h1 className="loading-title">CRIPTA</h1>
        <div className="loading-subtitle">Dungeon Master AI Offline</div>
        <div className="loading-bar-container">
          <div className="loading-bar-progress"></div>
        </div>
        <div className="loading-status-text">
          {status ? "Grimorio cargado y listo" : "Sintonizando energías elementales..."}
        </div>
      </div>
    );
  }

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
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1.2fr 1fr', gap: '20px', marginTop: '40px' }}>
          {/* Column 1: Campaigns */}
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

          {/* Column 2: Taberna de Héroes (Global Characters) */}
          <div className="medieval-border" style={{ padding: '20px', backgroundColor: 'var(--color-stone-medium)', display: 'flex', flexDirection: 'column' }}>
            <h2 style={{ fontFamily: 'var(--font-serif)', color: 'var(--color-gold)' }}>Taberna de Héroes</h2>
            
            {!quizMode && !manualMode ? (
              <>
                <p style={{ color: 'var(--color-text-muted)', fontSize: '13px' }}>Héroes errantes creados globalmente listos para ser asignados a campañas.</p>
                {globalCharacters.length === 0 ? (
                  <p style={{ fontStyle: 'italic', color: 'var(--color-text-muted)', fontSize: '12px', margin: '20px 0' }}>La taberna está vacía. Crea un personaje para iniciar.</p>
                ) : (
                  <div style={{ flexGrow: 1, overflowY: 'auto', maxHeight: '250px', marginBottom: '20px' }}>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                      {globalCharacters.map((c) => (
                        <li key={c.id} style={{ 
                          padding: '10px', 
                          border: '1px solid var(--color-gold-dim)', 
                          backgroundColor: 'var(--color-stone-light)', 
                          marginBottom: '8px',
                          borderRadius: '4px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}>
                          <div>
                            <strong style={{ color: 'var(--color-gold)' }}>{c.name}</strong>
                            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                              {c.race} {c.class}
                            </div>
                          </div>
                          <span style={{ fontSize: '11px', color: 'var(--color-gold-dim)' }}>Sin Gesta</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: 'auto' }}>
                  <button className="btn-medieval" onClick={startQuiz} style={{ padding: '8px', fontSize: '12px' }}>
                    Crear por Entrevista
                  </button>
                  <button className="btn-medieval" onClick={() => setManualMode(true)} style={{ padding: '6px', fontSize: '11px', opacity: 0.8 }}>
                    Crear Ficha Manual
                  </button>
                </div>
              </>
            ) : quizMode ? (
              <div style={{ backgroundColor: 'var(--color-stone-light)', padding: '15px', borderRadius: '4px', border: '1px solid var(--color-gold-dim)' }}>
                {!quizResult ? (
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--color-text-muted)', marginBottom: '8px' }}>
                      <span>ENTREVISTA NARRATIVA</span>
                      <span>{currentQuestionIdx + 1}/{quizQuestions.length}</span>
                    </div>
                    {quizQuestions.length > 0 && (
                      <div>
                        <div style={{ fontSize: '13px', marginBottom: '12px', color: '#fff', fontWeight: 'bold' }}>
                          {quizQuestions[currentQuestionIdx].question}
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                          {quizQuestions[currentQuestionIdx].options.map((opt: any, idx: number) => (
                            <button
                              key={idx}
                              className="btn-medieval"
                              style={{ textAlign: 'left', padding: '8px 10px', fontSize: '12px', textTransform: 'none' }}
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
                    <h3 style={{ fontFamily: 'var(--font-serif)', color: 'var(--color-gold)', margin: '0 0 10px 0', fontSize: '16px' }}>Héroe Destinado</h3>
                    <div style={{ fontSize: '13px', fontWeight: 'bold', color: '#f59e0b', marginBottom: '10px' }}>
                      {quizResult.race_es} {quizResult.class_es}
                    </div>
                    <div style={{ marginBottom: '12px' }}>
                      <label style={{ display: 'block', fontSize: '11px', marginBottom: '4px' }}>Escribe el nombre de tu héroe:</label>
                      <input
                        type="text"
                        value={newCharName}
                        onChange={(e) => setNewCharName(e.target.value)}
                        placeholder="Nombre del héroe..."
                        style={{ width: '100%', padding: '8px', backgroundColor: 'var(--color-stone-medium)', border: '1px solid var(--color-gold-dim)', color: '#fff', boxSizing: 'border-box' }}
                        required
                      />
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button type="submit" className="btn-medieval" style={{ flex: 1, padding: '8px', fontSize: '12px' }}>Confirmar</button>
                      <button type="button" className="btn-medieval" onClick={() => { setQuizMode(false); setQuizResult(null); }} style={{ flex: 1, padding: '8px', fontSize: '12px', opacity: 0.7 }}>Cancelar</button>
                    </div>
                  </form>
                )}
              </div>
            ) : (
              <form onSubmit={handleCreateCharacter} style={{ backgroundColor: 'var(--color-stone-light)', padding: '15px', borderRadius: '4px', border: '1px solid var(--color-gold-dim)' }}>
                <h3 style={{ fontFamily: 'var(--font-serif)', color: 'var(--color-gold)', margin: '0 0 10px 0', fontSize: '16px' }}>Nuevo Personaje</h3>
                <div style={{ marginBottom: '8px' }}>
                  <input
                    type="text"
                    value={newCharName}
                    onChange={(e) => setNewCharName(e.target.value)}
                    placeholder="Nombre del héroe..."
                    style={{ width: '100%', padding: '8px', backgroundColor: 'var(--color-stone-medium)', border: '1px solid var(--color-gold-dim)', color: '#fff', boxSizing: 'border-box' }}
                    required
                  />
                </div>
                <div style={{ display: 'flex', gap: '6px', marginBottom: '12px' }}>
                  <select
                    value={newCharClass}
                    onChange={(e) => setNewCharClass(e.target.value)}
                    style={{ width: '50%', padding: '8px', backgroundColor: 'var(--color-stone-medium)', border: '1px solid var(--color-gold-dim)', color: '#fff' }}
                  >
                    <option value="Fighter">Guerrero</option>
                    <option value="Wizard">Mago</option>
                    <option value="Rogue">Pícaro</option>
                    <option value="Cleric">Clérigo</option>
                  </select>
                  <select
                    value={newCharRace}
                    onChange={(e) => setNewCharRace(e.target.value)}
                    style={{ width: '50%', padding: '8px', backgroundColor: 'var(--color-stone-medium)', border: '1px solid var(--color-gold-dim)', color: '#fff' }}
                  >
                    <option value="Human">Humano</option>
                    <option value="Elf">Elfo</option>
                    <option value="Dwarf">Enano</option>
                  </select>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button type="submit" className="btn-medieval" style={{ flex: 1, padding: '8px', fontSize: '12px' }}>Crear Ficha</button>
                  <button type="button" className="btn-medieval" onClick={() => setManualMode(false)} style={{ flex: 1, padding: '8px', fontSize: '12px', opacity: 0.7 }}>Cancelar</button>
                </div>
              </form>
            )}
          </div>

          {/* Column 3: Nueva Gesta */}
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
            <button className="btn-medieval" style={{ padding: '6px 15px', fontSize: '12px' }} onClick={() => { setSelectedCampaign(null); fetchGlobalCharacters(); }}>
              Volver al Lobby
            </button>
          </div>

          <div className="book-container">
            <div className="book-spine"></div>

            {/* PAGE LEFT: Dungeon Map, Character Sheet, and Mechanics Log */}
            <div className="book-page-left">
              <div className="book-page-header">
                <span>Estado del Mundo</span>
                <span>Mecánicas & Estado</span>
              </div>

              {!selectedCharacter ? (
                /* Character Selection / Creation Form */
                <div style={{ padding: '10px 0' }}>
                  <h3 style={{ fontFamily: 'var(--font-serif)', color: '#8c6e33', margin: '0 0 10px 0', fontSize: '18px', textAlign: 'center' }}>Creación de Héroe</h3>
                  <p style={{ fontSize: '13px', lineHeight: '1.5', color: '#5a4a35', margin: '0 0 20px 0', textAlign: 'center' }}>
                    Antes de cruzar el umbral de la cripta y comenzar tu gesta, debes dar vida a tu héroe.
                  </p>
                  <div style={{ 
                    backgroundColor: 'rgba(0,0,0,0.03)', 
                    border: '1px solid rgba(140, 110, 51, 0.2)',
                    borderRadius: '6px',
                    padding: '15px'
                  }}>
                    {!quizMode && !manualMode ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', textAlign: 'center' }}>
                        <p style={{ fontSize: '12px', color: '#5a4a35', margin: '0' }}>Elige una opción para tu personaje:</p>
                        <button className="btn-medieval" onClick={startQuiz} style={{ padding: '8px', fontSize: '12px' }}>
                          Iniciar Entrevista de Destino
                        </button>
                        <button className="btn-medieval" onClick={() => setManualMode(true)} style={{ padding: '6px', fontSize: '11px', opacity: 0.9 }}>
                          Crear Ficha Manualmente
                        </button>
                        {globalCharacters.length > 0 && (
                          <div style={{ marginTop: '12px', borderTop: '1px solid rgba(140, 110, 51, 0.15)', paddingTop: '12px' }}>
                            <label style={{ display: 'block', fontSize: '12px', marginBottom: '6px', color: '#8c6e33', textAlign: 'left' }}>Reclutar héroe de la Taberna:</label>
                            <select 
                              onChange={async (e) => {
                                if (e.target.value) {
                                  await handleAssignCharacter(e.target.value);
                                }
                              }}
                              defaultValue=""
                              style={{ width: '100%', padding: '6px', fontSize: '12px', backgroundColor: '#f7eed7', border: '1px solid rgba(140,110,51,0.3)', color: '#5a4a35' }}
                            >
                              <option value="" disabled>Selecciona un héroe...</option>
                              {globalCharacters.map(c => (
                                <option key={c.id} value={c.id}>{c.name} ({c.race} {c.class})</option>
                              ))}
                            </select>
                          </div>
                        )}
                      </div>
                    ) : quizMode ? (
                      <div>
                        {!quizResult ? (
                          <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#6b7280', marginBottom: '4px' }}>
                              <span>ENTREVISTA DE DESTINO</span>
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
                          placeholder="Nombre del héroe..."
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
                        <button type="button" className="btn-medieval" onClick={() => setManualMode(false)} style={{ width: '100%', padding: '4px', fontSize: '10px', opacity: 0.8, marginTop: '4px' }}>
                          Cancelar
                        </button>
                      </form>
                    )}
                  </div>
                </div>
              ) : (
                /* Active Game State: Map, Character stats, and Dice rolls */
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', minHeight: '440px' }}>
                  {/* Row 1: Map and Quick Stats side by side */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: '15px' }}>
                    {/* Procedural Map */}
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontFamily: 'var(--font-serif)', fontSize: '11px', color: '#8c6e33', marginBottom: '8px', letterSpacing: '1px' }}>
                        MAPA PROCEDURAL
                      </div>
                      <div className="dungeon-map-grid">
                        {Array.from({ length: 5 }).map((_, yIdx) => (
                          Array.from({ length: 5 }).map((_, xIdx) => {
                            const isCurrent = playerCoords && playerCoords.x === xIdx && playerCoords.y === yIdx;
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

                    {/* Character Card info */}
                    <div style={{ 
                      backgroundColor: 'rgba(0,0,0,0.02)', 
                      border: '1px solid rgba(140, 110, 51, 0.15)',
                      borderRadius: '6px',
                      padding: '10px',
                      fontSize: '12px'
                    }}>
                      <div style={{ 
                        fontFamily: 'var(--font-serif)', 
                        fontSize: '10px', 
                        color: '#8c6e33', 
                        borderBottom: '1px solid rgba(140,110,51,0.15)', 
                        paddingBottom: '4px', 
                        marginBottom: '6px', 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        alignItems: 'center' 
                      }}>
                        <span>FICHA DEL HÉROE</span>
                        {characters.length > 1 && (
                          <select
                            value={selectedCharacter.id}
                            onChange={(e) => {
                              const found = characters.find(c => c.id === e.target.value);
                              if (found) setSelectedCharacter(found);
                            }}
                            style={{ padding: '2px', fontSize: '10px', backgroundColor: '#f7eed7', border: '1px solid rgba(140,110,51,0.2)' }}
                          >
                            {characters.map(c => (
                              <option key={c.id} value={c.id}>{c.name}</option>
                            ))}
                          </select>
                        )}
                      </div>

                      <strong style={{ fontSize: '14px', color: '#1e1d1a', fontFamily: 'var(--font-serif)' }}>{selectedCharacter.name}</strong>
                      <div style={{ color: '#8c6e33', fontSize: '11px', marginBottom: '4px', fontWeight: 'bold' }}>
                        {selectedCharacter.race} {selectedCharacter.class} (Nv. {characterXP.level})
                      </div>
                      <div style={{ color: '#6b7280', fontSize: '10px', marginBottom: '8px', fontStyle: 'italic' }}>
                        Trasfondo: {selectedCharacter.background}
                      </div>

                      {/* Health, AC, XP block */}
                      <div style={{ display: 'flex', gap: '8px', marginBottom: '10px', fontSize: '11px' }}>
                        <div style={{ flex: 1, backgroundColor: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '4px', padding: '4px 6px', textAlign: 'center' }}>
                          <div style={{ fontSize: '9px', color: '#b91c1c' }}>VIDA</div>
                          <strong>{selectedCharacter.hp_current} / {selectedCharacter.hp_max} HP</strong>
                        </div>
                        <div style={{ flex: 1, backgroundColor: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.2)', borderRadius: '4px', padding: '4px 6px', textAlign: 'center' }}>
                          <div style={{ fontSize: '9px', color: '#1d4ed8' }}>ARMADURA</div>
                          <strong>{selectedCharacter.armor_class} CA</strong>
                        </div>
                        <div style={{ flex: 1, backgroundColor: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: '4px', padding: '4px 6px', textAlign: 'center' }}>
                          <div style={{ fontSize: '9px', color: '#047857' }}>EXP</div>
                          <strong>{characterXP.xp} XP</strong>
                        </div>
                      </div>

                      {/* Attributes Grid (STR, DEX, CON, INT, WIS, CHA) */}
                      {selectedCharacter.stats && (
                        <div style={{ 
                          display: 'grid', 
                          gridTemplateColumns: 'repeat(3, 1fr)', 
                          gap: '6px', 
                          marginBottom: '10px' 
                        }}>
                          {Object.entries(selectedCharacter.stats).map(([statName, val]) => {
                            const mod = Math.floor((val - 10) / 2);
                            const modSign = mod >= 0 ? `+${mod}` : `${mod}`;
                            return (
                              <div key={statName} style={{
                                backgroundColor: '#f7eed7',
                                border: '1px solid rgba(140, 110, 51, 0.18)',
                                borderRadius: '4px',
                                padding: '4px',
                                textAlign: 'center'
                              }}>
                                <div style={{ fontSize: '9px', color: '#8c6e33', fontWeight: 'bold' }}>{statName}</div>
                                <div style={{ fontSize: '13px', fontWeight: 'bold', color: '#1e1d1a' }}>{val}</div>
                                <div style={{ fontSize: '9px', color: '#6b7280' }}>{modSign}</div>
                              </div>
                            );
                          })}
                        </div>
                      )}

                      {/* Inventory Block */}
                      <div style={{ 
                        borderTop: '1px solid rgba(140,110,51,0.12)', 
                        paddingTop: '6px', 
                        fontSize: '11px',
                        color: '#5a4a35'
                      }}>
                        <div style={{ fontSize: '9px', color: '#8c6e33', fontWeight: 'bold', marginBottom: '2px' }}>INVENTARIO</div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                          <span>Oro:</span>
                          <strong>{selectedCharacter.inventory?.gold || 0} PO</strong>
                        </div>
                        {selectedCharacter.inventory?.items && selectedCharacter.inventory.items.length > 0 && (
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '4px' }}>
                            {selectedCharacter.inventory.items.map((item, idx) => (
                              <span key={idx} style={{
                                fontSize: '9px',
                                backgroundColor: 'rgba(140, 110, 51, 0.08)',
                                border: '1px solid rgba(140, 110, 51, 0.15)',
                                color: '#5a4a35',
                                padding: '1px 4px',
                                borderRadius: '2px'
                              }}>
                                {item}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Row 2: Mechanics & Dice roll log */}
                  <div style={{ flexGrow: 1 }}>
                    <div style={{ fontFamily: 'var(--font-serif)', fontSize: '11px', color: '#8c6e33', marginBottom: '8px', letterSpacing: '1px' }}>
                      REGISTRO DE COMBATE Y EVENTOS
                    </div>

                    {/* Dice roll visual */}
                    {diceRollResult && (
                      <div style={{ 
                        padding: '6px 12px', 
                        backgroundColor: 'rgba(229, 193, 125, 0.12)', 
                        borderRadius: '4px', 
                        border: '1px solid rgba(193, 154, 75, 0.25)',
                        marginBottom: '10px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between'
                      }}>
                        <span style={{ fontSize: '11px', color: '#5a4a35' }}>Tirada ({diceRollResult.formula}):</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontSize: '10px', color: '#6b7280' }}>[{diceRollResult.rolls.join(', ')}] + {diceRollResult.modifier}</span>
                          <strong style={{ fontSize: '16px', color: '#8c6e33', fontFamily: 'var(--font-serif)' }}>{diceRollResult.total}</strong>
                        </div>
                      </div>
                    )}

                    {/* Text Mechanics */}
                    {bookPages[currentPageIdx] && bookPages[currentPageIdx].mechanics ? (
                      <div style={{ 
                        padding: '10px 12px',
                        backgroundColor: 'rgba(140, 110, 51, 0.06)',
                        borderRadius: '4px',
                        fontSize: '12px', 
                        fontFamily: 'monospace', 
                        color: '#5a4a35',
                        border: '1px solid rgba(140, 110, 51, 0.12)',
                        minHeight: '80px',
                        whiteSpace: 'pre-line'
                      }}>
                        {bookPages[currentPageIdx].mechanics}
                      </div>
                    ) : (
                      <div style={{ color: '#6b7280', fontSize: '11px', fontStyle: 'italic', padding: '10px', textAlign: 'center' }}>
                        Sin novedades mecánicas en esta página.
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Book footer at the bottom of the Left Page */}
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

            {/* PAGE RIGHT: AI Narration, customized choices, and text input */}
            <div className="book-page-right">
              <div className="book-page-header">
                <span>{selectedCampaign.name}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button
                    className="btn-medieval"
                    style={{ 
                      padding: '2px 8px', 
                      fontSize: '10px', 
                      textTransform: 'none',
                      backgroundColor: !showDecisionTree ? 'var(--color-gold-dim)' : 'transparent',
                      color: !showDecisionTree ? '#fff' : '#8c6e33',
                      border: '1px solid #8c6e33'
                    }}
                    onClick={() => setShowDecisionTree(false)}
                  >
                    Gesta
                  </button>
                  <button
                    className="btn-medieval"
                    style={{ 
                      padding: '2px 8px', 
                      fontSize: '10px', 
                      textTransform: 'none',
                      backgroundColor: showDecisionTree ? 'var(--color-gold-dim)' : 'transparent',
                      color: showDecisionTree ? '#fff' : '#8c6e33',
                      border: '1px solid #8c6e33'
                    }}
                    onClick={() => setShowDecisionTree(true)}
                  >
                    Checkpoints
                  </button>
                </div>
              </div>

              {!selectedCharacter ? (
                /* Cover Page of the sealed book */
                <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '400px', textAlign: 'center' }}>
                  <h2 style={{ fontFamily: 'var(--font-serif-dec)', color: '#8c6e33', fontSize: '36px', marginBottom: '10px' }}>CRIPTA</h2>
                  <div style={{ width: '60px', height: '2px', backgroundColor: '#8c6e33', marginBottom: '20px' }}></div>
                  <p style={{ fontFamily: 'var(--font-serif)', fontSize: '13px', color: '#5a4a35', letterSpacing: '2px', textTransform: 'uppercase' }}>
                    Grimorio de Aventuras
                  </p>
                  <p style={{ fontSize: '11px', color: '#6b7280', marginTop: '30px' }}>
                    Crea un personaje en la página izquierda para abrir las páginas del libro.
                  </p>
                </div>
              ) : showDecisionTree ? (
                /* Checkpoints timeline view */
                <div style={{ minHeight: '400px' }}>
                  <div style={{ fontFamily: 'var(--font-serif)', fontSize: '12px', color: '#8c6e33', borderBottom: '1px solid rgba(140,110,51,0.15)', paddingBottom: '4px', marginBottom: '15px', letterSpacing: '1px' }}>
                    ÁRBOL NARRATIVO & REGRESIONES
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '380px', overflowY: 'auto', paddingRight: '4px' }}>
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
                          <div style={{ fontSize: '11px', color: '#6b7280', maxWidth: '220px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {page.player_text || 'Entrada / Inicio'}
                          </div>
                        </div>
                        <button
                          className="btn-medieval"
                          style={{ padding: '4px 8px', fontSize: '10px', textTransform: 'none' }}
                          disabled={isProcessing || page.page_number === bookPages.length}
                          onClick={() => handleRollback(page.page_number)}
                        >
                          Restaurar
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ) : bookPages[currentPageIdx] ? (
                /* Main Game Play & Narration Page */
                <div style={{ minHeight: '400px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    {/* Header bar within narration with TTS Escuchar */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                      <div style={{ fontSize: '12px', fontStyle: 'italic', color: '#8c6e33', fontFamily: 'var(--font-serif)' }}>
                        NARRACIÓN DEL MASTER
                      </div>
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
                    </div>

                    {/* Previous Player Action text */}
                    {bookPages[currentPageIdx].player_text && (
                      <div style={{ 
                        fontStyle: 'italic', 
                        color: 'rgba(30, 29, 26, 0.6)', 
                        marginBottom: '15px',
                        borderLeft: '3px solid var(--color-gold-dim)',
                        paddingLeft: '12px',
                        fontSize: '13px'
                      }}>
                        &ldquo;{bookPages[currentPageIdx].player_text}&rdquo;
                      </div>
                    )}

                    {/* AI Narration Body */}
                    <div style={{ 
                      fontSize: '16px', 
                      lineHeight: '1.6', 
                      fontFamily: 'var(--font-readable)',
                      color: '#1a1815',
                      whiteSpace: 'pre-line',
                      marginBottom: '20px'
                    }}>
                      {bookPages[currentPageIdx].dm_text}
                    </div>
                  </div>

                  {/* Choices & Text Input */}
                  <div>
                    {/* customized Choices buttons list */}
                    <div style={{ borderTop: '1px solid rgba(140, 110, 51, 0.15)', paddingTop: '12px', marginBottom: '12px' }}>
                      <div style={{ fontFamily: 'var(--font-serif)', fontSize: '11px', color: '#8c6e33', marginBottom: '8px', letterSpacing: '1px' }}>
                        DECISIONES NARRATIVAS
                      </div>
                      
                      {bookPages[currentPageIdx].choices && bookPages[currentPageIdx].choices.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                          {bookPages[currentPageIdx].choices.map((choice: string, idx: number) => (
                            <button
                              key={idx}
                              className="btn-medieval"
                              style={{ 
                                textAlign: 'left', 
                                padding: '8px 12px', 
                                fontSize: '12px', 
                                textTransform: 'none',
                                backgroundColor: '#f7eed7',
                                color: '#5a4a35',
                                border: '1px solid rgba(140, 110, 51, 0.25)',
                                transition: 'all 0.15s ease'
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
                        <p style={{ fontSize: '11px', color: '#6b7280', fontStyle: 'italic', margin: '5px 0 0 0' }}>No hay opciones predefinidas para esta página.</p>
                      )}
                    </div>

                    {/* Customized Custom Action input bar */}
                    {currentPageIdx === bookPages.length - 1 && (
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '10px' }}>
                        <button
                          className="btn-medieval"
                          style={{
                            borderRadius: '50%',
                            width: '40px',
                            height: '40px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            backgroundColor: isRecording ? '#ef4444' : '#f7eed7',
                            borderColor: isRecording ? '#ef4444' : '#8c6e33',
                            flexShrink: 0
                          }}
                          onMouseDown={startRecording}
                          onMouseUp={stopRecording}
                          title="Grabar Voz"
                        >
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px' }}>
                            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                            <line x1="12" y1="19" x2="12" y2="23" />
                            <line x1="8" y1="23" x2="16" y2="23" />
                          </svg>
                        </button>

                        <form onSubmit={handleSendText} style={{ display: 'flex', gap: '6px', width: '100%' }}>
                          <input
                            type="text"
                            value={textInput}
                            onChange={(e) => setTextInput(e.target.value)}
                            placeholder="Describe tu acción personalizada..."
                            style={{
                              flexGrow: 1,
                              padding: '8px 10px',
                              backgroundColor: '#f7eed7',
                              border: '1px solid rgba(140, 110, 51, 0.25)',
                              color: '#1a1815',
                              borderRadius: '4px',
                              fontSize: '12px'
                            }}
                            disabled={isProcessing}
                          />
                          <button 
                            type="submit" 
                            className="btn-medieval" 
                            style={{ padding: '0 12px', fontSize: '11px' }} 
                            disabled={isProcessing}
                          >
                            Enviar
                          </button>
                        </form>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div style={{ color: '#5a4a35', fontStyle: 'italic', textAlign: 'center', marginTop: '60px', fontSize: '12px' }}>
                  El libro aguarda las decisiones del héroe...
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
