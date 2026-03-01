import { useState } from 'react';
import type { AnalysisResponse, Scenario } from '../../types';
import {
  formatCurrency,
  formatPercent,
  scoreColor,
  confidenceBadge,
} from '../../utils/format';

interface ScenariosTabProps {
  analysis: AnalysisResponse;
}

export default function ScenariosTab({ analysis }: ScenariosTabProps) {
  const [selectedIdx, setSelectedIdx] = useState<number>(0);

  if (analysis.scenarios.length === 0) {
    return <p className="text-gray-500">No scenarios generated.</p>;
  }

  const selected = analysis.scenarios[selectedIdx];

  return (
    <div className="space-y-6">
      {/* Scenario selector */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {analysis.scenarios.map((scenario, idx) => (
          <button
            key={idx}
            onClick={() => setSelectedIdx(idx)}
            className={`flex-shrink-0 px-3 py-2 rounded-lg text-sm transition-colors ${
              selectedIdx === idx
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {scenario.title}
          </button>
        ))}
      </div>

      {/* Selected scenario detail */}
      {selected && <ScenarioDetail scenario={selected} />}

      {/* Side-by-side comparison button */}
      {analysis.scenarios.length > 1 && (
        <div className="text-center">
          <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
            Compare All Scenarios Side-by-Side
          </button>
        </div>
      )}
    </div>
  );
}

function ScenarioDetail({ scenario }: { scenario: Scenario }) {
  return (
    <div className="space-y-5">
      {/* Header */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <h3 className="text-lg font-semibold text-gray-800">{scenario.title}</h3>
          <span className={`text-xs px-2 py-0.5 rounded-full ${confidenceBadge(scenario.confidence_level)}`}>
            {scenario.confidence_level}
          </span>
        </div>
        <p className="text-sm text-gray-600">{scenario.description}</p>
      </div>

      {/* Key metrics grid */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-blue-50 rounded-lg p-3">
          <p className="text-xs text-blue-500">Total Investment</p>
          <p className="text-xl font-bold text-blue-800">{formatCurrency(scenario.costs.total)}</p>
        </div>
        <div className="bg-green-50 rounded-lg p-3">
          <p className="text-xs text-green-500">ROI</p>
          <p className="text-xl font-bold text-green-800">
            {formatPercent(scenario.roi_metrics.roi_pct)}
          </p>
        </div>
        <div className="bg-purple-50 rounded-lg p-3">
          <p className="text-xs text-purple-500">Profit</p>
          <p className="text-xl font-bold text-purple-800">
            {formatCurrency(scenario.roi_metrics.profit)}
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-500">Timeline</p>
          <p className="text-xl font-bold text-gray-800">{scenario.timeline_months} months</p>
        </div>
      </div>

      {/* Development details */}
      <div>
        <h4 className="text-sm font-semibold text-gray-700 mb-2">Development Details</h4>
        <div className="grid grid-cols-3 gap-2 text-sm">
          <DetailItem label="Units" value={scenario.proposed_units?.toString() ?? 'N/A'} />
          <DetailItem label="Storeys" value={scenario.proposed_storeys?.toString() ?? 'N/A'} />
          <DetailItem
            label="GFA"
            value={scenario.proposed_gfa_sqft ? `${scenario.proposed_gfa_sqft.toLocaleString()} sqft` : 'N/A'}
          />
        </div>
      </div>

      {/* Additional ROI metrics */}
      <div>
        <h4 className="text-sm font-semibold text-gray-700 mb-2">Financial Metrics</h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <DetailItem label="Profit Margin" value={formatPercent(scenario.roi_metrics.profit_margin_pct)} />
          <DetailItem label="IRR" value={scenario.roi_metrics.irr_pct != null ? formatPercent(scenario.roi_metrics.irr_pct) : 'N/A'} />
          <DetailItem label="Cap Rate" value={scenario.roi_metrics.cap_rate_pct != null ? formatPercent(scenario.roi_metrics.cap_rate_pct) : 'N/A'} />
          <DetailItem label="Cash-on-Cash" value={scenario.roi_metrics.cash_on_cash_pct != null ? formatPercent(scenario.roi_metrics.cash_on_cash_pct) : 'N/A'} />
        </div>
      </div>

      {/* Opportunity score */}
      <div className="flex items-center gap-3 p-3 border rounded-lg">
        <div
          className={`text-3xl font-bold ${scoreColor(scenario.opportunity_score)}`}
        >
          {scenario.opportunity_score.toFixed(0)}
        </div>
        <div>
          <p className="text-sm font-medium text-gray-800">Opportunity Score</p>
          <p className="text-xs text-gray-500">
            {scenario.opportunity_score >= 70
              ? 'Strong opportunity'
              : scenario.opportunity_score >= 40
                ? 'Moderate opportunity'
                : 'Challenging opportunity'}
          </p>
        </div>
      </div>

      {/* Sensitivity analysis */}
      {scenario.sensitivity_analysis && scenario.sensitivity_analysis.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Sensitivity Analysis</h4>
          <div className="space-y-2">
            {scenario.sensitivity_analysis.map((sa) => (
              <div key={sa.variable} className="bg-gray-50 rounded-lg p-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 capitalize">
                    {sa.variable.replace(/_/g, ' ')}
                  </span>
                  <span className="font-medium text-gray-800">
                    +/- {formatPercent(sa.impact_on_roi_pct)} ROI impact
                  </span>
                </div>
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>Low: {formatCurrency(sa.low_case)}</span>
                  <span>Base: {formatCurrency(sa.base_value)}</span>
                  <span>High: {formatCurrency(sa.high_case)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Risks */}
      {scenario.risks.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Risk Factors</h4>
          <div className="space-y-1.5">
            {scenario.risks.map((risk, i) => (
              <div
                key={i}
                className="bg-amber-50 border-l-3 border-amber-400 px-3 py-2 text-sm text-amber-800 rounded-r"
              >
                {risk}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded p-2">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm font-medium text-gray-800">{value}</p>
    </div>
  );
}
