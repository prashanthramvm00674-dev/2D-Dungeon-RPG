# 2D Dungeon RPG

An intermediate-to-advanced 2D Dungeon RPG built with Python and Pygame.

## Technology

- Python 3.13
- Pygame 2.6.1
- Git
- GitHub

## Project Status

packaging


## Current gameplay systems

- Procedural, enclosed dungeon rooms and connected corridors.
- Player movement, enemy AI, combat, XP, leveling, equipment, inventory, and potion loot.
- Four-wave survival run with controlled reinforcement spawning, followed by the **Ashen Titan** boss encounter.
- Boss combat features a dedicated health bar, a dodgeable targeted slam, and a phase-two shockwave.
- Manual saves preserve player stats, inventory/equipment, wave progress, enemies, loot, quest status, and boss attack state.
- Open the pause menu with **Esc** to save/load or open **Settings**; **F5** saves and **F9** loads the current slot.
- Settings remember fullscreen preference, dungeon lighting, scene finishing, and save-on-exit. Saves and settings are stored locally in the ignored `saves` folder.
- The final victory screen appears only after the guardian falls; the main quest grants **50 bonus XP** once per run.
- Main quest, **The Dungeon Purge**, tracked in the quest journal.
- Meet the **Ashen Warden** near the starting chamber and press **E** to learn about the dungeon and current wave.
- Dialogue pauses combat; use **E**, **Enter**, or **Space** to advance, and **Esc** to close it.
- Press **J** during gameplay to open or close the quest journal; **Esc** closes the journal.
- Surviving all four waves and defeating the Ashen Titan completes the main quest and grants **50 bonus XP** once per run.
- Press **I** for inventory, **1–5** for hotbar slots, and **F11** or **Alt+Enter** to toggle fullscreen.
