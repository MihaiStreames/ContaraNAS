/**
 * Auth Store - Manages authentication state using Svelte 5 runes
 */

const TOKEN_KEY = "contara_api_token";
const NAS_URL_KEY = "contara_nas_url";

class AuthStore {
  // Auth state
  token = $state<string | null>(null);
  nasUrl = $state<string | null>(null);

  // Connection state
  connected = $state(false);
  connecting = $state(false);
  error = $state<string | null>(null);

  constructor() {
    // Load from localStorage on init (client-side only)
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem(TOKEN_KEY);
      this.nasUrl = localStorage.getItem(NAS_URL_KEY);
    }
  }

  /**
   * Check if we have stored credentials
   */
  get hasCredentials(): boolean {
    return !!this.token && !!this.nasUrl;
  }

  /**
   * Check if authenticated and connected
   */
  get isAuthenticated(): boolean {
    return this.hasCredentials && this.connected;
  }

  /**
   * Store credentials after successful pairing
   */
  setCredentials(token: string, nasUrl: string) {
    this.token = token;
    this.nasUrl = nasUrl;
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(NAS_URL_KEY, nasUrl);
  }

  /**
   * Clear credentials (logout/unpair)
   */
  clearCredentials() {
    this.token = null;
    this.nasUrl = null;
    this.connected = false;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(NAS_URL_KEY);
  }

  /**
   * Set connection state
   */
  setConnected(connected: boolean) {
    this.connected = connected;
    this.connecting = false;
    this.error = null;
  }

  /**
   * Set connecting state
   */
  setConnecting(connecting: boolean) {
    this.connecting = connecting;
    if (connecting) {
      this.error = null;
    }
  }

  /**
   * Set error state
   */
  setError(error: string) {
    this.error = error;
    this.connecting = false;
    this.connected = false;
  }

  /**
   * Get the base URL for API requests
   */
  get apiBaseUrl(): string {
    return this.nasUrl || "";
  }

  /**
   * Get authorization headers
   */
  get authHeaders(): Record<string, string> {
    if (!this.token) return {};
    return { Authorization: `Bearer ${this.token}` };
  }
}

// Export singleton instance
export const authStore = new AuthStore();
