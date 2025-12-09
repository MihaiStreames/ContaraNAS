<script lang="ts">
  import type { ImageSchema } from "$lib/api";

  interface Props extends Partial<Omit<ImageSchema, "type">> {}

  let {
    src = "",
    alt = "",
    width = null,
    height = null,
    border_radius = "sm",
  }: Props = $props();

  let hasError = $state(false);
  let isLoading = $state(true);

  function handleLoad() {
    isLoading = false;
  }

  function handleError() {
    hasError = true;
    isLoading = false;
  }
</script>

<div
  class="image-container image-radius-{border_radius}"
  style:width={width ? `${width}px` : undefined}
  style:height={height ? `${height}px` : undefined}
>
  {#if hasError}
    <div class="image-placeholder">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
        <circle cx="9" cy="9" r="2" />
        <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
      </svg>
    </div>
  {:else}
    {#if isLoading}
      <div class="image-placeholder image-loading">
        <div class="image-spinner"></div>
      </div>
    {/if}
    <img
      {src}
      {alt}
      width={width ?? undefined}
      height={height ?? undefined}
      class="image"
      class:image-hidden={isLoading}
      onload={handleLoad}
      onerror={handleError}
    />
  {/if}
</div>

<style>
  .image-container {
    position: relative;
    overflow: hidden;
    background: var(--bg-surface-2);
    flex-shrink: 0;
  }

  .image-radius-none {
    border-radius: 0;
  }

  .image-radius-sm {
    border-radius: var(--radius-sm);
  }

  .image-radius-md {
    border-radius: var(--radius-md);
  }

  .image-radius-lg {
    border-radius: var(--radius-lg);
  }

  .image {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .image-hidden {
    opacity: 0;
    position: absolute;
  }

  .image-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    color: var(--text-muted);
  }

  .image-loading {
    position: absolute;
    inset: 0;
  }

  .image-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid var(--border-subtle);
    border-top-color: var(--color-primary);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
