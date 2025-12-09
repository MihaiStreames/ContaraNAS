<script lang="ts">
  import { Grid, Stack, Modal, Alert, Spinner, Text, Button } from "$lib/ui";
  import { ComponentRenderer } from "$lib/ui";
  import { uiStore, authStore } from "$lib/stores";
  import { api, wsService } from "$lib/services";
  import { processActionResult } from "$lib/actions";
  import type { ActionRef } from "$lib/api";

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
      uiStore.setAppState(state.modules, state.active_modal);
    } catch (e) {
      uiStore.setError(
        e instanceof Error ? e.message : "Failed to fetch state"
      );
    }
  }

  function handleDisconnect() {
    wsService.disconnect();
    authStore.clearCredentials();
    uiStore.clear();
    onDisconnect();
  }

  // Action handler for components
  async function handleAction(moduleName: string, actionRef: ActionRef) {
    try {
      const result = await api.executeAction(moduleName, actionRef.__action__);
      processActionResult(result, {
        openModal: (id) => uiStore.openModal(id),
        closeModal: (id) => uiStore.closeModal(id),
        notify: (msg, variant) => uiStore.notify(msg, variant),
        refresh: () => connectToNAS(),
      });
    } catch (e) {
      uiStore.notify(e instanceof Error ? e.message : "Action failed", "error");
    }
  }

  // Find the current active modal's data
  const activeModalData = $derived(() => {
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
          label="Disconnect"
          variant="ghost"
          size="sm"
          icon="log-out"
          onclick={handleDisconnect}
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
    {:else if uiStore.tiles.length === 0}
      <div class="empty-container">
        <Text content="No modules enabled" variant="muted" />
      </div>
    {:else}
      <Grid columns={3} gap="4">
        {#each uiStore.tiles as { module, tile } (module)}
          <ComponentRenderer
            component={{
              ...tile,
              // Wire up actions to our handler
              // TODO: Deep transform ActionRefs in the component tree
            }}
          />
        {/each}
      </Grid>
    {/if}
  </main>

  <!-- Modals -->
  {#if activeModalData()}
    {@const { module, modal } = activeModalData()!}
    <Modal
      id={modal.id}
      title={modal.title}
      closable={modal.closable ?? true}
      onclose={() => uiStore.closeModal()}
    >
      {#snippet children()}
        {#if modal.children}
          {#each modal.children as child}
            <ComponentRenderer component={child} />
          {/each}
        {/if}
      {/snippet}
      {#snippet footer()}
        {#if modal.footer}
          {#each modal.footer as footerChild}
            <ComponentRenderer component={footerChild} />
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
</style>
