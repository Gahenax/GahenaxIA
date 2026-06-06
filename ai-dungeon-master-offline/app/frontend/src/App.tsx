import { GameBoard } from "./components/GameBoard";
import { CharacterSheet } from "./components/CharacterSheet";
import { LoadingScreen } from "./components/LoadingScreen";
import { useBackend } from "./hooks/useBackend";
import { useGameEngine } from "./hooks/useGameEngine";
import "./App.css";

function App() {
  const { isRunning, loading: backendLoading, error: backendError } = useBackend();
  const { gameState, loading: actionLoading, error: actionError, performAction } = useGameEngine();

  if (backendLoading) {
    return <LoadingScreen message="Iniciando Backend..." error={backendError} />;
  }

  if (!isRunning) {
    return (
      <LoadingScreen
        message="Backend no disponible"
        error={backendError || "No se pudo conectar con los servicios"}
      />
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🧙‍♂️ CRIPTA</h1>
          <span className="tagline">Dungeon Master Virtual — D&D 5.5</span>
        </div>
        <div className="header-status">
          <span className="status-indicator ready">● Backend activo</span>
        </div>
      </header>

      <main className="app-main">
        <aside className="sidebar">
          <div className="sidebar-content">
            <CharacterSheet
              hp={gameState.hp}
              maxHp={gameState.maxHp}
              ac={gameState.ac}
              level={gameState.level}
              xp={gameState.xp}
              currentRoom={gameState.room}
            />
            <div className="sidebar-section">
              <h3>Acciones rápidas</h3>
              <div className="command-buttons">
                <button
                  onClick={() => performAction("combat", "Ataco al enemigo más cercano")}
                  disabled={actionLoading}
                >
                  ⚔️ Atacar
                </button>
                <button
                  onClick={() => performAction("exploration", "Examino la habitación")}
                  disabled={actionLoading}
                >
                  🔍 Explorar
                </button>
                <button
                  onClick={() => performAction("rest", "Descanso un momento")}
                  disabled={actionLoading}
                >
                  🛌 Descansar
                </button>
                <button
                  onClick={() => performAction("inventory", "Reviso mi inventario")}
                  disabled={actionLoading}
                >
                  🎒 Inventario
                </button>
              </div>
            </div>
          </div>
        </aside>

        <section className="main-content">
          <GameBoard onAction={performAction} loading={actionLoading} />
          {actionError && (
            <div className="error-banner">
              <span> {actionError}</span>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
