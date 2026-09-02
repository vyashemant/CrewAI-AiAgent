import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { BarChart3 } from 'lucide-react';
import type { EvidenceRegistry } from '../../types/api';
import { formatLargeNumber } from '../../utils/formatters';

interface Props {
    registry?: EvidenceRegistry | null;
}

export function FinancialPerformance({ registry }: Props) {
    if (!registry || !registry.evidence) {
        return (
            <div className="panel" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <div className="panel-header">
                    <div className="panel-title"><BarChart3 size={16} /> Financial Performance</div>
                </div>
                <div style={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                    Data Unavailable
                </div>
            </div>
        );
    }

    // Try to extract historical revenue or margins from evidence registry
    // evidence items might look like: claim="Revenue", period="FY2023", value="383.28B"
    const parseValue = (valStr: any) => {
        if (typeof valStr === 'number') return valStr;
        if (typeof valStr !== 'string') return null;
        const clean = valStr.replace(/[^0-9.-]/g, '');
        return clean ? parseFloat(clean) : null;
    };

    const periods = new Set<string>();
    const dataByPeriod: Record<string, any> = {};

    registry.evidence.forEach(item => {
        if (item.period && (item.claim.toLowerCase().includes('revenue') || item.claim.toLowerCase().includes('margin'))) {
            periods.add(item.period);
            if (!dataByPeriod[item.period]) {
                dataByPeriod[item.period] = { period: item.period };
            }
            if (item.claim.toLowerCase().includes('revenue')) {
                dataByPeriod[item.period].Revenue = parseValue(item.value);
            }
            if (item.claim.toLowerCase().includes('gross margin')) {
                dataByPeriod[item.period].GrossMargin = parseValue(item.value);
            }
            if (item.claim.toLowerCase().includes('op margin') || item.claim.toLowerCase().includes('operating margin')) {
                dataByPeriod[item.period].OpMargin = parseValue(item.value);
            }
        }
    });

    const chartData = Array.from(periods).sort().map(p => dataByPeriod[p]);

    if (chartData.length === 0) {
        return (
            <div className="panel" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <div className="panel-header">
                    <div className="panel-title"><BarChart3 size={16} /> Financial Performance</div>
                </div>
                <div style={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                    Historical Data Unavailable
                </div>
            </div>
        );
    }

    return (
        <div className="panel" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div className="panel-header">
                <div className="panel-title"><BarChart3 size={16} /> Financial Performance</div>
            </div>
            <div style={{ flexGrow: 1, minHeight: '250px' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                        <XAxis dataKey="period" stroke="var(--text-secondary)" fontSize={12} tickLine={false} axisLine={false} />
                        <YAxis stroke="var(--text-secondary)" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => formatLargeNumber(v)} />
                        <Tooltip 
                            contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border)', color: 'var(--text-primary)', fontSize: '0.875rem' }}
                            itemStyle={{ color: 'var(--text-primary)' }}
                            formatter={(value: any) => [formatLargeNumber(value), 'Revenue']}
                        />
                        <Legend wrapperStyle={{ fontSize: '12px', color: 'var(--text-secondary)' }} />
                        <Bar dataKey="Revenue" fill="var(--accent-light)" radius={[4, 4, 0, 0]} maxBarSize={40} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
