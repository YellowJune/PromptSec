import { Shield, ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

interface DetectionResult {
  risk_score: number;
  label: string;
  details: {
    rule_engine?: { score: number; matched_rules: string[] };
    heuristic_analyzer?: { score: number; detected_heuristics: string[] };
    llm_classifier?: { is_attack: boolean; confidence: number; attack_types: string[] };
  };
}

interface DetectionPanelProps {
  result: DetectionResult | null;
  loading: boolean;
}

export default function DetectionPanel({ result, loading }: DetectionPanelProps) {
  if (loading) {
    return (
      <div className="rounded-xl border border-border p-6 bg-card animate-pulse">
        <div className="h-6 bg-muted rounded w-1/3 mb-4" />
        <div className="h-20 bg-muted rounded" />
      </div>
    );
  }

  if (!result) {
    return (
      <div className="rounded-xl border border-border p-6 bg-card text-center text-muted-foreground">
        <Shield className="mx-auto mb-3 opacity-50" size={40} />
        <p>Submit a prompt to analyze its security risk.</p>
      </div>
    );
  }

  const getLabelColor = (label: string) => {
    switch (label) {
      case 'attack': return 'text-red-400 bg-red-950 border-red-800';
      case 'suspicious': return 'text-yellow-400 bg-yellow-950 border-yellow-800';
      case 'safe': return 'text-green-400 bg-green-950 border-green-800';
      default: return 'text-muted-foreground bg-muted border-border';
    }
  };

  const getLabelIcon = (label: string) => {
    switch (label) {
      case 'attack': return <ShieldAlert size={24} className="text-red-400" />;
      case 'suspicious': return <AlertTriangle size={24} className="text-yellow-400" />;
      case 'safe': return <ShieldCheck size={24} className="text-green-400" />;
      default: return <Shield size={24} />;
    }
  };

  const riskPercent = Math.round(result.risk_score * 100);
  const riskBarColor = result.label === 'attack' ? 'bg-red-500' :
    result.label === 'suspicious' ? 'bg-yellow-500' : 'bg-green-500';

  return (
    <div className="rounded-xl border border-border p-6 bg-card space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          {getLabelIcon(result.label)}
          Detection Result
        </h3>
        <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getLabelColor(result.label)}`}>
          {result.label.toUpperCase()}
        </span>
      </div>

      {/* Risk Score Bar */}
      <div>
        <div className="flex justify-between text-sm mb-1">
          <span className="text-muted-foreground">Risk Score</span>
          <span className="font-mono font-bold">{riskPercent}%</span>
        </div>
        <div className="w-full h-3 bg-muted rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${riskBarColor}`}
            style={{ width: `${riskPercent}%` }}
          />
        </div>
      </div>

      {/* Detection Details */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
        {/* Rule Engine */}
        <div className="rounded-lg border border-border p-3 bg-secondary/30">
          <div className="text-xs text-muted-foreground mb-1">Rule Engine</div>
          <div className="text-lg font-mono font-bold">
            {((result.details.rule_engine?.score ?? 0) * 100).toFixed(0)}%
          </div>
          {result.details.rule_engine?.matched_rules && result.details.rule_engine.matched_rules.length > 0 && (
            <div className="mt-1 flex flex-wrap gap-1">
              {result.details.rule_engine.matched_rules.map((rule, i) => (
                <span key={i} className="text-xs px-1.5 py-0.5 rounded bg-red-950 text-red-300 border border-red-800">
                  {rule}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Heuristic */}
        <div className="rounded-lg border border-border p-3 bg-secondary/30">
          <div className="text-xs text-muted-foreground mb-1">Heuristic</div>
          <div className="text-lg font-mono font-bold">
            {((result.details.heuristic_analyzer?.score ?? 0) * 100).toFixed(0)}%
          </div>
          {result.details.heuristic_analyzer?.detected_heuristics && result.details.heuristic_analyzer.detected_heuristics.length > 0 && (
            <div className="mt-1 flex flex-wrap gap-1">
              {result.details.heuristic_analyzer.detected_heuristics.map((h, i) => (
                <span key={i} className="text-xs px-1.5 py-0.5 rounded bg-yellow-950 text-yellow-300 border border-yellow-800">
                  {h}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* LLM Classifier */}
        <div className="rounded-lg border border-border p-3 bg-secondary/30">
          <div className="text-xs text-muted-foreground mb-1">LLM Classifier</div>
          <div className="text-lg font-mono font-bold">
            {((result.details.llm_classifier?.confidence ?? 0) * 100).toFixed(0)}%
          </div>
          {result.details.llm_classifier?.attack_types && result.details.llm_classifier.attack_types.length > 0 && (
            <div className="mt-1 flex flex-wrap gap-1">
              {result.details.llm_classifier.attack_types.map((t, i) => (
                <span key={i} className="text-xs px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
