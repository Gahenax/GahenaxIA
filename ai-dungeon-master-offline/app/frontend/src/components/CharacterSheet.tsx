import { useState } from "react";
import "./CharacterSheet.css";

interface CharacterSheetProps {
  hp: number;
  maxHp: number;
  ac: number;
  level?: number;
  xp?: number;
  currentRoom?: string;
}

const ATTRIBUTES = {
  str: 15, dex: 10, con: 14, int: 10, wis: 12, cha: 13
};

const calculateModifier = (score: number) =>
  Math.floor((score - 10) / 2);

export function CharacterSheet({
  hp,
  maxHp,
  ac,
  level = 1,
  xp = 0,
  currentRoom
}: CharacterSheetProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const hpPercent = Math.max(0, (hp / maxHp) * 100);
  const hpColor = hpPercent > 50 ? "#4caf50" : hpPercent > 25 ? "#ff9800" : "#f44336";

  return (
    <div className={`character-sheet ${isExpanded ? "expanded" : "collapsed"}`}>
      <div className="sheet-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="header-main">
          <h3>Mercenario</h3>
          <span className="level-badge">Nv {level}</span>
        </div>
        <div className="header-stats">
          <div className="stat-box">
            <span className="stat-label">HP</span>
            <span className="stat-value" style={{ color: hpColor }}>
              {hp}/{maxHp}
            </span>
          </div>
          <div className="stat-box">
            <span className="stat-label">AC</span>
            <span className="stat-value">{ac}</span>
          </div>
          <div className="stat-box">
            <span className="stat-label">XP</span>
            <span className="stat-value">{xp}</span>
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="sheet-body">
          <div className="sheet-section">
            <h4>Hit Points</h4>
            <div className="hp-bar">
              <div
                className="hp-fill"
                style={{
                  width: `${hpPercent}%`,
                  background: hpColor,
                  transition: "width 0.4s ease, background 0.4s ease"
                }}
              />
            </div>
            <p className="hp-text">{hp} / {maxHp}</p>
          </div>

          <div className="sheet-section">
            <h4>Atributos</h4>
            <div className="attributes-grid">
              {Object.entries(ATTRIBUTES).map(([name, score]) => (
                <div key={name} className="attribute">
                  <span className="attr-name">{name.toUpperCase()}</span>
                  <span className="attr-score">{score}</span>
                  <span className="attr-mod">
                    ({calculateModifier(score) >= 0 ? "+" : ""}{calculateModifier(score)})
                  </span>
                </div>
              ))}
            </div>
          </div>

          {currentRoom && (
            <div className="sheet-section">
              <h4>Ubicación</h4>
              <p className="class-text">{currentRoom}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
