from ContaraNAS.gui.theme.theme import ColorShades, Shadows, Theme, ThemeMode


LIGHT_THEME = Theme(
    name="Light",
    mode=ThemeMode.LIGHT,
    # Backgrounds
    bg_base="#f0f2f5",
    bg_surface="#ffffff",
    bg_elevated="#f8fafc",
    bg_input="#ffffff",
    # Text
    text_primary="#1a1a2e",
    text_secondary="#4a5568",
    text_muted="#a0aec0",
    text_inverse="#ffffff",
    # Borders
    border_default="#e2e8f0",
    border_subtle="#f1f5f9",
    # Primary (Blue)
    primary=ColorShades("#1e40af", "#1d4ed8", "#2563eb", "#3b82f6", "#60a5fa"),
    # Success (Green)
    success=ColorShades("#166534", "#15803d", "#22c55e", "#4ade80", "#86efac"),
    # Warning (Orange)
    warning=ColorShades("#c2410c", "#ea580c", "#f97316", "#fb923c", "#fdba74"),
    # Danger (Red)
    danger=ColorShades("#b91c1c", "#dc2626", "#ef4444", "#f87171", "#fca5a5"),
    # Info (Cyan)
    info=ColorShades("#0e7490", "#0891b2", "#06b6d4", "#22d3ee", "#67e8f9"),
    # Neutral (Gray)
    neutral=ColorShades("#1f2937", "#374151", "#6b7280", "#9ca3af", "#d1d5db"),
    # Shadows
    shadows=Shadows(
        none="none",
        sm="inset 0 1px 0 0 rgba(255,255,255,0.8), 0 1px 3px 0 rgba(0,0,0,0.1)",
        md="inset 0 1px 0 0 rgba(255,255,255,0.9), 0 4px 6px -1px rgba(0,0,0,0.1)",
        lg="inset 0 1px 0 0 rgba(255,255,255,1), 0 10px 15px -3px rgba(0,0,0,0.1)",
        inset="inset 0 2px 4px rgba(0,0,0,0.1), inset 0 -1px 0 rgba(255,255,255,0.5)",
    ),
    # Graph colors
    graph_primary="#2563eb",
    graph_secondary="#22c55e",
    graph_tertiary="#f97316",
    graph_quaternary="#8b5cf6",
    graph_fill_opacity=0.3,
)
