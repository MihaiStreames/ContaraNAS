<script lang="ts">
  import { Grid, Stack, Modal, Alert, Spinner, Text, Button } from "$lib/ui";
  import { ModuleRenderer } from "$lib/ui";
  import { uiStore, authStore } from "$lib/stores";
  import { api, wsService, ApiError } from "$lib/services";
  import { processActionResult } from "$lib/actions";
  import type { ActionRefWithParams } from "$lib/actions";

  interface Props {
    onDisconnect: () => void;
  }

  let { onDisconnect }: Props = $props();

  // Connect to WebSocket and fetch initial state
  $effect(() => {
    if (authStore.nasUrl && authStore.token) {
      connectToNAS();
    }

    return () => {
      wsService.disconnect();
    };
  });

  async function connectToNAS() {
    authStore.setConnecting(true);
    uiStore.setLoading(true);

    // Configure API client
    api.configure(authStore.nasUrl!, authStore.token!);

    // Connect WebSocket
    wsService.connect(authStore.nasUrl!, authStore.token!, {
      onConnect: () => {
        authStore.setConnected(true);
      },
      onDisconnect: () => {
        authStore.setConnected(false);
      },
      onFullState: (msg) => {
        uiStore.setAppState(msg.modules, msg.active_modal);
      },
      onModuleUI: (msg) => {
        uiStore.updateModuleUI(msg.module, msg.ui);
      },
      onAppState: (msg) => {
        if (msg.active_modal !== undefined) {
          if (msg.active_modal) {
            uiStore.openModal(msg.active_modal);
          } else {
            uiStore.closeModal();
          }
        }
      },
      onError: (msg) => {
        uiStore.notify(msg.message, "error");
      },
    });

    // Fetch initial state via REST (WebSocket will also send it, but this is faster)
    try {
      const state = await api.getState();
      console.log("[Dashboard] Got state:", state.modules?.length, "modules");
      uiStore.setAppState(state.modules, state.active_modal);
      console.log("[Dashboard] After setAppState, loading:", uiStore.loading);
    } catch (e) {
      console.error("[Dashboard] Error fetching state:", e);
      // If we get a 401, the token is invalid - clear credentials and go back to pairing
      if (e instanceof ApiError && e.status === 401) {
        authStore.clearCredentials();
        uiStore.clear();
        onDisconnect();
        return;
      }
      uiStore.setError(
        e instanceof Error ? e.message : "Failed to fetch state"
      );
    }
  }

  async function handleUnpair() {
    // Unpair from the NAS first
    try {
      await api.unpair();
    } catch (e) {
      // Ignore errors - we're disconnecting anyway
      console.warn("Failed to unpair:", e);
    }

    wsService.disconnect();
    authStore.clearCredentials();
    uiStore.clear();
    onDisconnect();
  }

  // Action handler for components
  async function handleAction(
    moduleName: string,
    actionRef: ActionRefWithParams
  ) {
    console.log(
      "[Dashboard] handleAction:",
      moduleName,
      actionRef.__action__,
      actionRef.__params__
    );
    try {
      const result = await api.executeAction(
        moduleName,
        actionRef.__action__,
        actionRef.__params__
      );
      console.log("[Dashboard] Action result:", result);
      processActionResult(result, {
        openModal: (id) => {
          console.log("[Dashboard] Opening modal:", id);
          uiStore.openModal(id);
        },
        closeModal: (id) => uiStore.closeModal(id),
        notify: (msg, variant) => uiStore.notify(msg, variant),
        refresh: () => connectToNAS(),
      });
    } catch (e) {
      console.error("[Dashboard] Action error:", e);
      uiStore.notify(e instanceof Error ? e.message : "Action failed", "error");
    }
  }

  // Toggle module enabled state
  async function toggleModule(moduleName: string, currentlyEnabled: boolean) {
    try {
      if (currentlyEnabled) {
        await api.disableModule(moduleName);
      } else {
        await api.enableModule(moduleName);
      }
      // Refresh state after toggle
      const state = await api.getState();
      uiStore.setAppState(state.modules, state.active_modal);
    } catch (e) {
      uiStore.notify(
        e instanceof Error ? e.message : "Failed to toggle module",
        "error"
      );
    }
  }

  // Get all modules (enabled and disabled)
  const allModules = $derived(Array.from(uiStore.modules.values()));

  // Find the current active modal's data
  const activeModalData = $derived.by(() => {
    if (!uiStore.activeModal) return null;
    for (const { module, modal } of uiStore.allModals) {
      if (modal.id === uiStore.activeModal) {
        return { module, modal };
      }
    }
    return null;
  });
</script>

