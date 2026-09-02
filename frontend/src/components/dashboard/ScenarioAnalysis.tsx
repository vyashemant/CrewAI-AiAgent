import { GitMerge } from 'lucide-react';
import type { InvestmentStrategy } from '../../types/api';

interface Props {
    strategy: InvestmentStrategy;
}

export function ScenarioAnalysis({ strategy }: Props) {
    return (
        <div className="panel">
            <div className="panel-header">
                <div className="panel-title">
                    <GitMerge size={16} />
                    Investment Case Scenarios
                </div>
            </div>
            
            <div className="grid-3" style={{ alignItems: 'start' }}>
                <div className="scenario-case bull">
                    <div className="scenario-title" style={{ color: 'var(--success)' }}>Bull Case</div>
                    <div style={{ fontSize: '0.875rem', lineHeight: 1.6, color: 'var(--text-secondary)' }}>
                        {strategy.bull_case}
                    </div>
                </div>
                
                <div className="scenario-case base">
                    <div className="scenario-title" style={{ color: 'var(--accent-light)' }}>Base Case</div>
                    <div style={{ fontSize: '0.875rem', lineHeight: 1.6, color: 'var(--text-secondary)' }}>
                        {strategy.base_case}
                    </div>
                </div>
                
                <div className="scenario-case bear">
                    <div className="scenario-title" style={{ color: 'var(--danger)' }}>Bear Case</div>
                    <div style={{ fontSize: '0.875rem', lineHeight: 1.6, color: 'var(--text-secondary)' }}>
                        {strategy.bear_case}
                    </div>
                </div>
            </div>
        </div>
    );
}
