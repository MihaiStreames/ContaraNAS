<script lang="ts">
  import type { TileSchema, StatSchema, ComponentSchema } from "$lib/api";
  import type { Snippet } from "svelte";
  import Icon from "../Icon.svelte";
  import ComponentRenderer from "../ComponentRenderer.svelte";

  interface Props
    extends Partial<Omit<TileSchema, "type" | "stats" | "content" | "actions">> {
    stats?: StatSchema[];
    content?: Snippet | ComponentSchema[];
    actions?: Snippet | ComponentSchema[];
  }

  let {
    icon = "box",
    title = "",
    colspan = 1,
    rowspan = 1,
    stats = [],
    content,
    actions,
  }: Props = $props();

  // Export colspan and rowspan for parent to use in grid layout
  export { colspan, rowspan };

  // Check if value is a Snippet (function) or an array of components
  const isSnippet = (val: unknown): val is Snippet => typeof val === "function";
</script>

<div class="module-tile">
  <div class="tile-header">
    <div class="tile-icon">
      <Icon name={icon} size={22} />
    </div>
    <div class="tile-title-group">
      <h3 class="tile-title">{title}</h3>
    </div>
  </div>

  {#if stats.length > 0}
    <div class="tile-stats">
      {#each stats as stat}
        <div class="tile-stat">
          <span class="tile-stat-value">{stat.value}</span>
          <span class="tile-stat-label">{stat.label}</span>
        </div>
      {/each}
    </div>
  {/if}

  {#if content}
    <div class="tile-content">
      {#if isSnippet(content)}
        {@render content()}
      {:else if Array.isArray(content)}
        {#each content as child}
          <ComponentRenderer component={child} />
        {/each}
      {/if}
    </div>
  {/if}

  {#if actions && (isSnippet(actions) || (Array.isArray(actions) && actions.length > 0))}
    <div class="tile-actions">
      {#if isSnippet(actions)}
        {@render actions()}
      {:else if Array.isArray(actions)}
        {#each actions as action}
          <ComponentRenderer component={action} />
        {/each}
      {/if}
    </div>
  {/if}
</div>
