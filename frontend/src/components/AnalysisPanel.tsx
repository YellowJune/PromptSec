import Heatmap from './Heatmap';
import { Activity } from 'lucide-react';

interface AnalysisResult {
  prompt: string;
  model_name: string;
  token_influence_scores: { token: string; influence_by_layer: Record<string, number> }[];
  heatmap_data: number[][];
  tokens: string[];
  layers: string[];
}

interface AnalysisPanelProps {
  result: AnalysisResult | null;
  loading: boolean;
}

export default function AnalysisPanel({ result, loading }: AnalysisPanelProps) {
  if (loading) {
    return (
      <div className="rounded-xl border border-border p-6 bg-card animate-pulse">
        <div className="h-6 bg-muted rounded w-1/3 mb-4" />
        <div className="h-64 bg-muted rounded" />
      </div>
    );
  }

  if (!result) {
    return (
      <div className="rounded-xl border border-border p-6 bg-card text-center text-muted-foreground">
        <Activity className="mx-auto mb-3 opacity-50" size={40} />
        <p>Submit a prompt to see the information flow analysis.</p>
      </div>
    );
  }

  // Find top influential tokens
  const tokenInfluences = result.token_influence_scores.map(t => {
    const avgInfluence = Object.values(t.influence_by_layer).reduce((a, b) => a + Math.abs(b), 0)
      / Object.values(t.influence_by_layer).length;
    return { token: t.token, avgInfluence };
  }).sort((a, b) => b.avgInfluence - a.avgInfluence);

  const topTokens = tokenInfluences.slice(0, 5);

  return (
    <div className="rounded-xl border border-border p-6 bg-card space-y-4">
      <div className="flex items-center gap-2 mb-2">
        <Activity size={20} className="text-primary" />
        <h3 className="text-lg font-semibold">Information Flow Analysis</h3>
      </div>

      <div className="text-sm text-muted-foreground mb-2">
        Model: <span className="text-foreground font-mono">{result.model_name}</span> |
        Tokens: <span className="text-foreground">{result.tokens.length}</span> |
        Layers: <span className="text-foreground">{result.layers.length}</span>
      </div>

      {/* Heatmap */}
      <div className="bg-secondary/20 rounded-lg p-4 overflow-x-auto">
        <Heatmap
          heatmapData={result.heatmap_data}
          tokens={result.tokens}
          layers={result.layers}
        />
      </div>

      {/* Top Influential Tokens */}
      {topTokens.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-muted-foreground mb-2">Most Influential Tokens</h4>
          <div className="flex flex-wrap gap-2">
            {topTokens.map((t, i) => (
              <div key={i} className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-secondary/50 border border-border">
                <span className="text-sm font-mono text-primary">{t.token}</span>
                <span className="text-xs text-muted-foreground">
                  {t.avgInfluence.toFixed(4)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
