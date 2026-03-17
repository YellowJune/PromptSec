import { Swords, Loader2 } from 'lucide-react';

interface RedTeamResult {
  best_attack_prompt: string;
  attack_success_rate: number;
  generations_run: number;
  attack_details: {
    attack_success?: boolean;
    detector_bypassed?: boolean;
    attack_strength?: number;
    detector_risk_score?: number;
  };
}

interface RedTeamPanelProps {
  result: RedTeamResult | null;
  loading: boolean;
  onRun: (config: { target_vulnerability: string; num_generations: number; population_size: number }) => void;
}

export default function RedTeamPanel({ result, loading, onRun }: RedTeamPanelProps) {
  const handleRun = () => {
    onRun({
      target_vulnerability: 'data_exfiltration',
      num_generations: 5,
      population_size: 20,
    });
  };

  return (
    <div className="rounded-xl border border-border p-6 bg-card space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Swords size={20} className="text-red-400" />
          Red Team Engine
        </h3>
        <button
          onClick={handleRun}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 size={14} className="animate-spin" />
              Running...
            </>
          ) : (
            'Run Campaign'
          )}
        </button>
      </div>

      {!result && !loading && (
        <p className="text-sm text-muted-foreground">
          Run an automated red team campaign to discover adversarial prompts using genetic algorithms.
        </p>
      )}

      {result && (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-lg border border-border p-3 bg-secondary/30">
              <div className="text-xs text-muted-foreground">Generations</div>
              <div className="text-xl font-mono font-bold">{result.generations_run}</div>
            </div>
            <div className="rounded-lg border border-border p-3 bg-secondary/30">
              <div className="text-xs text-muted-foreground">Success Rate</div>
              <div className="text-xl font-mono font-bold">
                {(result.attack_success_rate * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          <div className="rounded-lg border border-border p-3 bg-secondary/30">
            <div className="text-xs text-muted-foreground mb-1">Best Attack Prompt</div>
            <p className="text-sm font-mono text-red-300 bg-red-950/30 rounded p-2">
              {result.best_attack_prompt}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-lg border border-border p-2 text-center">
              <div className="text-xs text-muted-foreground">Attack Success</div>
              <div className={`text-sm font-bold ${result.attack_details.attack_success ? 'text-red-400' : 'text-green-400'}`}>
                {result.attack_details.attack_success ? 'YES' : 'NO'}
              </div>
            </div>
            <div className="rounded-lg border border-border p-2 text-center">
              <div className="text-xs text-muted-foreground">Detector Bypassed</div>
              <div className={`text-sm font-bold ${result.attack_details.detector_bypassed ? 'text-red-400' : 'text-green-400'}`}>
                {result.attack_details.detector_bypassed ? 'YES' : 'NO'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
