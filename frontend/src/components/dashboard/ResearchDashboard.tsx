import type { InvestmentResearchReport } from '../../types/api';
import { DashboardHeader } from './DashboardHeader';
import { ExecutiveMetrics } from './ExecutiveMetrics';
import { MarketSnapshotCard } from './MarketSnapshotCard';
import { FinancialHealth } from './FinancialHealth';
import { ValuationSection } from './ValuationSection';
import { InvestmentThesis } from './InvestmentThesis';
import { ScenarioAnalysis } from './ScenarioAnalysis';
import { SpecialistReportsSection } from './SpecialistReports';
import { DataSourcesSection } from './DataSources';
import { EvidencePanel } from './EvidencePanel';
import { FinancialPerformance } from './FinancialPerformance';
import '../../styles/dashboard.css';

interface Props {
    report: InvestmentResearchReport;
}

export function ResearchDashboard({ report }: Props) {
    return (
        <div className="dashboard-container">
            <DashboardHeader report={report} />

            <div className="grid-3">
                <div style={{ gridColumn: 'span 2' }}>
                    <InvestmentThesis strategy={report.investment_strategy} />
                    <ExecutiveMetrics summary={report.financial_summary} metrics={report.financial_metrics} />
                </div>
                <div>
                    <MarketSnapshotCard snapshot={report.market_snapshot} />
                </div>
            </div>

            <div className="grid-2">
                <div>
                    <FinancialPerformance registry={report.evidence_registry} />
                </div>
                <div>
                    <ValuationSection registry={report.evidence_registry} />
                </div>
            </div>

            <div style={{ marginTop: '1.5rem' }}>
                <FinancialHealth summary={report.financial_summary} metrics={report.financial_metrics} />
            </div>

            <div style={{ marginTop: '1.5rem' }}>
                <ScenarioAnalysis strategy={report.investment_strategy} />
            </div>

            <div style={{ marginTop: '1.5rem' }}>
                <SpecialistReportsSection reports={report.specialist_reports} />
            </div>

            <div style={{ marginTop: '1.5rem' }}>
                <EvidencePanel registry={report.evidence_registry} />
            </div>

            <div style={{ marginTop: '1.5rem', marginBottom: '3rem' }}>
                <DataSourcesSection sources={report.data_sources} />
            </div>
        </div>
    );
}
