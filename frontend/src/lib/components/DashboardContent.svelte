<script lang="ts">
  import { Grid, Text, Alert, Spinner, Button } from "$lib/ui";
  import { ModuleRenderer } from "$lib/ui";
  import { uiStore } from "$lib/stores";
  import { api } from "$lib/services";
  import type { ActionRefWithParams } from "$lib/actions";

  interface Props {
    onAction: (moduleName: string, actionRef: ActionRefWithParams) => void;
    onRetry: () => void;
  }

  let { onAction, onRetry }: Props = $props();

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
</script>

<main class="dashboard-content">
  {#if uiStore.loading}
    <div class="loading-container">
      <Spinner size="lg" label="Loading modules..." />
    </div>
  {:else if uiStore.error}
    <div class="error-container">
      <Alert variant="error" title="Error" message={uiStore.error} />
      <Button label="Retry" variant="primary" onclick={onRetry} />
    </div>
  {:else if uiStore.allModulesWithTiles.length === 0}
    <div class="empty-container">
      <Text content="No modules available" variant="muted" />
    </div>
  {:else}
    <Grid columns={3} gap="4" row_height="minmax(200px, auto)">
      {#each uiStore.allModulesWithTiles as { module: mod, tile } (mod.name)}
        <div
          class="tile-wrapper"
          class:tile-disabled={!mod.enabled}
          style:grid-column="span {tile?.colspan ?? 1}"
          style:grid-row="span {tile?.rowspan ?? 1}"
        >
          {#if tile}
            <ModuleRenderer moduleName={mod.name} component={tile} {onAction} />
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

<style>
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

  .tile-wrapper {
    position: relative;
    height: 100%;
  }

  .tile-disable-btn {
    position: absolute;
    top: var(--space-4);
    right: var(--space-4);
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
