<script lang="ts">
  import type { TabsSchema, TabSchema, ComponentSchema } from "$lib/api";
  import ComponentRenderer from "../ComponentRenderer.svelte";
  import Icon from "../Icon.svelte";

  interface Props extends Partial<Omit<TabsSchema, "type">> {}

  let { tabs = [], default_tab = null, size = "md" }: Props = $props();

  // Track active tab - use default_tab or first tab
  let activeTabId = $state(default_tab || (tabs.length > 0 ? tabs[0].id : ""));

  // Find the active tab's content
  const activeTab = $derived(tabs.find((t) => t.id === activeTabId));

  function selectTab(tabId: string) {
    activeTabId = tabId;
  }
</script>

<div class="tabs-container" class:tabs-sm={size === "sm"}>
  <div class="tabs-header" role="tablist">
    {#each tabs as tab}
      <button
        class="tab-button"
        class:active={tab.id === activeTabId}
        role="tab"
        aria-selected={tab.id === activeTabId}
        aria-controls="tabpanel-{tab.id}"
        onclick={() => selectTab(tab.id)}
      >
        {#if tab.icon}
          <Icon name={tab.icon} size={size === "sm" ? 14 : 16} />
        {/if}
        <span class="tab-label">{tab.label}</span>
      </button>
    {/each}
  </div>
  <div
    class="tabs-content"
    role="tabpanel"
    id="tabpanel-{activeTabId}"
    aria-labelledby="tab-{activeTabId}"
  >
    {#if activeTab?.children}
      {#each activeTab.children as child}
        <ComponentRenderer component={child} />
      {/each}
    {/if}
  </div>
</div>

<style>
  .tabs-container {
    display: flex;
    flex-direction: column;
    width: 100%;
  }

  .tabs-header {
    display: flex;
    gap: var(--space-1);
    border-bottom: 1px solid var(--border-subtle);
    padding: 0 var(--space-2);
    overflow-x: auto;
    scrollbar-width: none;
  }

  .tabs-header::-webkit-scrollbar {
    display: none;
  }

  .tab-button {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    color: var(--text-secondary);
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    transition: all var(--transition-fast);
    white-space: nowrap;
    margin-bottom: -1px;
  }

  .tabs-sm .tab-button {
    padding: var(--space-1) var(--space-2);
    font-size: var(--text-xs);
  }

  .tab-button:hover {
    color: var(--text-primary);
    background: var(--bg-surface-2);
  }

  .tab-button.active {
    color: var(--color-primary);
    border-bottom-color: var(--color-primary);
  }

  .tabs-content {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-2);
    min-height: 0;
  }

  .tab-label {
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
