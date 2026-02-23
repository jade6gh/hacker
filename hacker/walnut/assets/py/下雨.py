import pygame, random, sys

class Raindrop:
    def __init__(self, screen_width, screen_height):
        self.screen_width  = screen_width
        self.screen_height = screen_height
        self.reset()

    def reset(self):
        self.x      = random.randint(0, self.screen_width)
        self.y      = random.randint(-self.screen_height, 0)
        self.length = random.randint(5, 15)
        self.speed  = random.uniform(4, 10) * (self.length / 10)

    def fall(self):
        self.y += self.speed
        if self.y > self.screen_height:
            self.reset()

    def draw(self, surface):
        end_y = self.y + self.length
        pygame.draw.line(surface, (180, 180, 255), (self.x, self.y), (self.x, end_y), 1)

def main():
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Python 雨滴模拟")
    clock = pygame.time.Clock()

    # 初始化雨滴
    raindrops = [Raindrop(screen_width, screen_height) for _ in range(300)]

    # 主循环
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 填充背景
        screen.fill((10, 10, 30))

        # 更新并绘制每个雨滴
        for drop in raindrops:
            drop.fall()
            drop.draw(screen)

        # 刷新显示
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
