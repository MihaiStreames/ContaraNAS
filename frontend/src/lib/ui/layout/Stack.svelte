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

  // Check if children is an array (from backend) or a snippet (from Svelte)
  const isArrayChildren = $derived(Array.isArray(children));
</script>

<div
  class="stack stack-{direction} stack-align-{align} stack-justify-{justify} gap-{gap}"
>
  {#if isArrayChildren}
    {#each children as child}
      <ComponentRenderer component={child} />
    {/each}
  {:else if children}
    {@render children()}
  {/if}
</div>
