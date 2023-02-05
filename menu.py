import pygame
import math
import config


class Menu:
    def __init__(self, selections: list[str]):
        self.selections = selections.copy()
        self.select_idx = 0
        self.animation_time = 0
        self.contents = []
        self.contents_height = 0
        self.selections_width = max(
            [
                pygame.font.SysFont(
                    config.DEFAULT_TEXT_FONT_NAME, config.SELECTION_MAX_SIZE
                ).size(v)[0]
                for v in selections
            ]
        )
        self.selections_height = (
            len(selections) * config.SELECTION_MAX_SIZE
            + (len(selections) - 1) * config.SELECTION_SEP_SIZE
        )

    def add_content(self, content: pygame.Surface):
        self.contents.append(content.copy())
        self.contents_height += content.get_height()

    def update(self, dt: float):
        self.animation_time = max(0, self.animation_time - dt)

    def select(self, idx: int):
        idx = max(0, min(len(self.selections) - 1, idx))
        if self.select_idx != idx:
            self.select_idx = idx
            self.animation_time = config.SELECT_ANIMATION_MAX_TIME

    def get_idx_from_screen(self, pos) -> int:
        x, y = pos
        if abs(x - config.WINDOW_WIDTH / 2) <= self.selections_width / 2:
            start_y = (
                config.WINDOW_HEIGHT + self.contents_height - self.selections_height
            ) / 2
            idx = math.floor(
                (y - start_y - config.SELECTION_SEP_SIZE / 2)
                / (config.SELECTION_MAX_SIZE + config.SELECTION_SEP_SIZE)
            )
            if 0 <= idx < len(self.selections):
                return idx
        return -1

    def handle_event(self, event: pygame.event.Event) -> str:
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.select(self.select_idx - 1)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.select(self.select_idx + 1)
            elif event.key == pygame.K_RETURN:
                return self.selections[self.select_idx]

        if event.type == pygame.MOUSEMOTION:
            idx = self.get_idx_from_screen(event.pos)
            if idx != -1:
                self.select(idx)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                idx = self.get_idx_from_screen(event.pos)
                if idx != -1:
                    return self.selections[idx]

        return str()
