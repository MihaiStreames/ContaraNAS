<script lang="ts">
  import type { StackSchema } from "$lib/api";
  import type { Snippet } from "svelte";

  interface Props extends Partial<Omit<StackSchema, "type" | "children">> {
    children?: Snippet;
  }

  let {
    direction = "vertical",
    gap = "4",
    align = "stretch",
    justify = "start",
    children,
  }: Props = $props();
</script>

<div
  class="stack stack-{direction} stack-align-{align} stack-justify-{justify} gap-{gap}"
>
  {#if children}
    {@render children()}
  {/if}
</div>
