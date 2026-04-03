'use client';

interface PermissionRequest {
  id: string;
  tool: string;
  description: string;
  risk: 'low' | 'medium' | 'high';
  command?: string;
}

interface Props {
  request: PermissionRequest;
  onApprove: (id: string) => void;
  onDeny: (id: string) => void;
}

const RISK_COLORS = {
  low: 'border-karma-accent2',
  medium: 'border-yellow-400',
  high: 'border-karma-danger',
};

const RISK_LABELS = {
  low: 'LOW RISK',
  medium: 'MEDIUM RISK',
  high: 'HIGH RISK',
};

export function PermissionDialog({ request, onApprove, onDeny }: Props) {
  return (
    <div className={`border ${RISK_COLORS[request.risk]} bg-karma-surface rounded p-3 my-2 text-[11px]`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-karma-accent font-mono font-bold">{request.tool}</span>
        <span className={`text-[9px] tracking-[1px] ${
          request.risk === 'high' ? 'text-karma-danger' :
          request.risk === 'medium' ? 'text-yellow-400' : 'text-karma-accent2'
        }`}>
          {RISK_LABELS[request.risk]}
        </span>
      </div>

      <div className="text-karma-text mb-2">{request.description}</div>

      {request.command && (
        <div className="bg-karma-bg border border-karma-border rounded px-2 py-1 font-mono text-[10px] text-karma-muted mb-2 overflow-x-auto">
          {request.command}
        </div>
      )}

      <div className="flex gap-2 justify-end">
        <button
          onClick={() => onDeny(request.id)}
          className="px-3 py-1 text-[10px] border border-karma-border text-karma-muted hover:text-karma-danger
                     hover:border-karma-danger cursor-pointer bg-transparent"
        >
          DENY
        </button>
        <button
          onClick={() => onApprove(request.id)}
          className="px-3 py-1 text-[10px] border border-karma-accent text-karma-accent hover:bg-karma-accent/20
                     cursor-pointer bg-transparent"
        >
          APPROVE
        </button>
      </div>
    </div>
  );
}
