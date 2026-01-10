<script lang="ts">
  import type { TableSchema } from "$lib/api";
  import { browser } from "$app/environment";

  let convertFileSrc: ((path: string) => string) | null = null;

  if (browser) {
    (async () => {
      const mod = await import("@tauri-apps/api/core");
      convertFileSrc = mod.convertFileSrc;
    })();
  }

  interface Props extends Partial<Omit<TableSchema, "type">> {}

  let {
    columns = [],
    data = [],
    empty_message = "No data",
    sortable = false,
    default_sort_key = null,
    default_sort_desc = true,
  }: Props = $props();

  // Sort state
  let sortKey = $state<string | null>(default_sort_key);
  let sortDesc = $state(default_sort_desc);

  // Sorted data
  const sortedData = $derived.by(() => {
    if (!sortable || !sortKey) return data;

    return [...data].sort((a, b) => {
      // Look for a _sort suffix field first (e.g., size_sort for size column)
      const sortSuffix = `${sortKey}_sort`;
      const aVal = a[sortSuffix] ?? a[sortKey!];
      const bVal = b[sortSuffix] ?? b[sortKey!];

      // Handle numbers (including those stored as strings like "45.2 GB")
      const aNum = typeof aVal === "number" ? aVal : parseFloat(String(aVal));
      const bNum = typeof bVal === "number" ? bVal : parseFloat(String(bVal));

      // If both are valid numbers, compare numerically
      if (!isNaN(aNum) && !isNaN(bNum)) {
        return sortDesc ? bNum - aNum : aNum - bNum;
      }

      // String comparison
      const aStr = String(aVal ?? "");
      const bStr = String(bVal ?? "");
      const cmp = aStr.localeCompare(bStr);
      return sortDesc ? -cmp : cmp;
    });
  });

  function handleHeaderClick(column: (typeof columns)[0]) {
    if (!sortable || column.sortable === false) return;

    if (sortKey === column.key) {
      sortDesc = !sortDesc;
    } else {
      sortKey = column.key;
      sortDesc = true;
    }
  }
</script>

<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        {#each columns as column}
          {@const columnSortable = sortable && column.sortable !== false}
          <th
            class:text-left={column.align === "left" || !column.align}
            class:text-center={column.align === "center"}
            class:text-right={column.align === "right"}
            class:sortable={columnSortable}
            class:sorted={sortKey === column.key}
            style={column.width ? `width: ${column.width}` : undefined}
            onclick={() => handleHeaderClick(column)}
          >
            <span class="th-content">
              {column.label}
              {#if columnSortable}
                <span
                  class="sort-indicator"
                  class:active={sortKey === column.key}
                >
                  {#if sortKey === column.key}
                    {sortDesc ? "▼" : "▲"}
                  {:else}
                    ▼
                  {/if}
                </span>
              {/if}
            </span>
          </th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#if sortedData.length === 0}
        <tr>
          <td colspan={columns.length} class="table-empty">
            {empty_message}
          </td>
        </tr>
      {:else}
        {#each sortedData as row}
          <tr>
            {#each columns as column}
              <td
                class:text-left={column.align === "left" || !column.align}
                class:text-center={column.align === "center"}
                class:text-right={column.align === "right"}
              >
                {#if column.render === "image"}
                  {@const imgPath = row[column.key] as string}
                  {@const imgSrc =
                    browser && convertFileSrc && imgPath
                      ? convertFileSrc(imgPath)
                      : ""}
                  {@const imgAlt = row["name"] as string}
                  <img src={imgSrc} alt={imgAlt ?? ""} class="table-image" />
                {:else}
                  {row[column.key] ?? ""}
                {/if}
              </td>
            {/each}
          </tr>
        {/each}
      {/if}
    </tbody>
  </table>
</div>

<style>
  .th-content {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
  }

  .sortable {
    cursor: pointer;
    user-select: none;
  }

  .sortable:hover {
    background: var(--bg-surface-2);
  }

  .sort-indicator {
    opacity: 0.3;
    font-size: 0.7em;
  }

  .sort-indicator.active {
    opacity: 1;
  }

  .table-image {
    width: 120px;
    height: 56px;
    object-fit: cover;
    border-radius: var(--radius-sm);
    vertical-align: middle;
  }
</style>
