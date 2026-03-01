import type { AnalysisResponse, Scenario } from '../../types';
import { formatCurrency, formatPercent } from '../../utils/format';

interface CostsTabProps {
  analysis: AnalysisResponse;
}

export default function CostsTab({ analysis }: CostsTabProps) {
  if (analysis.scenarios.length === 0) {
    return <p className="text-gray-500">No scenarios available for cost analysis.</p>;
  }

  return (
    <div className="space-y-6">
      {analysis.scenarios.map((scenario, idx) => (
        <ScenarioCostCard key={idx} scenario={scenario} index={idx} />
      ))}

      {/* Comparison table */}
      {analysis.scenarios.length > 1 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Cost Comparison</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="text-left p-2 text-gray-600">Metric</th>
                  {analysis.scenarios.map((s, i) => (
                    <th key={i} className="text-right p-2 text-gray-600">
                      {s.title.length > 20 ? `${s.title.slice(0, 20)}...` : s.title}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <CostRow label="Total Cost" scenarios={analysis.scenarios} getValue={(s) => s.costs.total} />
                <CostRow label="Construction" scenarios={analysis.scenarios} getValue={(s) => s.costs.hard_construction} />
                <CostRow label="Soft Costs" scenarios={analysis.scenarios} getValue={(s) => s.costs.soft_costs} />
                <CostRow label="Financing" scenarios={analysis.scenarios} getValue={(s) => s.costs.financing} />
                <CostRow label="Revenue" scenarios={analysis.scenarios} getValue={(s) => s.projected_sale_revenue ?? s.projected_annual_rental ?? 0} />
                <CostRow label="Profit" scenarios={analysis.scenarios} getValue={(s) => s.roi_metrics.profit} />
                <tr className="font-semibold bg-blue-50">
                  <td className="p-2">ROI</td>
                  {analysis.scenarios.map((s, i) => (
                    <td key={i} className="text-right p-2 text-green-600">
                      {formatPercent(s.roi_metrics.roi_pct)}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function ScenarioCostCard({ scenario, index }: { scenario: Scenario; index: number }) {
  const costItems = [
    { label: 'Acquisition', value: scenario.costs.acquisition },
    { label: 'Teardown', value: scenario.costs.teardown },
    { label: 'Hard Construction', value: scenario.costs.hard_construction },
    { label: 'Soft Costs', value: scenario.costs.soft_costs },
    { label: 'Development Charges', value: scenario.costs.development_charges },
    { label: 'Permit Fees', value: scenario.costs.permit_fees },
    { label: 'Financing', value: scenario.costs.financing },
    { label: 'HST (Net)', value: scenario.costs.hst },
  ].filter((item) => item.value > 0);

  return (
    <div className="border rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-800">
          {index + 1}. {scenario.title}
        </h3>
        <span className="text-lg font-bold text-gray-800">
          {formatCurrency(scenario.costs.total)}
        </span>
      </div>

      <div className="space-y-1.5">
        {costItems.map((item) => (
          <div key={item.label} className="flex justify-between text-sm">
            <span className="text-gray-500">{item.label}</span>
            <span className="text-gray-800">{formatCurrency(item.value)}</span>
          </div>
        ))}
        <div className="flex justify-between text-sm font-semibold border-t pt-1.5">
          <span className="text-gray-800">Total Investment</span>
          <span className="text-gray-800">{formatCurrency(scenario.costs.total)}</span>
        </div>
      </div>

      {/* ROI summary */}
      <div className="mt-3 grid grid-cols-3 gap-2">
        <MiniMetric label="ROI" value={formatPercent(scenario.roi_metrics.roi_pct)} />
        <MiniMetric label="Profit" value={formatCurrency(scenario.roi_metrics.profit)} />
        <MiniMetric
          label="IRR"
          value={scenario.roi_metrics.irr_pct != null ? formatPercent(scenario.roi_metrics.irr_pct) : 'N/A'}
        />
      </div>
    </div>
  );
}

function CostRow({
  label,
  scenarios,
  getValue,
}: {
  label: string;
  scenarios: Scenario[];
  getValue: (s: Scenario) => number;
}) {
  return (
    <tr className="border-b">
      <td className="p-2 text-gray-600">{label}</td>
      {scenarios.map((s, i) => (
        <td key={i} className="text-right p-2">
          {formatCurrency(getValue(s))}
        </td>
      ))}
    </tr>
  );
}

function MiniMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded p-2 text-center">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm font-semibold text-gray-800">{value}</p>
    </div>
  );
}
