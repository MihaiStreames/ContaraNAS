<script lang="ts">
  import type { AlertSchema } from "$lib/api";
  import { Info, CheckCircle, AlertTriangle, XCircle } from "lucide-svelte";

  interface Props extends Partial<Omit<AlertSchema, "type">> {}

  let { message = "", variant = "info", title = null }: Props = $props();

  const iconMap = {
    info: Info,
    success: CheckCircle,
    warning: AlertTriangle,
    error: XCircle,
  };

  const IconComponent = $derived(iconMap[variant]);
</script>

<div class="alert alert-{variant}">
  <span class="alert-icon">
    <IconComponent size={16} />
  </span>
  <div class="alert-content">
    {#if title}
      <div class="alert-title">{title}</div>
    {/if}
    {message}
  </div>
</div>
