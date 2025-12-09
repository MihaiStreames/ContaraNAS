/**
 * Action handling utilities for server-driven UI
 * Converts ActionRef objects to click handlers that POST to the backend
 */

import type { ActionRef } from "$lib/api";

// Individual result types from the backend
interface OpenModalResult {
  type: "open_modal";
  modal_id: string;
}

interface CloseModalResult {
  type: "close_modal";
  modal_id?: string;
}

interface NotifyResult {
  type: "notify";
  message: string;
  variant: "info" | "success" | "warning" | "error";
  title?: string;
}

interface RefreshResult {
  type: "refresh";
}

type ResultItem =
  | OpenModalResult
  | CloseModalResult
  | NotifyResult
  | RefreshResult;

export interface ActionResult {
  success: boolean;
  module?: string;
  action?: string;
  results?: ResultItem[];
  error?: string;
}

/**
 * Extended ActionRef with optional params
 */
export interface ActionRefWithParams extends ActionRef {
  __params__?: Record<string, unknown> | null;
}

/**
 * Check if a value is an ActionRef
 */
export function isActionRef(value: unknown): value is ActionRefWithParams {
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
  if (!result.results) return;

  for (const item of result.results) {
    switch (item.type) {
      case "open_modal":
        handlers.openModal?.(item.modal_id);
        break;
      case "close_modal":
        handlers.closeModal?.(item.modal_id ?? "");
        break;
      case "notify":
        handlers.notify?.(item.message, item.variant);
        break;
      case "refresh":
        handlers.refresh?.();
        break;
    }
  }
}
