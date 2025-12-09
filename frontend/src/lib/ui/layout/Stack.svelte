<script lang="ts">
  import type { StackSchema, ComponentSchema, ActionRef } from "$lib/api";
  import type { Snippet } from "svelte";
  import { getActionContext } from "$lib/context";
  import ComponentRenderer from "../ComponentRenderer.svelte";

  interface Props extends Partial<Omit<StackSchema, "type" | "children" | "on_click">> {
    children?: Snippet | ComponentSchema[];
    on_click?: ActionRef | null;
  }

  let {
    direction = "vertical",
    gap = "4",
    align = "stretch",
    justify = "start",
    grow = false,
    children,
    on_click = null,
  }: Props = $props();

  const actionContext = getActionContext();

  // Handle click - dispatch action via context
  function handleClick() {
    if (on_click && actionContext) {
      actionContext.handleAction(on_click);
    }
  }

  // Derive typed versions for template use
  const arrayChildren = $derived(Array.isArray(children) ? children : null);
  const snippetChildren = $derived(
    !Array.isArray(children) && typeof children === "function"
      ? (children as Snippet)
      : null
  );

  const isClickable = $derived(!!on_click);
</script>

{#if isClickable}
  <button
    type="button"
    class="stack stack-{direction} stack-align-{align} stack-justify-{justify} gap-{gap} stack-clickable"
    class:stack-grow={grow}
    onclick={handleClick}
  >
    {#if arrayChildren}
      {#each arrayChildren as child}
        <div class:stack-child-grow={grow}>
          <ComponentRenderer component={child} />
        </div>
      {/each}
    {:else if snippetChildren}
      {@render snippetChildren()}
    {/if}
  </button>
{:else}
  <div
    class="stack stack-{direction} stack-align-{align} stack-justify-{justify} gap-{gap}"
    class:stack-grow={grow}
  >
    {#if arrayChildren}
      {#each arrayChildren as child}
        <div class:stack-child-grow={grow}>
          <ComponentRenderer component={child} />
        </div>
      {/each}
    {:else if snippetChildren}
      {@render snippetChildren()}
    {/if}
  </div>
{/if}

<style>
  .stack-grow {
    width: 100%;
  }

  .stack-child-grow {
    flex: 1;
    min-width: 0; /* Prevent flex items from overflowing */
    display: flex;
    justify-content: center;
  }

  .stack-clickable {
    cursor: pointer;
    background: transparent;
    border: none;
    padding: var(--space-3);
    border-radius: var(--radius-md);
    transition: background-color var(--transition-fast);
    text-align: left;
  }

  .stack-clickable:hover {
    background: var(--bg-surface-2);
  }

  .stack-clickable:active {
    background: var(--bg-surface-3);
  }
</style>
