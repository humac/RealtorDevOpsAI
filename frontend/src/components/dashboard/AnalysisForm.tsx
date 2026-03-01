import { useState } from 'react';
import type { AnalyzeRequest } from '../../types';

interface AnalysisFormProps {
  onSubmit: (request: AnalyzeRequest) => void;
  loading: boolean;
  error: string | null;
}

const TARGET_USE_OPTIONS = [
  { value: 'multi_unit_rental', label: 'Multi-Unit Rental' },
  { value: 'single_family', label: 'Single Family' },
  { value: 'duplex', label: 'Duplex' },
  { value: 'townhouse', label: 'Townhouse' },
  { value: 'commercial_retail', label: 'Commercial Retail' },
  { value: 'mixed_use', label: 'Mixed Use' },
];

export default function AnalysisForm({ onSubmit, loading, error }: AnalysisFormProps) {
  const [address, setAddress] = useState('');
  const [parcelId, setParcelId] = useState('');
  const [acquisitionCost, setAcquisitionCost] = useState('');
  const [targetUse, setTargetUse] = useState('multi_unit_rental');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      address: address || undefined,
      parcel_id: parcelId || undefined,
      acquisition_cost: acquisitionCost ? parseFloat(acquisitionCost) : undefined,
      target_use: targetUse,
    });
  };

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-800 mb-1">Analyze Property</h2>
      <p className="text-sm text-gray-500 mb-6">
        Enter property details to generate AI-powered development scenarios
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Property Address
          </label>
          <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="123 Bank Street, Ottawa, ON"
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm px-3 py-2 border"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Parcel ID
          </label>
          <input
            type="text"
            value={parcelId}
            onChange={(e) => setParcelId(e.target.value)}
            placeholder="02735-0123"
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm px-3 py-2 border"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Acquisition Cost ($)
          </label>
          <input
            type="number"
            value={acquisitionCost}
            onChange={(e) => setAcquisitionCost(e.target.value)}
            placeholder="850000"
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm px-3 py-2 border"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Target Use
          </label>
          <select
            value={targetUse}
            onChange={(e) => setTargetUse(e.target.value)}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm px-3 py-2 border"
          >
            {TARGET_USE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || (!address && !parcelId)}
          className="w-full bg-primary-600 text-white py-2.5 px-4 rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
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
              Analyzing...
            </span>
          ) : (
            'Run Analysis'
          )}
        </button>
      </form>

      <div className="mt-8 p-4 bg-gray-50 rounded-lg text-xs text-gray-500">
        <p className="font-medium text-gray-600 mb-1">How it works</p>
        <ol className="list-decimal list-inside space-y-1">
          <li>Enter a property address or parcel ID</li>
          <li>We aggregate zoning, survey, and market data</li>
          <li>AI analyzes development potential and generates scenarios</li>
          <li>Review costs, ROI projections, and risk factors</li>
        </ol>
      </div>
    </div>
  );
}
