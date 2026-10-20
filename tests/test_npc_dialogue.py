"""Regression checks for Warden proximity, contextual dialogue, and UI paging."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from entities.npc import AshenWarden
from ui.dialogue_ui import DialogueUI


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    warden = AshenWarden(100, 100)
    player = SimpleNamespace(rect=pygame.Rect(110, 110, 40, 40))
    assert warden.is_in_range(player)

    player.rect.topleft = (700, 500)
    assert not warden.is_in_range(player)

    waves = SimpleNamespace(
        current_wave=1,
        total_waves=4,
        is_victory=False,
        is_intermission=False,
    )
    quest = SimpleNamespace(completed=False)
    opening = warden.dialogue_for(waves, quest)
    assert len(opening) == 3
    assert "Ashen Warden" in opening[0]
    assert "four waves" in opening[1]

    waves.current_wave = 2
    waves.is_intermission = True
    intermission = warden.dialogue_for(waves, quest)
    assert any("Wave 3" in line for line in intermission)

    waves.is_intermission = False
    waves.is_victory = True
    victory = warden.dialogue_for(waves, quest)
    assert any("complete" in line.lower() for line in victory)

    dialogue = DialogueUI()
    dialogue.open(warden.NAME, opening)
    assert dialogue.visible
    assert dialogue.line_index == 0
    dialogue.render(screen)

    assert dialogue.advance()
    assert dialogue.line_index == 1
    dialogue.render(screen)
    assert dialogue.advance()
    assert dialogue.line_index == 2
    assert not dialogue.advance()
    assert not dialogue.visible

    dialogue.open(warden.NAME, opening)
    dialogue.close()
    assert not dialogue.visible
    assert dialogue.lines == ()

    pygame.quit()
    print("NPC dialogue tests passed: proximity, wave context, rendering, paging, and close.")


if __name__ == "__main__":
    main()
