export function formatCurrency(value?: number | null): string {
    if (value === undefined || value === null) return 'Data unavailable';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

export function formatLargeNumber(value?: number | null): string {
    if (value === undefined || value === null) return 'Data unavailable';
    if (Math.abs(value) >= 1e12) {
        return `$${(value / 1e12).toFixed(2)}T`;
    }
    if (Math.abs(value) >= 1e9) {
        return `$${(value / 1e9).toFixed(2)}B`;
    }
    if (Math.abs(value) >= 1e6) {
        return `$${(value / 1e6).toFixed(2)}M`;
    }
    return formatCurrency(value);
}

export function formatVolume(value?: number | null): string {
    if (value === undefined || value === null) return 'Data unavailable';
    if (value >= 1e9) {
        return `${(value / 1e9).toFixed(2)}B`;
    }
    if (value >= 1e6) {
        return `${(value / 1e6).toFixed(2)}M`;
    }
    if (value >= 1e3) {
        return `${(value / 1e3).toFixed(2)}K`;
    }
    return value.toString();
}

export function formatPercentagePoints(value?: number | null): string {
    if (value === undefined || value === null) return 'Data unavailable';
    return `${value.toFixed(2)}%`;
}

export function formatFractionAsPercentage(value?: number | null): string {
    if (value === undefined || value === null) return 'Data unavailable';
    return `${(value * 100).toFixed(2)}%`;
}

export function formatRatio(value?: number | null): string {
    if (value === undefined || value === null) return 'Data unavailable';
    return `${value.toFixed(2)}x`;
}

export function formatDecimal(value?: number | null): string {
    if (value === undefined || value === null) return 'Data unavailable';
    return value.toFixed(2);
}

export function formatDate(dateString?: string | null): string {
    if (!dateString) return 'Data unavailable';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    return new Intl.DateTimeFormat('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric'
    }).format(date);
}
