import pygame
import graphics
import game
import menu
from config import *


def create_start_menu():
    start_menu = menu.Menu(["开始游戏", "帮助", "退出"])
    title_font = pygame.font.SysFont(DEFAULT_TEXT_FONT_NAME, 100, True)
    start_menu.add_content(title_font.render("贪吃蛇", True, graphics.COLOR_BLACK))
    start_menu.add_content(pygame.Surface((0, 30)))
    return start_menu


def create_end_menu(score, reason):
    reason_text = "触碰边界" if reason == 1 else "触碰身体"
    reason_text = "结束原因：" + reason_text
    end_menu = menu.Menu(["重新开始", "退出"])
    title_font = pygame.font.SysFont(DEFAULT_TEXT_FONT_NAME, 80, True)
    reason_font = pygame.font.SysFont(DEFAULT_TEXT_FONT_NAME, 25)
    end_menu.add_content(title_font.render("游戏结束", True, graphics.COLOR_DARK_RED))
    end_menu.add_content(pygame.Surface((0, 30)))
    end_menu.add_content(reason_font.render(reason_text, True, graphics.COLOR_DARK_RED))
    end_menu.add_content(pygame.Surface((0, 25)))
    end_menu.add_content(graphics.render_score(score, 25))
    end_menu.add_content(pygame.Surface((0, 30)))
    return end_menu


def show_start_menu(display):
    start_menu = create_start_menu()
    clock = pygame.time.Clock()
    show_help = False
    keep_going = True
    while keep_going:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if show_help:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        show_help = False
                continue

            r = start_menu.handle_event(event)
            if r == "开始游戏":
                return True
            elif r == "帮助":
                show_help = True
            elif r == "退出":
                return False

        clock.tick(GAME_MAX_FPS)
        start_menu.update(clock.get_time() / 1000)

        display.fill(graphics.COLOR_WHITE)
        graphics.draw_menu(display, start_menu)
        if show_help:
            graphics.draw_help(display)
        pygame.display.update()


def main():
    pygame.init()
    manager = game.GameManager(GAME_WIDTH, GAME_HEIGHT)
    display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    end_menu = create_end_menu(0, 0)
    clock = pygame.time.Clock()

    keep_going = show_start_menu(display)
    game_end = False
    while keep_going:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keep_going = False
            manager.handle_event(event)
            if game_end:
                r = end_menu.handle_event(event)
                if r == "重新开始":
                    game_end = False
                    manager.reset_game()
                elif r == "退出":
                    keep_going = False

        clock.tick(GAME_MAX_FPS)
        delta = min(0.2, clock.get_time() / 1000)
        manager.update(delta)
        if manager.end and not game_end:
            game_end = True
            end_menu = create_end_menu(manager.get_score(), manager.end)
        end_menu.update(delta)

        if manager.end == 0:
            graphics.draw_game(display, manager)
        else:
            graphics.draw_end(display, manager, end_menu)
        pygame.display.update()
        
    pygame.quit()


if __name__ == "__main__":
    main()
