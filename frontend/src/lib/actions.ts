/**
 * Action handling utilities for server-driven UI
 * Converts ActionRef objects to click handlers that POST to the backend
 */

import type { ActionRef } from "$lib/api";

export interface ActionResult {
  success: boolean;
  open_modal?: string;
  close_modal?: string;
  notify?: {
    message: string;
    variant: "info" | "success" | "warning" | "error";
  };
  refresh?: boolean;
  error?: string;
}

/**
 * Check if a value is an ActionRef
 */
export function isActionRef(value: unknown): value is ActionRef {
  return (
    typeof value === "object" &&
    value !== null &&
    "__action__" in value &&
    typeof (value as ActionRef).__action__ === "string"
  );
}

/**
 * Execute an action by POSTing to the backend
 */
export async function executeAction(
  moduleName: string,
  actionName: string,
  payload: Record<string, unknown> = {},
  token: string
): Promise<ActionResult> {
  const response = await fetch(
    `/api/modules/${moduleName}/action/${actionName}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    }
  );

  if (!response.ok) {
    const error = await response.text();
    return {
      success: false,
      error: error || `Action failed with status ${response.status}`,
    };
  }

  return await response.json();
}

/**
 * Create a click handler from an ActionRef
 */
export function createActionHandler(
  actionRef: ActionRef,
  moduleName: string,
  token: string,
  onResult?: (result: ActionResult) => void
): () => Promise<void> {
  return async () => {
    const result = await executeAction(
      moduleName,
      actionRef.__action__,
      {},
      token
    );
    onResult?.(result);
  };
}

/**
 * Process action results (open modals, show notifications, etc.)
 */
export function processActionResult(
  result: ActionResult,
  handlers: {
    openModal?: (id: string) => void;
    closeModal?: (id: string) => void;
    notify?: (
      message: string,
      variant: "info" | "success" | "warning" | "error"
    ) => void;
    refresh?: () => void;
  }
): void {
  if (result.open_modal && handlers.openModal) {
    handlers.openModal(result.open_modal);
  }
  if (result.close_modal && handlers.closeModal) {
    handlers.closeModal(result.close_modal);
  }
  if (result.notify && handlers.notify) {
    handlers.notify(result.notify.message, result.notify.variant);
  }
  if (result.refresh && handlers.refresh) {
    handlers.refresh();
  }
}
