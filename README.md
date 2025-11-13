# ContaraNAS

A modular desktop application for monitoring and managing NAS systems at home.

## Features

- 🎮 Steam library monitoring and analysis
- 📊 Real-time drive usage visualization
- 🔄 Automatic game installation tracking
- 🖥️ Native desktop GUI with NiceGUI

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/MihaiStreames/ContaraNAS
cd ContaraNAS

# Install dependencies
uv sync

# Run the application
uv run -m ContaraNAS.main
```

### Requirements

- Python 3.9+
- Steam installed (for Steam module)

## Architecture

ContaraNAS uses a modular architecture with the following components:

- **Core**: Module management, event bus, utilities
- **Modules**: Steam, System, etc. (pluggable)
- **GUI**: NiceGUI-based dashboard with reactive components
