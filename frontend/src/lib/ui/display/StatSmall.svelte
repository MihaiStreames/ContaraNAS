<script lang="ts">
  import type { StatSmallSchema } from "$lib/api";

  interface Props extends Partial<Omit<StatSmallSchema, "type">> {}

  let { label = "", value = "" }: Props = $props();
</script>

<div class="stat-small">
  <span class="stat-small-label">{label}</span>
  <span class="stat-small-value">{value}</span>
</div>
