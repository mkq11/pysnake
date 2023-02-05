import math
import random
import pygame

FOOD_TYPE_NORMAL = -1
FOOD_TYPE_DOUBLESCORE = 0
FOOD_TYPE_SPEEDUP = 1
FOOD_TYPE_SLOWDOWN = 2

SNAKE_UP = 0
SNAKE_LEFT = 1
SNAKE_RIGHT = 2
SNAKE_DOWN = 3

SNAKE_STATE_NORMAL = 0
SNAKE_STATE_SPEEDUP = 1
SNAKE_STATE_SLOWDOWN = 2

SNAKE_INITIAL_LENGTH = 3


class Food:
    def __init__(self, xmin, xmax, ymin, ymax):
        xmu = (xmin + xmax) / 2
        xvar = (xmax - xmin) / 4
        self.x = random.normalvariate(xmu, xvar)
        while not xmin < self.x < xmax:
            self.x = random.normalvariate(xmu, xvar)

        ymu = (ymin + ymax) / 2
        yvar = (ymax - ymin) / 4
        self.y = random.normalvariate(ymu, yvar)
        while not ymin < self.y < ymax:
            self.y = random.normalvariate(ymu, yvar)

        self.type = random.randrange(0, 10)
        if self.type > 2:
            self.type = FOOD_TYPE_NORMAL

    def is_close_to(self, pos):
        return (pos.x - self.x) ** 2 + (pos.y - self.y) ** 2 < 1


class SnakeKeyPoint:
    def __init__(self, x, y, orientation):
        self.x = x
        self.y = y
        self.orientation = orientation

    def distance(self, pos):
        return math.sqrt((self.x - pos.x) ** 2 + (self.y - pos.y) ** 2)


class Snake:
    def move(self, time):
        self.state_time -= time
        if self.state_time < 0:
            self.state = SNAKE_STATE_NORMAL
        next = self.key_points[0]
        step_size = time * self.get_speed()
        xmove = [0, -1, 1, 0]
        ymove = [-1, 0, 0, 1]
        next.x += step_size * xmove[next.orientation]
        next.y += step_size * ymove[next.orientation]

        length_sum = 0
        for i, j in zip(self.key_points[1:], self.key_points[:-1]):
            length_sum += i.distance(j)

        if length_sum > self.length:
            while len(self.key_points) >= 2:
                last = self.key_points[-1]
                before = self.key_points[-2]
                last_length = last.distance(before)
                surplus = length_sum - self.length
                if last_length > surplus:
                    last.x -= (last.x - before.x) / last_length * surplus
                    last.y -= (last.y - before.y) / last_length * surplus
                    break
                else:
                    length_sum -= last_length
                    self.key_points.pop()

    def eat(self, food):
        self.length += 1
        if food.type == FOOD_TYPE_DOUBLESCORE:
            self.length += 1
        if food.type == FOOD_TYPE_SPEEDUP:
            self.state = SNAKE_STATE_SPEEDUP
            self.state_time = 100 / self.get_speed()
        if food.type == FOOD_TYPE_SLOWDOWN:
            self.state = SNAKE_STATE_SLOWDOWN
            self.state_time = 50 / self.get_speed()

    def is_close_to_body(self, pos):
        length_sum = 0
        for k1, k2 in zip(self.key_points[:-1], self.key_points[1:]):
            last_sum = length_sum
            length_sum += k1.distance(k2)
            if length_sum < 1:
                continue
            if length_sum > 1 and last_sum < 1:
                xchange = [0, 1, -1, 0]
                ychange = [1, 0, 0, -1]
                k1 = SnakeKeyPoint(
                    k1.x + xchange[k1.orientation] * (1 - last_sum),
                    k1.y + ychange[k1.orientation] * (1 - last_sum),
                    k1.orientation,
                )
            if k2.distance(pos) < 1:
                return True
            if k1.x == k2.x:
                if min(k1.y, k2.y) < pos.y < max(k1.y, k2.y):
                    if abs(k1.x - pos.x) < 1:
                        return True
            else:
                if min(k1.x, k2.x) < pos.x < max(k1.x, k2.x):
                    if abs(k1.y - pos.y) < 1:
                        return True
        return False

    def set_orientation(self, orientation):
        front = self.key_points[0]
        if len(self.key_points) >= 2:
            if orientation == front.orientation:
                return
            if front.distance(self.key_points[1]) <= 1:
                return
            if front.orientation + orientation == 3:
                return
        self.key_points.insert(0, SnakeKeyPoint(front.x, front.y, orientation))

    def get_speed(self):
        speed = (self.length + 5) / 2
        if self.state == SNAKE_STATE_SPEEDUP:
            speed *= 2
        if self.state == SNAKE_STATE_SLOWDOWN:
            speed /= 2
        return speed

    def reset(self, x, y):
        self.length = SNAKE_INITIAL_LENGTH
        self.key_points = [SnakeKeyPoint(x, y, SNAKE_LEFT)]
        self.state = SNAKE_STATE_NORMAL
        self.state_time = 0.0


class GameManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.snake = Snake()
        self.foods = []
        self.reset_game()

    def update(self, dt):
        if not self.playing or self.end != 0:
            return

        self.snake.move(dt)
        head = self.snake.key_points[0]
        if not 0 < head.x < self.width - 1 or not 0 < head.y < self.height - 1:
            self.end = 1
        if self.snake.is_close_to_body(head):
            self.end = 2

        foods = []
        for food in self.foods:
            if self.snake.is_close_to_body(food) or head.distance(food) < 1:
                self.snake.eat(food)
            else:
                foods.append(food)
        self.foods = foods

        self.food_time += dt
        if len(foods) >= 3:
            self.food_time = max(self.width, self.height) / self.snake.get_speed() / 4
        if self.food_time > max(self.width, self.height) / self.snake.get_speed() / 2:
            self.create_new_food()
            self.food_time = 0

    def reset_game(self):
        self.end = 0
        self.playing = False
        self.snake.reset(self.width / 2, self.height / 2)
        self.foods.clear()
        self.food_time = max(self.width, self.height) / self.snake.get_speed() * 0.45

    def set_snake_orientation(self, orientation):
        if self.end == 0:
            self.playing = True
            self.snake.set_orientation(orientation)

    def create_new_food(self):
        satisfy = False
        while not satisfy:
            new_food = Food(0, self.width - 1, 0, self.height - 1)
            satisfy = True
            if self.snake.is_close_to_body(new_food):
                satisfy = False
            for food in self.foods:
                if new_food.is_close_to(food):
                    satisfy = False
                    break
            head = self.snake.key_points[0]
            if new_food.is_close_to(head):
                satisfy = False
        self.foods.append(new_food)

    def get_score(self):
        return self.snake.length - SNAKE_INITIAL_LENGTH

    def handle_event(self, event):
        if self.end == 0:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    self.set_snake_orientation(SNAKE_UP)
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    self.set_snake_orientation(SNAKE_LEFT)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.set_snake_orientation(SNAKE_DOWN)
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    self.set_snake_orientation(SNAKE_RIGHT)
