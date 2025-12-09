/**
 * API client for communicating with the NAS backend
 */

import type {
  PairResponse,
  AppStateResponse,
  ModuleUIResponse,
  HealthResponse,
} from "$lib/api";
import type { ActionResult } from "$lib/actions";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

class ApiClient {
  private baseUrl: string = "";
  private token: string = "";

  /**
   * Configure the API client
   */
  configure(baseUrl: string, token: string = "") {
    this.baseUrl = baseUrl.replace(/\/$/, ""); // Remove trailing slash
    this.token = token;
  }

  /**
   * Set the auth token
   */
  setToken(token: string) {
    this.token = token;
  }

  /**
   * Make an authenticated request
   */
  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new ApiError(
        response.status,
        errorText || `Request failed: ${response.status}`
      );
    }

    return response.json();
  }

  // === Health endpoints ===

  /**
   * Check if the NAS is reachable
   */
  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>("/api/health");
  }

  // === Auth endpoints ===

  /**
   * Pair with the NAS using a pairing code
   */
  async pair(pairingCode: string): Promise<PairResponse> {
    return this.request<PairResponse>("/api/auth/pair", {
      method: "POST",
      body: JSON.stringify({ pairing_code: pairingCode }),
    });
  }

  /**
   * Unpair from the NAS
   */
  async unpair(): Promise<{ success: boolean; message: string }> {
    return this.request("/api/auth/unpair", { method: "POST" });
  }

  // === State endpoints ===

  /**
   * Get full application state
   */
  async getState(): Promise<AppStateResponse> {
    return this.request<AppStateResponse>("/api/state");
  }

  // === Module endpoints ===

  /**
   * Get UI for a specific module
   */
  async getModuleUI(moduleName: string): Promise<ModuleUIResponse> {
    return this.request<ModuleUIResponse>(`/api/modules/${moduleName}/ui`);
  }

  /**
   * Enable a module
   */
  async enableModule(
    moduleName: string
  ): Promise<{ success: boolean; enabled: boolean }> {
    return this.request(`/api/modules/${moduleName}/enable`, {
      method: "POST",
    });
  }

  /**
   * Disable a module
   */
  async disableModule(
    moduleName: string
  ): Promise<{ success: boolean; enabled: boolean }> {
    return this.request(`/api/modules/${moduleName}/disable`, {
      method: "POST",
    });
  }

  /**
   * Execute a module action
   */
  async executeAction(
    moduleName: string,
    actionName: string,
    payload: Record<string, unknown> = {}
  ): Promise<ActionResult> {
    return this.request<ActionResult>(
      `/api/modules/${moduleName}/action/${actionName}`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  }
}

// Export singleton instance
export const api = new ApiClient();
export { ApiError };
