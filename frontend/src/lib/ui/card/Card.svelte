<script lang="ts">
  import type { CardSchema, ComponentSchema } from "$lib/api";
  import type { Snippet } from "svelte";
  import Icon from "../Icon.svelte";
  import ComponentRenderer from "../ComponentRenderer.svelte";

  interface Props
    extends Partial<Omit<CardSchema, "type" | "children" | "footer">> {
    children?: Snippet | ComponentSchema[];
    footer?: Snippet | ComponentSchema[];
  }

  let { icon = null, title = null, children, footer }: Props = $props();

  const isSnippet = (val: unknown): val is Snippet => typeof val === "function";
</script>

<div class="card">
  {#if icon || title}
    <div class="card-header">
      {#if icon}
        <span class="card-icon">
          <Icon name={icon} size={20} />
        </span>
      {/if}
      {#if title}
        <h3 class="card-title">{title}</h3>
      {/if}
    </div>
  {/if}
  {#if children}
    <div class="card-content">
      {#if isSnippet(children)}
        {@render children()}
      {:else if Array.isArray(children)}
        {#each children as child}
          <ComponentRenderer component={child} />
        {/each}
      {/if}
    </div>
  {/if}
  {#if footer}
    <div class="card-footer">
      {#if isSnippet(footer)}
        {@render footer()}
      {:else if Array.isArray(footer)}
        {#each footer as child}
          <ComponentRenderer component={child} />
        {/each}
      {/if}
    </div>
  {/if}
</div>
