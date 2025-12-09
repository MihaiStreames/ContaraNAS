<script lang="ts">
  import type { GridSchema, ComponentSchema } from "$lib/api";
  import type { Snippet } from "svelte";
  import ComponentRenderer from "../ComponentRenderer.svelte";

  interface Props extends Partial<Omit<GridSchema, "type" | "children">> {
    children?: Snippet | ComponentSchema[];
  }

  let { columns = 2, gap = "4", children }: Props = $props();

  // Handle columns - can be number or string like "repeat(auto-fill, minmax(300px, 1fr))"
  const gridColumns = $derived(
    typeof columns === "number" ? `repeat(${columns}, 1fr)` : columns
  );

  const isArrayChildren = $derived(Array.isArray(children));
</script>

<div class="grid gap-{gap}" style="grid-template-columns: {gridColumns}">
  {#if isArrayChildren}
    {#each children as child}
      <ComponentRenderer component={child} />
    {/each}
  {:else if children}
    {@render children()}
  {/if}
</div>
