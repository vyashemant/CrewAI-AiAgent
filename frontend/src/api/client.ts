import type { ResearchRequest, ResearchJobResponse, ResearchHistoryResponse } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export class ApiClient {
    private static async fetchWithHandling(url: string, options?: RequestInit) {
        try {
            const response = await fetch(`${API_BASE_URL}${url}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options?.headers,
                },
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    static async checkHealth(): Promise<{ status: string }> {
        return this.fetchWithHandling('/health');
    }

    static async submitResearch(data: ResearchRequest): Promise<ResearchJobResponse> {
        return this.fetchWithHandling('/api/v1/research', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    static async getResearchStatus(jobId: string): Promise<ResearchJobResponse> {
        return this.fetchWithHandling(`/api/v1/research/${jobId}`);
    }

    static async getResearchHistory(limit: number = 20): Promise<ResearchHistoryResponse> {
        return this.fetchWithHandling(`/api/v1/research/history?limit=${limit}`);
    }
}
