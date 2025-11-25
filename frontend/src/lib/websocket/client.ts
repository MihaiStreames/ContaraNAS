/**
 * WebSocket Client
 * Manages WebSocket connection with auto-reconnect
 */

import {API_CONFIG} from '../api/config';
import {getStoredToken} from '../api/client';
import type {
	ConnectionState,
	IncomingMessage,
	InitialStateMessage,
	ModuleStateMessage,
	OutgoingMessage,
	SteamLibraryMessage,
	SystemStatsMessage
} from './types';

export type MessageHandler<T extends IncomingMessage = IncomingMessage> = (message: T) => void;

interface WebSocketClientOptions {
	reconnectInterval?: number;
	maxReconnectAttempts?: number;
	pingInterval?: number;
}

const DEFAULT_OPTIONS: Required<WebSocketClientOptions> = {
	reconnectInterval: 3000,
	maxReconnectAttempts: 10,
	pingInterval: 30000
};

/**
 * WebSocket client with automatic reconnection and message handling
 */
export class WebSocketClient {
	private ws: WebSocket | null = null;
	private options: Required<WebSocketClientOptions>;
	private reconnectAttempts = 0;
	private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
	private pingTimer: ReturnType<typeof setInterval> | null = null;
	private intentionallyClosed = false;

	// State
	private _connectionState: ConnectionState = 'disconnected';
	private _lastError: string | null = null;
	private _lastMessageAt: Date | null = null;

	// Event handlers
	private onStateChange: ((state: ConnectionState) => void) | null = null;
	private onInitialState: MessageHandler<InitialStateMessage> | null = null;
	private onModuleState: MessageHandler<ModuleStateMessage> | null = null;
	private onSystemStats: MessageHandler<SystemStatsMessage> | null = null;
	private onSteamLibrary: MessageHandler<SteamLibraryMessage> | null = null;
	private onError: ((error: string) => void) | null = null;

	constructor(options: WebSocketClientOptions = {}) {
		this.options = {...DEFAULT_OPTIONS, ...options};
	}

	// === Getters ===

	get connectionState(): ConnectionState {
		return this._connectionState;
	}

	get lastError(): string | null {
		return this._lastError;
	}

	get lastMessageAt(): Date | null {
		return this._lastMessageAt;
	}

	get isConnected(): boolean {
		return this._connectionState === 'connected';
	}

	// === Event Registration ===

	setOnStateChange(handler: (state: ConnectionState) => void): void {
		this.onStateChange = handler;
	}

	setOnInitialState(handler: MessageHandler<InitialStateMessage>): void {
		this.onInitialState = handler;
	}

	setOnModuleState(handler: MessageHandler<ModuleStateMessage>): void {
		this.onModuleState = handler;
	}

	setOnSystemStats(handler: MessageHandler<SystemStatsMessage>): void {
		this.onSystemStats = handler;
	}

	setOnSteamLibrary(handler: MessageHandler<SteamLibraryMessage>): void {
		this.onSteamLibrary = handler;
	}

	setOnError(handler: (error: string) => void): void {
		this.onError = handler;
	}

	// === Connection Management ===

	/**
	 * Connect to the WebSocket server
	 */
	connect(): void {
		if (this.ws?.readyState === WebSocket.OPEN) {
			return;
		}

		const token = getStoredToken();
		if (!token) {
			this.setConnectionState('error');
			this._lastError = 'No authentication token available';
			this.onError?.('No authentication token available');
			return;
		}

		this.intentionallyClosed = false;
		this.setConnectionState('connecting');

		const url = `${API_CONFIG.wsUrl}?token=${encodeURIComponent(token)}`;

		try {
			this.ws = new WebSocket(url);
			this.setupEventHandlers();
		} catch (error) {
			this.handleConnectionError(error instanceof Error ? error.message : 'Connection failed');
		}
	}

