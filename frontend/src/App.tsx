import { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/common/Header';
import PropertyMap from './components/map/PropertyMap';
import AnalysisPanel from './components/analysis/AnalysisPanel';
import AnalysisForm from './components/dashboard/AnalysisForm';
import SettingsPage from './components/settings/SettingsPage';
import { useAnalysis } from './hooks/useAnalysis';
import type { AnalyzeRequest } from './types';

function HomePage() {
  const { analysis, loading, error, runAnalysis, clearAnalysis } = useAnalysis();
  const [selectedCoords, setSelectedCoords] = useState<[number, number] | null>(null);

  const handleAnalyze = async (request: AnalyzeRequest) => {
    await runAnalysis(request);
  };

  const handleMapClick = (lng: number, lat: number) => {
    setSelectedCoords([lng, lat]);
  };

  return (
    <div className="h-screen flex flex-col">
      <Header
        opportunityScore={analysis?.overall_opportunity_score ?? null}
        onNewAnalysis={clearAnalysis}
      />

      {!analysis && !loading ? (
        <div className="flex-1 flex">
          <div className="w-3/5 relative">
            <PropertyMap
              onMapClick={handleMapClick}
              selectedCoords={selectedCoords}
            />
          </div>
          <div className="w-2/5 border-l border-gray-200 overflow-y-auto bg-white p-6">
            <AnalysisForm onSubmit={handleAnalyze} loading={loading} error={error} />
          </div>
        </div>
      ) : (
        <div className="flex-1 flex">
          <div className="w-3/5 relative">
            <PropertyMap
              onMapClick={handleMapClick}
              selectedCoords={selectedCoords}
            />
          </div>
          <div className="w-2/5 border-l border-gray-200 overflow-y-auto bg-white">
            <AnalysisPanel analysis={analysis} loading={loading} error={error} />
          </div>
        </div>
      )}

      <footer className="bg-gray-800 text-gray-400 text-xs text-center py-2">
        RealtorDevOpsAI | AI analysis is not legal or financial advice. Consult qualified professionals.
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/settings" element={<SettingsPage />} />
    </Routes>
  );
}
