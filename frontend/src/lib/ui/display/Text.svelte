<script lang="ts">
  import type { TextSchema } from "$lib/api";

  interface Props extends Partial<Omit<TextSchema, "type">> {}

  let { content = "", variant = "body" }: Props = $props();
</script>

{#if variant === "code"}
  <code class="text-code">{content}</code>
{:else}
  <span class="text-{variant}">{content}</span>
{/if}
