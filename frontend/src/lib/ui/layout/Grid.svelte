<script lang="ts">
  import type { GridSchema, ComponentSchema } from "$lib/api";
  import type { Snippet } from "svelte";
  import ComponentRenderer from "../ComponentRenderer.svelte";

  interface Props extends Partial<Omit<GridSchema, "type" | "children">> {
    children?: Snippet | ComponentSchema[];
  }

  let { columns = 2, gap = "4", row_height, children }: Props = $props();

  // Handle columns - can be number or string like "repeat(auto-fill, minmax(300px, 1fr))"
  const gridColumns = $derived(
    typeof columns === "number" ? `repeat(${columns}, 1fr)` : columns
  );

  // Build style string
  const gridStyle = $derived(
    `grid-template-columns: ${gridColumns}${row_height ? `; grid-auto-rows: ${row_height}` : ""}`
  );

  // Derive typed versions for template use
  const arrayChildren = $derived(Array.isArray(children) ? children : null);
  const snippetChildren = $derived(
    !Array.isArray(children) && typeof children === "function"
      ? (children as Snippet)
      : null
  );
</script>

<div class="grid gap-{gap}" style={gridStyle}>
  {#if arrayChildren}
    {#each arrayChildren as child}
      <ComponentRenderer component={child} />
    {/each}
  {:else if snippetChildren}
    {@render snippetChildren()}
  {/if}
</div>
