# DriftSystem v0.1

## Semantic Scene Generation Engine for Minecraft

DriftSystem is an AI-powered semantic scene generation engine that dynamically creates immersive Minecraft environments based on natural language input and player context.

---

## Architecture Overview

```
Player Input (Natural Language)
           ↓
    Semantic Engine
    - Parse player intent
    - Extract semantic tags
    - Map to narrative themes
           ↓
    Scene Prediction
    - Score candidate scenes
    - Select best match
    - Determine scene parameters
           ↓
    Theme Resolver
    - Load active theme pack
    - Apply visual style rules
    - Configure atmospheric settings
           ↓
    Fragment Selection
    - Query fragment library
    - Compose scene fragments
    - Generate spatial layout
           ↓
    Scene Assembler
    - Combine fragments into patch
    - Resolve entity placements
    - Generate loot containers
           ↓
    World Patch
    - Serializes to JSON
    - Transmits to plugin
           ↓
    Minecraft Plugin
    - Applies world modifications
    - Spawns entities
    - Triggers cutscene events
```

---

## Project Structure

```
drift-system/
├── backend/              # Python backend server
│   ├── app/
│   │   ├── api/         # REST API endpoints
│   │   ├── content/     # Scene and fragment definitions
│   │   ├── core/        # Core narrative engine
│   │   │   ├── narrative/
│   │   │   │   ├── scene_library.py      # Scene registry
│   │   │   │   ├── scene_assembler.py    # Fragment composition
│   │   │   │   └── semantic_engine.py    # Semantic processing
│   │   │   └── runtime/
│   │   │       └── resource_canonical.py # Resource canonicalization
│   │   └── routers/    # API route handlers
│   └── requirements.txt
│
├── plugin/              # Minecraft plugin (Java)
│   └── mc_plugin/
│       └── src/main/java/com/driftmc/
│           ├── DriftPlugin.java           # Main plugin class
│           ├── commands/                  # Plugin commands
│           ├── listeners/                 # Event listeners
│           └── scene/                     # Scene patch execution
│
├── content/            # Content definitions (exported from backend)
│   ├── scenes/
│   │   ├── fragments/   # Reusable scene fragments
│   │   └── presets/     # Scene scoring presets
│   └── semantic/        # Semantic mapping rules
│
├── docs/               # Documentation
│   ├── DRIFTSYSTEM_ARCHITECTURE_V0.5.md
│   ├── DRIFTSYSTEM_ROADMAP.md
│   └── SCENE_SCORING_PRESETS.md
│
└── scripts/            # Utility scripts
    ├── switch_scene_scoring_preset.sh
    └── scene_influence_15min_validation.sh
```

---

## Core Modules

### Semantic Engine (`backend/app/core/narrative/semantic_engine.py`)
- Processes natural language input
- Extracts semantic tags and intent
- Maps player input to scene themes

### Scene Library (`backend/app/core/narrative/scene_library.py`)
- Central registry of all scenes
- Scene metadata management
- Scene query and filtering

### Fragment Loader (`backend/app/content/scenes/`)
- Loads fragment definitions
- Manages fragment composition rules
- Handles fragment inheritance

### Scene Assembler (`backend/app/core/narrative/scene_assembler.py`)
- Composes scenes from fragments
- Generates world patch data
- Resolves entity and block placements

### World Patch Generator (`backend/app/core/runtime/resource_canonical.py`)
- Serializes scene data to JSON
- Canonicalizes resource names
- Validates patch integrity

### Minecraft Plugin Bridge (`plugin/mc_plugin/`)
- Receives world patches via HTTP
- Applies modifications to Minecraft world
- Handles player interaction events

---

## Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

### Plugin Setup
```bash
cd plugin/mc_plugin
./build_plugin.sh
# Copy resulting .jar to Minecraft plugins/
```

---

## Version

**v0.1-semantic-scene-engine**

Initial release of the DriftSystem semantic scene generation engine.

---

## License

See LICENSE file for details.
