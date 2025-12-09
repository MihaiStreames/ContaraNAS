<script lang="ts">
  import type { TableSchema, TableColumnSchema } from "$lib/api";

  interface Props extends Partial<Omit<TableSchema, "type">> {}

  let { columns = [], data = [], empty_message = "No data" }: Props = $props();
</script>

<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        {#each columns as column}
          <th
            class:text-left={column.align === "left" || !column.align}
            class:text-center={column.align === "center"}
            class:text-right={column.align === "right"}
            style={column.width ? `width: ${column.width}` : undefined}
          >
            {column.label}
          </th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#if data.length === 0}
        <tr>
          <td colspan={columns.length} class="table-empty">
            {empty_message}
          </td>
        </tr>
      {:else}
        {#each data as row}
          <tr>
            {#each columns as column}
              <td
                class:text-left={column.align === "left" || !column.align}
                class:text-center={column.align === "center"}
                class:text-right={column.align === "right"}
              >
                {row[column.key] ?? ""}
              </td>
            {/each}
          </tr>
        {/each}
      {/if}
    </tbody>
  </table>
</div>
