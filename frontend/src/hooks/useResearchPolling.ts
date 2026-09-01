import { useState, useEffect, useRef } from 'react';
import { ApiClient } from '../api/client';
import type { ResearchJobResponse } from '../types/api';

export function useResearchPolling(initialJobId: string | null) {
    const [jobId, setJobId] = useState<string | null>(initialJobId);
    const [status, setStatus] = useState<string | null>(null);
    const [result, setResult] = useState<ResearchJobResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    
    const pollingRef = useRef<number | null>(null);
    const isMounted = useRef<boolean>(true);
    const isPolling = useRef<boolean>(false);

    useEffect(() => {
        isMounted.current = true;
        return () => {
            isMounted.current = false;
        };
    }, []);

    useEffect(() => {
        if (!jobId) {
            setStatus(null);
            setResult(null);
            setError(null);
            return;
        }

        const poll = async () => {
            if (isPolling.current) return;
            isPolling.current = true;
            
            try {
                const response = await ApiClient.getResearchStatus(jobId);
                
                if (!isMounted.current) return;

                setStatus(response.status);
                setResult(response);
                
                if (response.status === 'completed' || response.status === 'failed') {
                    if (pollingRef.current) {
                        window.clearInterval(pollingRef.current);
                        pollingRef.current = null;
                    }
                }
            } catch (err: any) {
                if (!isMounted.current) return;
                console.error("Polling error", err);
                setError(err.message || 'Error occurred while polling status.');
                if (pollingRef.current) {
                    window.clearInterval(pollingRef.current);
                    pollingRef.current = null;
                }
            } finally {
                isPolling.current = false;
            }
        };

        // Poll immediately once
        poll();
        
        // Then poll every 3 seconds
        pollingRef.current = window.setInterval(poll, 3000);

        return () => {
            if (pollingRef.current) {
                window.clearInterval(pollingRef.current);
                pollingRef.current = null;
            }
        };
    }, [jobId]);

    return { jobId, setJobId, status, result, error, setError };
}
