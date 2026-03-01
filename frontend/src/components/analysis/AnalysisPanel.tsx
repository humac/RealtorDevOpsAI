import { useState } from 'react';
import type { AnalysisResponse, TabId } from '../../types';
import OverviewTab from './OverviewTab';
import ZoningTab from './ZoningTab';
import CostsTab from './CostsTab';
import ScenariosTab from './ScenariosTab';

interface AnalysisPanelProps {
  analysis: AnalysisResponse | null;
  loading: boolean;
  error: string | null;
}

const TABS: { id: TabId; label: string }[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'zoning', label: 'Zoning' },
  { id: 'costs', label: 'Costs' },
  { id: 'scenarios', label: 'Scenarios' },
];

export default function AnalysisPanel({ analysis, loading, error }: AnalysisPanelProps) {
  const [activeTab, setActiveTab] = useState<TabId>('overview');

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <svg className="animate-spin h-10 w-10 text-primary-600 mx-auto mb-4" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
              fill="none"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          <p className="text-gray-600 font-medium">Analyzing property...</p>
          <p className="text-sm text-gray-400 mt-1">
            Aggregating data, parsing zoning, running AI analysis
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          <p className="font-medium">Analysis Failed</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      </div>
    );
  }

  if (!analysis) return null;

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="border-b border-gray-200 bg-gray-50">
        <nav className="flex">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'overview' && <OverviewTab analysis={analysis} />}
        {activeTab === 'zoning' && <ZoningTab analysis={analysis} />}
        {activeTab === 'costs' && <CostsTab analysis={analysis} />}
        {activeTab === 'scenarios' && <ScenariosTab analysis={analysis} />}
      </div>

      {/* Disclaimer */}
      <div className="border-t border-gray-200 px-6 py-2 bg-gray-50">
        <p className="text-xs text-gray-400">{analysis.disclaimer}</p>
      </div>
    </div>
  );
}
