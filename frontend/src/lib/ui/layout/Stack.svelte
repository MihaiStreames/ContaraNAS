<script lang="ts">
  import type { StackSchema, ComponentSchema } from "$lib/api";
  import type { Snippet } from "svelte";
  import ComponentRenderer from "../ComponentRenderer.svelte";

  interface Props extends Partial<Omit<StackSchema, "type" | "children">> {
    children?: Snippet | ComponentSchema[];
  }

  let {
    direction = "vertical",
    gap = "4",
    align = "stretch",
    justify = "start",
    grow = false,
    children,
  }: Props = $props();

  // Derive typed versions for template use
  const arrayChildren = $derived(Array.isArray(children) ? children : null);
  const snippetChildren = $derived(
    !Array.isArray(children) && typeof children === "function"
      ? (children as Snippet)
      : null
  );
</script>

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

<style>
  .stack-grow {
    width: 100%;
  }

  .stack-child-grow {
    flex: 1;
    min-width: 0; /* Prevent flex items from overflowing */
  }
</style>
