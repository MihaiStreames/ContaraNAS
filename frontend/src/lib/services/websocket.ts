/**
 * WebSocket service for real-time updates from the NAS
 */

import type { ModuleUI } from "$lib/api";

export type WebSocketMessageType =
  | "full_state"
  | "module_ui"
  | "app_state"
  | "error";

export interface WSFullStateMessage {
  type: "full_state";
  modules: Array<{
    name: string;
    display_name: string;
    enabled: boolean;
    initialized: boolean;
    ui: ModuleUI | null;
  }>;
  active_modal: string | null;
}

export interface WSModuleUIMessage {
  type: "module_ui";
  module: string;
  ui: ModuleUI;
}

export interface WSAppStateMessage {
  type: "app_state";
  active_modal: string | null;
}

export interface WSErrorMessage {
  type: "error";
  message: string;
}

export type WebSocketMessage =
  | WSFullStateMessage
  | WSModuleUIMessage
  | WSAppStateMessage
  | WSErrorMessage;

export interface WebSocketCallbacks {
  onFullState?: (message: WSFullStateMessage) => void;
  onModuleUI?: (message: WSModuleUIMessage) => void;
  onAppState?: (message: WSAppStateMessage) => void;
  onError?: (message: WSErrorMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private callbacks: WebSocketCallbacks = {};
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private baseUrl: string = "";
  private token: string = "";

  /**
   * Connect to the WebSocket server
   */
  connect(baseUrl: string, token: string, callbacks: WebSocketCallbacks) {
    this.baseUrl = baseUrl;
    this.token = token;
    this.callbacks = callbacks;
    this.reconnectAttempts = 0;
    this.createConnection();
  }

  /**
   * Create WebSocket connection
   */
  private createConnection() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    // Convert http(s) to ws(s)
    const wsUrl = this.baseUrl.replace(/^http/, "ws");
    const url = `${wsUrl}/ws?token=${encodeURIComponent(this.token)}`;

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        this.callbacks.onConnect?.();
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          this.handleMessage(message);
        } catch (e) {
          console.error("Failed to parse WebSocket message:", e);
        }
      };

      this.ws.onerror = (event) => {
        console.error("WebSocket error:", event);
      };

      this.ws.onclose = (event) => {
        this.callbacks.onDisconnect?.();

        // Attempt reconnection if not intentionally closed
        if (
          event.code !== 1000 &&
          this.reconnectAttempts < this.maxReconnectAttempts
        ) {
          this.scheduleReconnect();
        }
      };
    } catch (e) {
      console.error("Failed to create WebSocket:", e);
      this.scheduleReconnect();
    }
  }

  /**
   * Handle incoming WebSocket message
   */
  private handleMessage(message: WebSocketMessage) {
    switch (message.type) {
      case "full_state":
        this.callbacks.onFullState?.(message);
        break;
      case "module_ui":
        this.callbacks.onModuleUI?.(message);
        break;
      case "app_state":
        this.callbacks.onAppState?.(message);
        break;
      case "error":
        this.callbacks.onError?.(message);
        break;
      default:
        console.warn("Unknown WebSocket message type:", message);
    }
  }

  /**
   * Schedule a reconnection attempt
   */
  private scheduleReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    this.reconnectTimer = setTimeout(() => {
      this.createConnection();
    }, delay);
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close(1000, "Client disconnect");
      this.ws = null;
    }
  }

  /**
   * Check if connected
   */
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Export singleton instance
export const wsService = new WebSocketService();
