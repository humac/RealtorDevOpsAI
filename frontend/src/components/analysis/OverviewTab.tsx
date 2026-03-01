import type { AnalysisResponse } from '../../types';
import { formatCurrency, formatNumber, scoreColor } from '../../utils/format';

interface OverviewTabProps {
  analysis: AnalysisResponse;
}

export default function OverviewTab({ analysis }: OverviewTabProps) {
  const bestScenario = analysis.scenarios.reduce(
    (best, s) => (s.opportunity_score > (best?.opportunity_score ?? 0) ? s : best),
    analysis.scenarios[0],
  );

  return (
    <div className="space-y-6">
      {/* Property summary */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Property Summary</h3>
        <div className="grid grid-cols-2 gap-3">
          <InfoCard label="Address" value={analysis.address} />
          <InfoCard label="Parcel ID" value={analysis.parcel_id} />
          <InfoCard label="Zoning" value={analysis.zoning_code} />
          <InfoCard label="Lot Size" value={`${formatNumber(analysis.lot_area_sqft)} sq ft`} />
        </div>
      </div>

      {/* Opportunity score */}
      <div className="bg-white border rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Overall Opportunity Score</p>
            <p className={`text-4xl font-bold ${scoreColor(analysis.overall_opportunity_score)}`}>
              {analysis.overall_opportunity_score.toFixed(0)}
              <span className="text-lg text-gray-400">/100</span>
            </p>
          </div>
          <div className="w-32 h-32 relative">
            <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="#e5e7eb"
                strokeWidth="3"
              />
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke={analysis.overall_opportunity_score >= 70 ? '#10b981' : analysis.overall_opportunity_score >= 40 ? '#f59e0b' : '#ef4444'}
                strokeWidth="3"
                strokeDasharray={`${analysis.overall_opportunity_score}, 100`}
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Key metrics */}
      {bestScenario && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Best Scenario Highlights</h3>
          <div className="grid grid-cols-2 gap-3">
            <MetricCard
              label="Scenario"
              value={bestScenario.title}
              color="blue"
            />
            <MetricCard
              label="Total Cost"
              value={formatCurrency(bestScenario.costs.total)}
              color="gray"
            />
            <MetricCard
              label="ROI"
              value={`${bestScenario.roi_metrics.roi_pct.toFixed(1)}%`}
              color="green"
            />
            <MetricCard
              label="Timeline"
              value={`${bestScenario.timeline_months} months`}
              color="purple"
            />
          </div>
        </div>
      )}

      {/* Scenarios overview */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-3">
          {analysis.scenarios.length} Scenarios Generated
        </h3>
        <div className="space-y-2">
          {analysis.scenarios.map((scenario, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div>
                <p className="text-sm font-medium text-gray-800">{scenario.title}</p>
                <p className="text-xs text-gray-500">
                  {scenario.proposed_units} units | {scenario.timeline_months} months
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-green-600">
                  ROI: {scenario.roi_metrics.roi_pct.toFixed(1)}%
                </p>
                <p className={`text-xs ${scoreColor(scenario.opportunity_score)}`}>
                  Score: {scenario.opportunity_score.toFixed(0)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-lg p-3">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm font-medium text-gray-800">{value}</p>
    </div>
  );
}

function MetricCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: string;
}) {
  const colorClasses: Record<string, string> = {
    blue: 'bg-blue-50 border-blue-200',
    green: 'bg-green-50 border-green-200',
    gray: 'bg-gray-50 border-gray-200',
    purple: 'bg-purple-50 border-purple-200',
  };

  return (
    <div className={`rounded-lg p-3 border ${colorClasses[color] || colorClasses.gray}`}>
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm font-semibold text-gray-800 truncate">{value}</p>
    </div>
  );
}
