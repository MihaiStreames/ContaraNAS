<script lang="ts">
  import type { ModalSchema } from "$lib/api";
  import type { Snippet } from "svelte";
  import { X } from "lucide-svelte";

  interface Props
    extends Partial<Omit<ModalSchema, "type" | "children" | "footer">> {
    open?: boolean;
    onclose?: () => void;
    children?: Snippet;
    footer?: Snippet;
  }

  let {
    id = "modal",
    title = "",
    closable = true,
    open = false,
    onclose,
    children,
    footer,
  }: Props = $props();

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget && closable) {
      onclose?.();
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Escape" && closable) {
      onclose?.();
    }
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
  <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
  <div
    class="modal-backdrop"
    onclick={handleBackdropClick}
    onkeydown={handleKeydown}
    role="dialog"
    aria-modal="true"
    aria-labelledby="{id}-title"
    tabindex="-1"
  >
    <div class="modal">
      <div class="modal-header">
        <h3 class="modal-title" id="{id}-title">{title}</h3>
        {#if closable}
          <button
            class="modal-close"
            onclick={onclose}
            aria-label="Close modal"
          >
            <X size={18} />
          </button>
        {/if}
      </div>
      {#if children}
        <div class="modal-body">
          {@render children()}
        </div>
      {/if}
      {#if footer}
        <div class="modal-footer">
          {@render footer()}
        </div>
      {/if}
    </div>
  </div>
{/if}
