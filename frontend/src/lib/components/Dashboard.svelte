<script lang="ts">
  import { Modal, Alert } from "$lib/ui";
  import { ModuleRenderer } from "$lib/ui";
  import { uiStore, authStore } from "$lib/stores";
  import { api, wsService, ApiError } from "$lib/services";
  import { processActionResult } from "$lib/actions";
  import type { ActionRefWithParams } from "$lib/actions";
  import Header from "./Header.svelte";
  import Sidebar from "./Sidebar.svelte";
  import DashboardContent from "./DashboardContent.svelte";

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
  <Header />

  <div class="dashboard-body">
    <Sidebar />
    <DashboardContent onAction={handleAction} onRetry={connectToNAS} />
  </div>

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
        {#each modal.footer ?? [] as footerChild}
          <ModuleRenderer
            moduleName={modalModule}
            component={footerChild}
            onAction={handleAction}
          />
        {/each}
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

  .dashboard-body {
    flex: 1;
    display: flex;
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
