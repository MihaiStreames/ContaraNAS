<script lang="ts">
  import type { LineChartSchema } from "$lib/api";

  interface Props extends Partial<Omit<LineChartSchema, "type">> {}

  let {
    data = [],
    max = 100,
    min = 0,
    height = 80,
    color = "primary",
    fill = true,
    label = null,
  }: Props = $props();

  // Map semantic colors to CSS variables
  const colorMap: Record<string, { stroke: string; fill: string }> = {
    default: {
      stroke: "var(--text-secondary)",
      fill: "var(--bg-surface-3)",
    },
    primary: {
      stroke: "var(--color-primary)",
      fill: "var(--color-primary-subtle)",
    },
    success: {
      stroke: "var(--color-success)",
      fill: "var(--color-success-subtle)",
    },
    warning: {
      stroke: "var(--color-warning)",
      fill: "var(--color-warning-subtle)",
    },
    error: {
      stroke: "var(--color-error)",
      fill: "var(--color-error-subtle)",
    },
  };

  const colors = $derived(colorMap[color] || colorMap.primary);

  // Generate SVG path from data points
  const pathData = $derived(() => {
    if (data.length === 0) return { line: "", area: "" };

    const range = max - min;
    const points = data.map((value, index) => {
      const x = (index / Math.max(1, data.length - 1)) * 100;
      const y = 100 - ((value - min) / range) * 100;
      return { x, y: Math.max(0, Math.min(100, y)) };
    });

    // Build line path
    const linePath = points
      .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`)
      .join(" ");

    // Build area path (for fill)
    const areaPath = `${linePath} L 100 100 L 0 100 Z`;

    return { line: linePath, area: areaPath };
  });

  // Get the current (latest) value for display
  const currentValue = $derived(data.length > 0 ? data[data.length - 1] : null);
</script>

<div class="line-chart" style="height: {height}px">
  <svg viewBox="0 0 100 100" preserveAspectRatio="none" class="chart-svg">
    {#if fill && pathData().area}
      <path d={pathData().area} fill={colors.fill} class="chart-area" />
    {/if}
    {#if pathData().line}
      <path
        d={pathData().line}
        stroke={colors.stroke}
        fill="none"
        stroke-width="2"
        vector-effect="non-scaling-stroke"
        class="chart-line"
      />
    {/if}
  </svg>
  {#if label !== null || currentValue !== null}
    <div class="chart-label">
      {#if label}
        <span class="label-text">{label}</span>
      {:else if currentValue !== null}
        <span class="label-value">{currentValue.toFixed(0)}%</span>
      {/if}
    </div>
  {/if}
</div>

<style>
  .line-chart {
    position: relative;
    width: 100%;
    background: var(--bg-surface-2);
    border-radius: var(--radius-md);
    overflow: hidden;
  }

  .chart-svg {
    width: 100%;
    height: 100%;
  }

  .chart-area {
    opacity: 0.3;
  }

  .chart-line {
    stroke-linecap: round;
    stroke-linejoin: round;
  }

  .chart-label {
    position: absolute;
    top: var(--space-2);
    right: var(--space-2);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    color: var(--text-primary);
    background: var(--bg-surface-1);
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius-sm);
    opacity: 0.9;
  }

  .label-value {
    font-variant-numeric: tabular-nums;
  }
</style>