	/**
	 * Disconnect from the WebSocket server
	 */
	disconnect(): void {
		this.intentionallyClosed = true;
		this.cleanup();
		this.setConnectionState('disconnected');
	}

	/**
	 * Send a message to the server
	 */
	send(message: OutgoingMessage): void {
		if (this.ws?.readyState === WebSocket.OPEN) {
			this.ws.send(JSON.stringify(message));
		}
	}

	/**
	 * Send a ping message
	 */
	ping(): void {
		this.send({type: 'ping'});
	}

	// === Private Methods ===

	private setupEventHandlers(): void {
		if (!this.ws) return;

		this.ws.onopen = () => {
			this.reconnectAttempts = 0;
			this._lastError = null;
			this.setConnectionState('connected');
			this.startPingInterval();
		};

		this.ws.onclose = (event) => {
			this.stopPingInterval();

			if (this.intentionallyClosed) {
				this.setConnectionState('disconnected');
			} else {
				this._lastError = `Connection closed: ${event.code}`;
				this.setConnectionState('error');
				this.scheduleReconnect();
			}
		};

		this.ws.onerror = () => {
			// onerror is usually followed by onclose, so we just log here
			this._lastError = 'WebSocket error occurred';
		};

		this.ws.onmessage = (event) => {
			this._lastMessageAt = new Date();
			this.handleMessage(event.data);
		};
	}

	private handleMessage(data: string): void {
		try {
			const message = JSON.parse(data) as IncomingMessage;

			switch (message.type) {
				case 'initial_state':
					this.onInitialState?.(message);
					break;
				case 'module_state':
					this.onModuleState?.(message);
					break;
				case 'system_stats':
					this.onSystemStats?.(message);
					break;
				case 'steam_library':
					this.onSteamLibrary?.(message);
					break;
				case 'pong':
					// Heartbeat response, no action needed
					break;
				default:
					console.warn('Unknown message type:', (message as { type: string }).type);
			}
		} catch (error) {
			console.error('Failed to parse WebSocket message:', error);
		}
	}

	private handleConnectionError(errorMessage: string): void {
		this._lastError = errorMessage;
		this.setConnectionState('error');
		this.onError?.(errorMessage);
		this.scheduleReconnect();
	}

	private scheduleReconnect(): void {
		if (this.intentionallyClosed) return;

		if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
			this._lastError = 'Max reconnection attempts reached';
			this.onError?.('Max reconnection attempts reached');
			return;
		}

		this.reconnectAttempts++;
		const delay = this.options.reconnectInterval * Math.min(this.reconnectAttempts, 5);

		this.reconnectTimer = setTimeout(() => {
			this.connect();
		}, delay);
	}

	private startPingInterval(): void {
		this.stopPingInterval();
		this.pingTimer = setInterval(() => {
			this.ping();
		}, this.options.pingInterval);
	}

	private stopPingInterval(): void {
		if (this.pingTimer) {
			clearInterval(this.pingTimer);
			this.pingTimer = null;
		}
	}

	private cleanup(): void {
		this.stopPingInterval();

		if (this.reconnectTimer) {
			clearTimeout(this.reconnectTimer);
			this.reconnectTimer = null;
		}

		if (this.ws) {
			this.ws.onopen = null;
			this.ws.onclose = null;
			this.ws.onerror = null;
			this.ws.onmessage = null;
			this.ws.close();
			this.ws = null;
		}
	}

	private setConnectionState(state: ConnectionState): void {
		if (this._connectionState !== state) {
			this._connectionState = state;
			this.onStateChange?.(state);
		}
	}
}

// Singleton instance for easy access
let instance: WebSocketClient | null = null;

export function getWebSocketClient(): WebSocketClient {
	if (!instance) {
		instance = new WebSocketClient();
	}
	return instance;
}

export function resetWebSocketClient(): void {
	if (instance) {
		instance.disconnect();
		instance = null;
	}
}