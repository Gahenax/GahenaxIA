import React, { useState, useRef, useEffect } from "react";
import "./GameBoard.css";

interface ChatMessage {
  id: string;
  role: "narrator" | "player";
  text: string;
  timestamp: Date;
}

interface GameBoardProps {
  onAction: (actionType: string, description: string) => Promise<{ narrative?: string } | null>;
  loading: boolean;
}

export function GameBoard({ onAction, loading }: GameBoardProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      role: "narrator",
      text: "Despiertas en una cámara oscura. El parpadeo de una antorcha distante revela paredes de piedra cubiertas de musgo. El aire es frío e inmóvil.",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [selectedAction, setSelectedAction] = useState<string>("combat");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || loading) return;

    const playerMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "player",
      text: inputValue,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, playerMsg]);
    const currentInput = inputValue;
    setInputValue("");

    try {
      const result = await onAction(selectedAction, currentInput);
      const narratorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "narrator",
        text: result?.narrative || "La mazmorra permanece en silencio...",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, narratorMsg]);
    } catch (error) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "narrator",
        text: "La mazmorra permanece en silencio...",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  return (
    <div className="game-board">
      <div className="board-header">
        <h2>⚔️ Game Board</h2>
        <div className="board-status">
          {loading && <span className="status-loading">Procesando...</span>}
        </div>
      </div>

      <div className="chat-container">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <span className="role-badge">{msg.role === "narrator" ? "🧙♂️" : "⚔️"}</span>
            <p className="message-text">{msg.text}</p>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="action-form">
        <select
          value={selectedAction}
          onChange={(e) => setSelectedAction(e.target.value)}
          className="action-select"
          disabled={loading}
        >
          <option value="combat">⚔️ Combat</option>
          <option value="exploration">🔍 Explore</option>
          <option value="social">💬 Social</option>
          <option value="inventory">🎒 Inventory</option>
          <option value="rest">🛌 Rest</option>
        </select>

        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Describe tu acción..."
          className="action-input"
          disabled={loading}
        />

        <button type="submit" className="action-button" disabled={loading}>
          {loading ? "⏳" : "→"}
        </button>
      </form>
    </div>
  );
}
