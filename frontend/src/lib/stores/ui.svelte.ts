/**
 * UI Store - Manages module UI state using Svelte 5 runes
 */

import type {
  ModuleSnapshot,
  ModuleUI,
  TileSchema,
  ModalSchema,
} from "$lib/api";

export interface Notification {
  id: string;
  message: string;
  variant: "info" | "success" | "warning" | "error";
  timeout?: number;
}

class UIStore {
  // Module state
  modules = $state<Map<string, ModuleSnapshot>>(new Map());

  // Modal state
  activeModal = $state<string | null>(null);

  // Notifications
  notifications = $state<Notification[]>([]);

  // Loading states
  loading = $state(true);
  error = $state<string | null>(null);

  /**
   * Initialize store with full app state
   */
  setAppState(modules: ModuleSnapshot[], activeModal: string | null = null) {
    console.log(
      "[UIStore] setAppState called with",
      modules?.length,
      "modules"
    );
    const moduleMap = new Map<string, ModuleSnapshot>();
    for (const mod of modules) {
      moduleMap.set(mod.name, mod);
    }
    this.modules = moduleMap;
    this.activeModal = activeModal;
    this.loading = false;
    this.error = null;
    console.log("[UIStore] loading is now:", this.loading);
  }

  /**
   * Update a single module's UI
   */
  updateModuleUI(moduleName: string, ui: ModuleUI) {
    const existing = this.modules.get(moduleName);
    if (existing) {
      this.modules.set(moduleName, { ...existing, ui });
      // Trigger reactivity by reassigning
      this.modules = new Map(this.modules);
    }
  }

  /**
   * Update a module's enabled state
   */
  updateModuleEnabled(moduleName: string, enabled: boolean) {
    const existing = this.modules.get(moduleName);
    if (existing) {
      this.modules.set(moduleName, { ...existing, enabled });
      this.modules = new Map(this.modules);
    }
  }

  /**
   * Get all enabled modules with their tiles
   */
  get enabledModules(): ModuleSnapshot[] {
    return Array.from(this.modules.values()).filter((m) => m.enabled);
  }

  /**
   * Get all tiles from enabled modules
   */
  get tiles(): Array<{ module: string; tile: TileSchema }> {
    const result: Array<{ module: string; tile: TileSchema }> = [];
    for (const mod of this.enabledModules) {
      if (mod.ui?.tile) {
        result.push({ module: mod.name, tile: mod.ui.tile });
      }
    }
    return result;
  }

  /**
   * Get all modules with their tile data
   */
  get allModulesWithTiles(): Array<{
    module: ModuleSnapshot;
    tile: TileSchema | null;
  }> {
    const result: Array<{ module: ModuleSnapshot; tile: TileSchema | null }> =
      [];
    for (const mod of this.modules.values()) {
      result.push({
        module: mod,
        tile: mod.ui?.tile ?? null,
      });
    }
    return result;
  }

  /**
   * Get all modals from all modules (enabled or not for configuration)
   */
  get allModals(): Array<{ module: string; modal: ModalSchema }> {
    const result: Array<{ module: string; modal: ModalSchema }> = [];
    for (const mod of this.modules.values()) {
      if (mod.ui?.modals) {
        for (const modal of mod.ui.modals) {
          result.push({ module: mod.name, modal });
        }
      }
    }
    return result;
  }

  /**
   * Open a modal
   */
  openModal(modalId: string) {
    this.activeModal = modalId;
  }

  /**
   * Close the active modal (or a specific modal)
   */
  closeModal(modalId?: string) {
    if (!modalId || this.activeModal === modalId) {
      this.activeModal = null;
    }
  }

  /**
   * Add a notification
   */
  notify(
    message: string,
    variant: Notification["variant"] = "info",
    timeout = 5000
  ) {
    const id = crypto.randomUUID();
    const notification: Notification = { id, message, variant, timeout };
    this.notifications = [...this.notifications, notification];

    if (timeout > 0) {
      setTimeout(() => this.dismissNotification(id), timeout);
    }

    return id;
  }

  /**
   * Dismiss a notification
   */
  dismissNotification(id: string) {
    this.notifications = this.notifications.filter((n) => n.id !== id);
  }

  /**
   * Set loading state
   */
  setLoading(loading: boolean) {
    this.loading = loading;
  }

  /**
   * Set error state
   */
  setError(error: string | null) {
    this.error = error;
    this.loading = false;
  }

  /**
   * Clear all state (for logout/disconnect)
   */
  clear() {
    this.modules = new Map();
    this.activeModal = null;
    this.notifications = [];
    this.loading = true;
    this.error = null;
  }
}

// Export singleton instance
export const uiStore = new UIStore();
