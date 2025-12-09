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
>
  {#if arrayChildren}
    {#each arrayChildren as child}
      <ComponentRenderer component={child} />
    {/each}
  {:else if snippetChildren}
    {@render snippetChildren()}
  {/if}
</div>
