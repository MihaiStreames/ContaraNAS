<script lang="ts">
  import type { ProgressSchema } from "$lib/api";

  interface Props extends Partial<Omit<ProgressSchema, "type">> {}

  let {
    value = 0,
    max = 100,
    label = null,
    sublabel = null,
    color = "default",
    size = "sm",
  }: Props = $props();

  const percentage = $derived(Math.min(100, Math.max(0, (value / max) * 100)));
</script>

<div class="progress-container">
  {#if label || sublabel}
    <div class="progress-header">
      {#if label}
        <span class="text-secondary">{label}</span>
      {/if}
      {#if sublabel}
        <span class="text-primary font-medium">{sublabel}</span>
      {/if}
    </div>
  {/if}
  <div class="progress-bar" class:progress-bar-lg={size === "lg"}>
    <div
      class="progress-fill"
      class:progress-success={color === "success"}
      class:progress-warning={color === "warning"}
      class:progress-error={color === "error"}
      style="width: {percentage}%"
    ></div>
  </div>
</div>
