import { scoreColor, scoreBgColor } from '../../utils/format';

interface HeaderProps {
  opportunityScore: number | null;
  onNewAnalysis: () => void;
}

export default function Header({ opportunityScore, onNewAnalysis }: HeaderProps) {
  return (
    <header className="bg-primary-900 text-white px-6 py-3 flex items-center justify-between shadow-md">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold tracking-tight">RealtorDevOpsAI</h1>
        <span className="text-primary-300 text-sm">Ottawa Development Analysis</span>
      </div>

      {opportunityScore !== null && (
        <div className="flex items-center gap-4">
          <div
            className={`px-4 py-1 rounded-full border font-semibold text-sm ${scoreBgColor(opportunityScore)}`}
          >
            <span className={scoreColor(opportunityScore)}>
              Opportunity Score: {opportunityScore.toFixed(0)}/100
            </span>
          </div>
          <button
            onClick={onNewAnalysis}
            className="text-sm bg-primary-700 hover:bg-primary-600 px-3 py-1 rounded transition-colors"
          >
            New Analysis
          </button>
        </div>
      )}
    </header>
  );
}
