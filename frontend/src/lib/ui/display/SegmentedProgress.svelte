<script lang="ts">
  import type { SegmentedProgressSchema } from "$lib/api";

  interface Props extends Partial<Omit<SegmentedProgressSchema, "type">> {}

  let {
    segments = [],
    max = 100,
    size = "sm",
    show_legend = false,
  }: Props = $props();

  // Calculate percentage widths for each segment
  const segmentWidths = $derived(
    segments.map((seg) => ({
      ...seg,
      width: Math.max(0, (seg.value / max) * 100),
    }))
  );

  // Map semantic colors to CSS variables
  function getSegmentColor(color: string): string {
    const colorMap: Record<string, string> = {
      primary: "var(--color-primary)",
      success: "var(--color-success)",
      warning: "var(--color-warning)",
      error: "var(--color-error)",
      info: "var(--color-info)",
      muted: "var(--text-muted)",
    };
    return colorMap[color] || color;
  }
</script>

<div class="segmented-progress-container">
  <div
    class="segmented-progress-bar"
    class:segmented-progress-lg={size === "lg"}
  >
    {#each segmentWidths as segment}
      {#if segment.width > 0}
        <div
          class="segmented-progress-segment"
          style="width: {segment.width}%; background-color: {getSegmentColor(
            segment.color
          )}"
          title={segment.label
            ? `${segment.label}: ${segment.value}`
            : undefined}
        ></div>
      {/if}
    {/each}
  </div>
  {#if show_legend}
    <div class="segmented-progress-legend">
      {#each segments as segment}
        <div class="legend-item">
          <span
            class="legend-color"
            style="background-color: {getSegmentColor(segment.color)}"
          ></span>
          <span class="legend-label">{segment.label || ""}</span>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .segmented-progress-container {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .segmented-progress-bar {
    display: flex;
    width: 100%;
    height: 8px;
    background: var(--bg-surface-3);
    border-radius: var(--radius-full);
    overflow: hidden;
  }

  .segmented-progress-bar.segmented-progress-lg {
    height: 12px;
  }

  .segmented-progress-segment {
    height: 100%;
    transition: width var(--transition-base);
  }

  .segmented-progress-segment:first-child {
    border-top-left-radius: var(--radius-full);
    border-bottom-left-radius: var(--radius-full);
  }

  .segmented-progress-segment:last-child {
    border-top-right-radius: var(--radius-full);
    border-bottom-right-radius: var(--radius-full);
  }

  .segmented-progress-legend {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-3);
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: var(--space-1);
  }

  .legend-color {
    width: 10px;
    height: 10px;
    border-radius: var(--radius-sm);
  }

  .legend-label {
    font-size: var(--text-xs);
    color: var(--text-secondary);
  }
</style>
