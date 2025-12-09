<script lang="ts">
  import type { StatSchema } from "$lib/api";

  interface Props extends Partial<Omit<StatSchema, "type">> {}

  let { label = "", value = "" }: Props = $props();
</script>

<div class="stat">
  <span class="stat-value">{value}</span>
  <span class="stat-label">{label}</span>
</div>
