<script lang="ts">
  import type { ComponentSchema } from "$lib/api";
  import { componentRegistry, isRenderableType } from "./registry";

  interface Props {
    component: ComponentSchema;
  }

  let { component }: Props = $props();

  const Component = $derived(
    isRenderableType(component.type) ? componentRegistry[component.type] : null
  );
</script>

{#if Component}
  <svelte:component this={Component} {...component} />
{:else}
  <div class="unknown-component">
    Unknown component type: {component.type}
  </div>
{/if}

<style>
  .unknown-component {
    padding: var(--space-2) var(--space-3);
    background: var(--color-warning-subtle);
    color: var(--color-warning-text);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
  }
</style>
