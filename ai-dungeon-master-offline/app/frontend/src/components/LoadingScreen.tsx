import "./LoadingScreen.css";

interface LoadingScreenProps {
  message: string;
  error?: string | null;
}

export function LoadingScreen({ message, error }: LoadingScreenProps) {
  return (
    <div className="loading-screen">
      <div className="loading-box">
        <div className="loading-spinner">🧙‍♂️</div>
        <p className="loading-message">{message}</p>
        {error && (
          <div className="loading-error">
            <strong>Error:</strong> {error}
          </div>
        )}
      </div>
    </div>
  );
}