<div class="dashboard">
  <!-- Header -->
  <header class="dashboard-header">
    <div class="header-content">
      <h1 class="logo">ContaraNAS</h1>
      <Stack direction="horizontal" gap="4" align="center">
        {#if authStore.connected}
          <span class="connection-status connected">Connected</span>
        {:else}
          <span class="connection-status disconnected">Disconnected</span>
        {/if}
        <Button
          label="Unpair"
          variant="ghost"
          size="sm"
          icon="LogOut"
          onclick={handleUnpair}
        />
      </Stack>
    </div>
  </header>

  <!-- Main content -->
  <main class="dashboard-content">
    {#if uiStore.loading}
      <div class="loading-container">
        <Spinner size="lg" label="Loading modules..." />
      </div>
    {:else if uiStore.error}
      <div class="error-container">
        <Alert variant="error" title="Error" message={uiStore.error} />
        <Button label="Retry" variant="primary" onclick={connectToNAS} />
      </div>
    {:else if allModules.length === 0}
      <div class="empty-container">
        <Text content="No modules available" variant="muted" />
      </div>
    {:else}
      <Grid columns={3} gap="4">
        {#each uiStore.allModulesWithTiles as { module: mod, tile } (mod.name)}
          <div
            class="tile-wrapper"
            class:tile-disabled={!mod.enabled}
            style:grid-column="span {tile?.colspan ?? 1}"
          >
            {#if tile}
              <ModuleRenderer
                moduleName={mod.name}
                component={tile}
                onAction={handleAction}
              />
              <!-- Disabled overlay -->
              {#if !mod.enabled}
                <div class="tile-disabled-overlay">
                  <Button
                    label="Enable Module"
                    variant="primary"
                    onclick={() => toggleModule(mod.name, false)}
                  />
                </div>
              {/if}
            {:else}
              <!-- Placeholder tile for uninitialized modules -->
              <div class="module-tile placeholder-tile">
                <div class="tile-header">
                  <div class="tile-icon">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="22"
                      height="22"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.75"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <path d="m21 21-6-6m6 6v-4.8m0 4.8h-4.8" />
                      <path d="M3 16.2V21h4.8" />
                      <path d="M21 7.8V3h-4.8" />
                      <path d="M3 7.8V3h4.8" />
                    </svg>
                  </div>
                  <div class="tile-title-group">
                    <h3 class="tile-title">{mod.display_name}</h3>
                  </div>
                </div>
                <div class="placeholder-tile-content">
                  <Text
                    content="Enable module to start collecting data"
                    variant="muted"
                  />
                </div>
                <div class="tile-actions">
                  <Button
                    label="Enable"
                    variant="primary"
                    size="sm"
                    onclick={() => toggleModule(mod.name, false)}
                  />
                </div>
              </div>
            {/if}
            {#if mod.enabled}
              <button
                class="tile-disable-btn"
                onclick={() => toggleModule(mod.name, true)}
                title="Disable module"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M18 6 6 18" />
                  <path d="m6 6 12 12" />
                </svg>
              </button>
            {/if}
          </div>
        {/each}
      </Grid>
    {/if}
  </main>

  <!-- Modals -->
  {#if activeModalData}
    {@const { module: modalModule, modal } = activeModalData}
    <Modal
      open={true}
      id={modal.id}
      title={modal.title}
      size={modal.size ?? "md"}
      closable={modal.closable ?? true}
      onclose={() => uiStore.closeModal()}
    >
      {#snippet children()}
        {#if modal.children}
          {#each modal.children as child}
            <ModuleRenderer
              moduleName={modalModule}
              component={child}
              onAction={handleAction}
            />
          {/each}
        {/if}
      {/snippet}
      {#snippet footer()}
        {#if modal.footer}
          {#each modal.footer as footerChild}
            <ModuleRenderer
              moduleName={modalModule}
              component={footerChild}
              onAction={handleAction}
            />
          {/each}
        {/if}
      {/snippet}
    </Modal>
  {/if}

  <!-- Notifications -->
  {#if uiStore.notifications.length > 0}
    <div class="notifications">
      {#each uiStore.notifications as notification (notification.id)}
        <Alert variant={notification.variant} message={notification.message} />
      {/each}
    </div>
  {/if}
</div>

<style>
  .dashboard {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .dashboard-header {
    background: var(--bg-surface-1);
    border-bottom: 1px solid var(--border-subtle);
    padding: var(--space-3) var(--space-4);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .header-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .logo {
    font-size: var(--text-xl);
    font-weight: var(--font-bold);
    color: var(--text-primary);
    margin: 0;
  }

  .connection-status {
    font-size: var(--text-sm);
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius-full);
  }

  .connection-status.connected {
    background: var(--color-success-subtle);
    color: var(--color-success-text);
  }

  .connection-status.disconnected {
    background: var(--color-error-subtle);
    color: var(--color-error-text);
  }

  .dashboard-content {
    flex: 1;
    padding: var(--space-4);
    max-width: 1400px;
    margin: 0 auto;
    width: 100%;
  }

  .loading-container,
  .error-container,
  .empty-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-4);
    min-height: 400px;
  }

  .notifications {
    position: fixed;
    bottom: var(--space-4);
    right: var(--space-4);
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    z-index: 1000;
    max-width: 400px;
  }

  .tile-wrapper {
    position: relative;
    height: 100%;
  }

  .tile-disable-btn {
    position: absolute;
    top: var(--space-2);
    right: var(--space-2);
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-surface-2);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-full);
    color: var(--text-muted);
    cursor: pointer;
    opacity: 0;
    transition: all var(--transition-fast);
  }

  .tile-wrapper:hover .tile-disable-btn {
    opacity: 1;
  }

  .tile-disable-btn:hover {
    background: var(--color-error-subtle);
    border-color: var(--color-error);
    color: var(--color-error-text);
  }

  .tile-disabled {
    opacity: 0.7;
  }

  .tile-disabled-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.5);
    border-radius: var(--radius-xl);
    z-index: 10;
  }

  .placeholder-tile {
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  .placeholder-tile-content {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-4);
    text-align: center;
  }
</style>
