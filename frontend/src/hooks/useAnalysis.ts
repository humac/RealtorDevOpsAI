import { useCallback, useState } from 'react';
import type { AnalysisResponse, AnalyzeRequest } from '../types';
import { analyzeProperty } from '../services/api';

interface UseAnalysisReturn {
  analysis: AnalysisResponse | null;
  loading: boolean;
  error: string | null;
  runAnalysis: (request: AnalyzeRequest) => Promise<void>;
  clearAnalysis: () => void;
}

export function useAnalysis(): UseAnalysisReturn {
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = useCallback(async (request: AnalyzeRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeProperty(request);
      setAnalysis(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Analysis failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearAnalysis = useCallback(() => {
    setAnalysis(null);
    setError(null);
  }, []);

  return { analysis, loading, error, runAnalysis, clearAnalysis };
}
