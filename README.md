# Roast Roulette 🔥🎲

<img width="800" alt="image" src="https://github.com/user-attachments/assets/ded4ae9b-36b8-4643-ad82-26622c93756d" />

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

## Screenshots

**Lobby**

<img width="800" alt="image" src="https://github.com/user-attachments/assets/60e17bfc-c779-42dd-93d7-3b52e7815733" />

**Photo Upload Stage**

<img width="800" alt="image" src="https://github.com/user-attachments/assets/cd3f7238-fda0-4aa1-bff7-d46e0b6f9207" />


