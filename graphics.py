import pygame
import pygame.gfxdraw
import math
import config
import game
import menu

COLOR_BLACK = pygame.Color("black")
COLOR_BLUE = pygame.Color("blue")
COLOR_CYAN = pygame.Color("cyan")
COLOR_DARK_RED = pygame.Color("darkred")
COLOR_DIM_GRAY = pygame.Color("dimgray")
COLOR_GOLD = pygame.Color("gold")
COLOR_GRAY = pygame.Color("gray")
COLOR_RED = pygame.Color("red")
COLOR_WHITE = pygame.Color("white")

FOOD_COLOR = {
    game.FOOD_TYPE_NORMAL: COLOR_GRAY,
    game.FOOD_TYPE_DOUBLESCORE: COLOR_GOLD,
    game.FOOD_TYPE_SLOWDOWN: COLOR_BLUE,
    game.FOOD_TYPE_SPEEDUP: COLOR_RED,
}
SELECTED_COLOR = COLOR_CYAN
UNSELECT_COLOR = COLOR_GRAY


def fill_aarectangle(
    surface: pygame.Surface,
    color: pygame.Color,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> None:
    x1f = math.floor(x1)
    y1f = math.floor(y1)
    width = math.ceil(x2) - x1f
    height = math.ceil(y2) - y1f
    x = max(0, x1f)
    y = max(0, y1f)
    w = width if x + width < surface.get_width() else width - 1
    h = height if y + height < surface.get_height() else height - 1
    aasurface = pygame.Surface((width, height), pygame.SRCALPHA)
    aasurface.blit(surface.subsurface((x, y, w, h)), (x1f - x, y1f - y))
    aasurface = pygame.transform.scale(
        aasurface, (config.SSAA * width, config.SSAA * height)
    )
    pygame.gfxdraw.box(
        aasurface,
        (
            round(config.SSAA * (x1 - math.floor(x1))),
            round(config.SSAA * (y1 - math.floor(y1))),
            round(config.SSAA * (x2 - x1)),
            round(config.SSAA * (y2 - y1)),
        ),
        color,
    )
    aasurface = pygame.transform.smoothscale(aasurface, (width, height))
    surface.blit(aasurface, (math.floor(x1), math.floor(y1)))


def fill_aacircle(
    surface: pygame.Surface, color: pygame.Color, x: float, y: float, r: float
) -> None:
    rx_floor = math.floor(x - r)
    ry_floor = math.floor(y - r)
    width = math.ceil(x + r) - rx_floor
    height = math.ceil(y + r) - ry_floor
    aar = config.SSAA * r
    aax = aar + round(config.SSAA * (x - r - rx_floor))
    aay = aar + round(config.SSAA * (y - r - ry_floor))
    sub_x = max(rx_floor, 0)
    sub_y = max(ry_floor, 0)
    sub_w = width if sub_x + width < surface.get_width() else width - 1
    sub_h = height if sub_y + height < surface.get_height() else height - 1
    aasurface = pygame.Surface((width, height), pygame.SRCALPHA)
    aasurface.blit(
        surface.subsurface((sub_x, sub_y, sub_w, sub_h)),
        (sub_x - rx_floor, sub_y - ry_floor),
    )
    aasurface = pygame.transform.scale(
        aasurface, (config.SSAA * width, config.SSAA * height)
    )
    pygame.draw.circle(aasurface, color, (aax, aay), aar)
    aasurface = pygame.transform.smoothscale(aasurface, (width, height))
    surface.blit(aasurface, (rx_floor, ry_floor))


def draw_snake(surface: pygame.Surface, snake: game.Snake) -> None:
    for k1, k2 in zip(snake.key_points[:-1], snake.key_points[1:]):
        o = k1.orientation
        fill_aacircle(
            surface,
            COLOR_DIM_GRAY,
            (k2.x + 0.5) * config.SNAKE_SIZE,
            (k2.y + 0.5) * config.SNAKE_SIZE,
            config.SNAKE_SIZE / 2,
        )
        if k1.x > k2.x or k1.y > k2.y:
            k1, k2 = k2, k1
        rx1 = k1.x * config.SNAKE_SIZE
        rx2 = k2.x * config.SNAKE_SIZE + config.SNAKE_SIZE
        ry1 = k1.y * config.SNAKE_SIZE
        ry2 = k2.y * config.SNAKE_SIZE + config.SNAKE_SIZE
        if o in [game.SNAKE_DOWN, game.SNAKE_UP]:
            ry1 += config.SNAKE_SIZE / 2
            ry2 -= config.SNAKE_SIZE / 2
        if o in [game.SNAKE_LEFT, game.SNAKE_RIGHT]:
            rx1 += config.SNAKE_SIZE / 2
            rx2 -= config.SNAKE_SIZE / 2
        fill_aarectangle(surface, COLOR_DIM_GRAY, rx1, ry1, rx2, ry2)

    head = snake.key_points[0]
    fill_aacircle(
        surface,
        COLOR_BLACK,
        (head.x + 0.5) * config.SNAKE_SIZE,
        (head.y + 0.5) * config.SNAKE_SIZE,
        config.SNAKE_SIZE / 2,
    )


def draw_foods(surface: pygame.Surface, foods: list[game.Food]) -> None:
    for food in foods:
        fill_aacircle(
            surface,
            FOOD_COLOR[food.type],
            (food.x + 0.5) * config.SNAKE_SIZE,
            (food.y + 0.5) * config.SNAKE_SIZE,
            config.SNAKE_SIZE / 2,
        )


def render_score(score: int, font_size: int) -> pygame.Surface:
    score_font = pygame.font.SysFont(config.DEFAULT_TEXT_FONT_NAME, font_size)
    prev_text = score_font.render("得分： ", True, COLOR_BLACK)
    score_text = score_font.render(str(score), True, COLOR_GOLD)

    prev_width = prev_text.get_width()
    score_width = score_text.get_width()
    surface = pygame.Surface(
        (prev_width + score_width, prev_text.get_height()), pygame.SRCALPHA
    )
    surface.blit(prev_text, [0, 0])
    surface.blit(score_text, [0 + prev_width, 0])
    return surface


def draw_score(surface: pygame.Surface, score: int, font_size: int, y: int) -> None:
    rs = render_score(score, font_size)
    start_x = (surface.get_width() - rs.get_width()) // 2
    surface.blit(rs, (start_x, y))


def draw_game(
    surface: pygame.Surface, manager: game.GameManager, score: bool = True
) -> None:
    surface.fill(COLOR_WHITE)
    draw_snake(surface, manager.snake)
    draw_foods(surface, manager.foods)
    if score:
        draw_score(surface, manager.get_score(), 20, 5)


def draw_menu(surface: pygame.Surface, game_menu: menu.Menu) -> None:
    drawing_y = (
        surface.get_height() - game_menu.contents_height - game_menu.selections_height
    ) / 2
    center_x = surface.get_width() / 2

    for v in game_menu.contents:
        surface.blit(v, (center_x - v.get_width() / 2, drawing_y))
        drawing_y += v.get_height()

    for i, selection in enumerate(game_menu.selections):
        size = config.SELECTION_MIN_SIZE
        color = UNSELECT_COLOR
        if i == game_menu.select_idx:
            size += round(
                (config.SELECT_ANIMATION_MAX_TIME - game_menu.animation_time)
                / config.SELECT_ANIMATION_MAX_TIME
                * (config.SELECTION_MAX_SIZE - config.SELECTION_MIN_SIZE)
            )
            color = SELECTED_COLOR

            triangle_size = config.SELECTION_MAX_SIZE / 4
            base = (
                center_x - game_menu.selections_width / 2 - triangle_size,
                drawing_y + config.SELECTION_MAX_SIZE / 2,
            )
            triangle = [
                base,
                (base[0] - triangle_size, base[1] - triangle_size),
                (base[0] - triangle_size, base[1] + triangle_size),
            ]
            pygame.gfxdraw.aapolygon(surface, triangle, SELECTED_COLOR)
            pygame.gfxdraw.filled_polygon(surface, triangle, SELECTED_COLOR)

        font = pygame.font.SysFont(config.DEFAULT_TEXT_FONT_NAME, size)
        text = font.render(selection, True, color)
        dy = (config.SELECTION_MAX_SIZE - text.get_height()) / 2
        surface.blit(text, (center_x - text.get_width() / 2, drawing_y + dy))
        drawing_y += config.SELECTION_MAX_SIZE + config.SELECTION_SEP_SIZE


def draw_end(
    surface: pygame.Surface, manager: game.GameManager, end_menu: menu.Menu
) -> None:
    draw_game(surface, manager, False)
    color = COLOR_WHITE
    color.a = 128
    pygame.gfxdraw.box(surface, surface.get_rect(), color)
    draw_menu(surface, end_menu)


def draw_help(surface: pygame.Surface) -> None:
    color = COLOR_CYAN
    color.a = 180
    pygame.gfxdraw.box(surface, surface.get_rect(), color)

    color = COLOR_WHITE
    color.a = 230
    pygame.gfxdraw.box(surface, surface.get_rect(), color)

    font_size = 25
    font = pygame.font.SysFont(config.DEFAULT_TEXT_FONT_NAME, font_size)
    line_size = font.get_linesize()
    help_text = config.GAME_HELP_TEXT

    text_y = line_size
    i = 0
    for j in range(i, len(help_text)):
        if (
            help_text[j] == "\n"
            or font.size(help_text[i : j + 1])[0] > surface.get_width() - 2 * line_size
        ):
            render_text = font.render(help_text[i:j], True, COLOR_BLACK)
            surface.blit(render_text, (line_size, text_y))
            i = j + 1 if help_text[j] == "\n" else j
            text_y += line_size

    render_text = font.render(help_text[i:], True, COLOR_BLACK)
    surface.blit(render_text, (line_size, text_y))
