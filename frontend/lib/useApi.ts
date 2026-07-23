"use client";

import { useCallback, useEffect, useState } from "react";

// Kleiner Hook zum Laden von Daten beim Mounten – mit Lade-/Fehlerzustand.
export function useApi<T>(loader: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const memoLoader = useCallback(loader, []);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await memoLoader();
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unbekannter Fehler");
    } finally {
      setLoading(false);
    }
  }, [memoLoader]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { data, loading, error, reload, setData };
}
