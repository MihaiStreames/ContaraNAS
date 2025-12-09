<script lang="ts">
  import type { ButtonSchema, ActionRef } from "$lib/api";
  import type { Snippet } from "svelte";
  import { getActionContext } from "$lib/context";
  import Icon from "../Icon.svelte";

  interface Props extends Partial<Omit<ButtonSchema, "type" | "on_click">> {
    on_click?: ActionRef | null;
    onclick?: () => void;
    children?: Snippet;
  }

  let {
    label = "",
    variant = "primary",
    size = "md",
    icon = null,
    icon_only = false,
    disabled = false,
    loading = false,
    on_click = null,
    onclick,
    children,
  }: Props = $props();

  const actionContext = getActionContext();

  // Handle click - either use provided onclick or dispatch action via context
  function handleClick() {
    if (onclick) {
      onclick();
    } else if (on_click && actionContext) {
      actionContext.handleAction(on_click);
    }
  }
</script>

<button
  class="btn btn-{variant} btn-{size}"
  class:btn-icon-only={icon_only}
  class:btn-loading={loading}
  {disabled}
  onclick={handleClick}
>
  {#if loading}
    <span class="spinner"></span>
  {/if}
  {#if icon && !loading}
    <Icon name={icon} size={size === "sm" ? 14 : size === "lg" ? 18 : 16} />
  {/if}
  {#if !icon_only}
    {#if children}
      {@render children()}
    {:else}
      {label}
    {/if}
  {/if}
</button>
