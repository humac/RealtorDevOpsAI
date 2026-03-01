import type { AnalysisResponse } from '../../types';

interface ZoningTabProps {
  analysis: AnalysisResponse;
}

export default function ZoningTab({ analysis }: ZoningTabProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Zoning Classification</h3>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-2xl font-bold text-blue-800">{analysis.zoning_code}</p>
          <p className="text-sm text-blue-600 mt-1">Ottawa Zoning By-law 2008-250</p>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Zoning Analysis</h3>
        <div className="prose prose-sm max-w-none text-gray-700 bg-gray-50 rounded-lg p-4">
          <p>{analysis.zoning_summary || 'Zoning summary not available.'}</p>
        </div>
      </div>

      {analysis.scenarios.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Development Implications</h3>
          <div className="space-y-3">
            {analysis.scenarios.map((scenario, idx) => (
              <div key={idx} className="border rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-gray-800">{scenario.title}</p>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full ${
                      scenario.confidence_level === 'high'
                        ? 'bg-green-100 text-green-700'
                        : scenario.confidence_level === 'medium'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {scenario.confidence_level} confidence
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <span className="text-gray-500">Units:</span>{' '}
                    <span className="font-medium">{scenario.proposed_units ?? 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Storeys:</span>{' '}
                    <span className="font-medium">{scenario.proposed_storeys ?? 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">GFA:</span>{' '}
                    <span className="font-medium">
                      {scenario.proposed_gfa_sqft?.toLocaleString() ?? 'N/A'} sqft
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Risks related to zoning */}
      {analysis.scenarios.some((s) => s.risks.length > 0) && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Zoning Risks & Approvals</h3>
          <div className="space-y-2">
            {analysis.scenarios.flatMap((s) =>
              s.risks.map((risk, i) => (
                <div
                  key={`${s.title}-${i}`}
                  className="bg-red-50 border-l-4 border-red-400 px-3 py-2 text-sm text-red-700"
                >
                  {risk}
                </div>
              )),
            )}
          </div>
        </div>
      )}
    </div>
  );
}
