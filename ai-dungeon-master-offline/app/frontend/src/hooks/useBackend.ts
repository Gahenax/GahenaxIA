import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";

export function useBackend() {
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function checkStatus() {
      try {
        await invoke("get_status");
        setIsRunning(true);
      } catch (err) {
        setError(String(err));
        setIsRunning(false);
      } finally {
        setLoading(false);
      }
    }
    checkStatus();
  }, []);

  return { isRunning, loading, error };
}
