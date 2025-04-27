# Roast Roulette 🔥🎲
s
A multiplayer party game where AI roasts players' photos.

## Quick Start

**Prerequisites**: Docker Desktop

1. **Install Docker**: https://docs.docker.com/desktop/setup/install/windows-install/

2. **Run `just` command**:
    ```bash
    just
    ```
3. **Open `http://localhost:8000`**

## Project Structure️

Key files and directories:
- `main/games/` - Game logic
  - `models.py` - Database models (Games, Players, Photos)
  - `views.py` - Page handlers
  - `urls.py` - URL routing
- `main/templates/` - Jinja templates
- `main/static/` - Avatars & images
