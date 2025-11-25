/**
 * Connection Store
 * Manages backend and WebSocket connection state
 */

import {health} from '../api';
import {type ConnectionState, getWebSocketClient} from '../websocket';

// === State ===

let backendOnline = $state(false);
let wsConnectionState = $state<ConnectionState>('disconnected');
let lastError = $state<string | null>(null);
let isChecking = $state(false);

// === Backend Health ===

/**
 * Check if the backend is reachable
 */
export async function checkBackendHealth(): Promise<boolean> {
	isChecking = true;
	try {
		backendOnline = await health.checkHealth();
		if (!backendOnline) {
			lastError = 'Backend is offline';
		} else {
			lastError = null;
		}
		return backendOnline;
	} catch {
		backendOnline = false;
		lastError = 'Failed to reach backend';
		return false;
	} finally {
		isChecking = false;
	}
}

// === WebSocket Connection ===

/**
 * Connect to WebSocket
 */
export function connectWebSocket(): void {
	const client = getWebSocketClient();

	// Set up state change handler
	client.setOnStateChange((state) => {
		wsConnectionState = state;
		if (state === 'error') {
			lastError = client.lastError;
		} else if (state === 'connected') {
			lastError = null;
		}
	});

	client.setOnError((error) => {
		lastError = error;
	});

	client.connect();
}

/**
 * Disconnect WebSocket
 */
export function disconnectWebSocket(): void {
	const client = getWebSocketClient();
	client.disconnect();
	wsConnectionState = 'disconnected';
}

/**
 * Clear connection error
 */
export function clearError(): void {
	lastError = null;
}

// === Exported State ===

export function getConnectionState() {
	return {
		get backendOnline() {
			return backendOnline;
		},
		get wsConnectionState() {
			return wsConnectionState;
		},
		get isConnected() {
			return wsConnectionState === 'connected';
		},
		get isConnecting() {
			return wsConnectionState === 'connecting';
		},
		get lastError() {
			return lastError;
		},
		get isChecking() {
			return isChecking;
		}
	};
}