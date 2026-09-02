import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { BookOpen, ChevronRight } from 'lucide-react';
import type { SpecialistReports } from '../../types/api';

interface Props {
    reports: SpecialistReports;
}

export function SpecialistReportsSection({ reports }: Props) {
    const [activeTab, setActiveTab] = useState<'financial' | 'market' | 'valuation' | 'risk'>('financial');

    if (!reports) return null;

    const tabs = [
        { id: 'financial', label: 'Financial Analysis', content: reports.financial_analyst },
        { id: 'market', label: 'Market & News Analysis', content: reports.market_news_analyst },
        { id: 'valuation', label: 'Valuation Analysis', content: reports.valuation_analyst },
        { id: 'risk', label: 'Risk Analysis', content: reports.risk_analyst }
    ] as const;

    const activeContent = tabs.find(t => t.id === activeTab)?.content;

    return (
        <div className="panel" style={{ padding: 0, display: 'flex', minHeight: '600px', backgroundColor: 'var(--bg-secondary)' }}>
            {/* Sidebar Navigation */}
            <div style={{ width: '240px', borderRight: '1px solid var(--border)', display: 'flex', flexDirection: 'column' }}>
                <div className="panel-header" style={{ margin: 0, padding: '1.25rem', borderBottom: '1px solid var(--border)' }}>
                    <div className="panel-title">
                        <BookOpen size={16} />
                        Detailed Research
                    </div>
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', padding: '0.75rem 0' }}>
                    {tabs.map(tab => (
                        <div 
                            key={tab.id}
                            style={{ 
                                padding: '0.75rem 1.25rem', 
                                display: 'flex', 
                                alignItems: 'center',
                                gap: '0.5rem',
                                cursor: 'pointer',
                                backgroundColor: activeTab === tab.id ? 'var(--bg-panel)' : 'transparent',
                                borderLeft: activeTab === tab.id ? '2px solid var(--accent-light)' : '2px solid transparent',
                                color: activeTab === tab.id ? 'var(--text-primary)' : 'var(--text-secondary)',
                                fontSize: '0.875rem',
                                fontWeight: activeTab === tab.id ? 600 : 500,
                                transition: 'all 0.2s'
                            }}
                            onClick={() => setActiveTab(tab.id as any)}
                        >
                            <ChevronRight size={14} style={{ opacity: activeTab === tab.id ? 1 : 0 }} />
                            {tab.label}
                        </div>
                    ))}
                </div>
            </div>

            {/* Reader Pane */}
            <div style={{ flexGrow: 1, backgroundColor: 'var(--bg-panel)', padding: '2rem', overflowY: 'auto' }}>
                <h2 style={{ fontSize: '1.5rem', marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border)' }}>
                    {tabs.find(t => t.id === activeTab)?.label}
                </h2>
                <div className="prose-content markdown-wrapper" style={{ fontSize: '0.9375rem', lineHeight: 1.6, color: 'var(--text-primary)' }}>
                    {activeContent ? <ReactMarkdown>{activeContent}</ReactMarkdown> : <p>Data unavailable</p>}
                </div>
            </div>
        </div>
    );
}
