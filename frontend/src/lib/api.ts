// API configuration and helper functions
const API_BASE = 'http://localhost:8000';

export interface Module {
    name: string;
    display_name: string;
    enabled: boolean;
    initialized: boolean;
}

export interface ModulesResponse {
    modules: Module[];
}

/**
 * Fetch all modules from the backend
 */
export async function fetchModules(): Promise<Module[]> {
    const response = await fetch(`${API_BASE}/api/modules`);
    if (!response.ok) {
        throw new Error(`Failed to fetch modules: ${response.statusText}`);
    }
    const data: ModulesResponse = await response.json();
    return data.modules;
}

/**
 * Enable a module
 */
export async function enableModule(name: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/modules/${name}/enable`, {
        method: 'POST',
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `Failed to enable module: ${response.statusText}`);
    }
}

/**
 * Disable a module
 */
export async function disableModule(name: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/modules/${name}/disable`, {
        method: 'POST',
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `Failed to disable module: ${response.statusText}`);
    }
}

/**
 * Check if the backend is healthy
 */
export async function checkHealth(): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE}/health`);
        return response.ok;
    } catch {
        return false;
    }
}