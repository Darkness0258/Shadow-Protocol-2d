import pygame, sys, random, os

pygame.init()
WIDTH, HEIGHT = 1920, 1020
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shadow Protocol 2d")
clock = pygame.time.Clock()
FPS = 60
pygame.mixer.init()

WHITE=(255,255,255)
RED=(220,60,60)
GREEN=(60,220,120)
YELLOW=(240,220,70)

ASSETS="assets/"
BG=pygame.image.load(ASSETS+"background.png").convert()
PLAYER_IMG=pygame.image.load(ASSETS+"player.png").convert_alpha()
ENEMY_IMG=pygame.image.load(ASSETS+"enemy.png").convert_alpha()

font=pygame.font.SysFont("consolas",20)
big=pygame.font.SysFont("consolas",48)
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.play(-1)


def load_highscore():
    return int(open("highscore.txt").read()) if os.path.exists("highscore.txt") else 0

def save_highscore(s):
    open("highscore.txt","w").write(str(s))

highscore = load_highscore()

class Player:
    def __init__(self):
        self.pos=pygame.Vector2(WIDTH//2,HEIGHT//2)
        self.health=100
        self.speed=5
        self.damage=25
    def update(self):
        k=pygame.key.get_pressed()
        if k[pygame.K_w]: self.pos.y-=self.speed
        if k[pygame.K_s]: self.pos.y+=self.speed
        if k[pygame.K_a]: self.pos.x-=self.speed
        if k[pygame.K_d]: self.pos.x+=self.speed
    def draw(self):
        screen.blit(PLAYER_IMG,self.pos-(32,32))

class Bullet:
    def __init__(self,pos,dir):
        self.pos=pygame.Vector2(pos)
        self.vel=dir*12
    def update(self):
        self.pos+=self.vel
    def draw(self):
        pygame.draw.circle(screen,YELLOW,self.pos,4)


class Enemy:
    def __init__(self,lvl):
        self.pos=pygame.Vector2(random.randint(0,WIDTH),random.randint(0,HEIGHT))
        self.health=40+lvl*5
        self.speed=2+lvl*0.05
        self.damage=0.3
    def update(self,p):
        d=p.pos-self.pos
        if d.length()>0:
            self.pos+=d.normalize()*self.speed
    def draw(self):
        screen.blit(ENEMY_IMG,self.pos-(32,32))

class Boss(Enemy):
    def __init__(self,lvl):
        super().__init__(lvl)
        self.max_health=400+lvl*60
        self.health=self.max_health
        self.speed=2.5
        self.damage=1.2
    def draw_bar(self):
        r=self.health/self.max_health
        pygame.draw.rect(screen,RED,(300,15,400,15))
        pygame.draw.rect(screen,GREEN,(300,15,400*r,15))
        pygame.draw.rect(screen,WHITE,(300,15,400,15),2)

def reset_game():
    global player, bullets, enemies, boss, level, kills, score, level_timer, state
    player=Player()
    bullets=[]
    enemies=[]
    boss=None
    level=1
    kills=0
    score=0
    level_timer=0
    spawn_level()
    state="PLAY"

LEVEL_GOAL=10
def spawn_level():
    global enemies,boss
    enemies=[Enemy(level) for _ in range(LEVEL_GOAL)]
    boss=Boss(level) if level%5==0 else None

state="PLAY"
reset_game()

running=True
while running:
    clock.tick(FPS)
    screen.blit(BG,(0,0))

    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            running=False

        if state=="PLAY" and e.type==pygame.MOUSEBUTTONDOWN:
            m=pygame.Vector2(pygame.mouse.get_pos())
            d=m-player.pos
            if d.length()>0:
                bullets.append(Bullet(player.pos,d.normalize()))

        if state=="GAME_OVER" and e.type==pygame.KEYDOWN:
            if e.key==pygame.K_r:
                reset_game()
            if e.key==pygame.K_ESCAPE:
                running=False

    if state=="PLAY":
        player.update()

        for b in bullets[:]:
            b.update()
            if not screen.get_rect().collidepoint(b.pos):
                bullets.remove(b)

        for en in enemies[:]:
            en.update(player)
            if en.pos.distance_to(player.pos)<40:
                player.health-=en.damage
            for b in bullets[:]:
                if en.pos.distance_to(b.pos)<30:
                    en.health-=player.damage
                    bullets.remove(b)
                    if en.health<=0:
                        enemies.remove(en)
                        kills+=1
                        score+=10

        if boss:
            boss.update(player)
            if boss.pos.distance_to(player.pos)<60:
                player.health-=boss.damage
            for b in bullets[:]:
                if boss.pos.distance_to(b.pos)<45:
                    boss.health-=player.damage
                    bullets.remove(b)
                    if boss.health<=0:
                        boss=None
                        score+=200

        if kills>=LEVEL_GOAL and not enemies and not boss:
            level+=1
            kills=0
            player.damage+=3
            spawn_level()

        if player.health<=0:
            state="GAME_OVER"
            if score>highscore:
                save_highscore(score)
                highscore=score

    player.draw()
    for b in bullets: b.draw()
    for en in enemies: en.draw()
    if boss:
        boss.draw()
        boss.draw_bar()

    screen.blit(font.render(f"HP: {int(player.health)}",True,RED),(10,10))
    screen.blit(font.render(f"Level: {level}",True,WHITE),(10,35))
    screen.blit(font.render(f"Score: {score}",True,WHITE),(10,60))
    screen.blit(font.render(f"High: {highscore}",True,WHITE),(10,85))

    if state=="GAME_OVER":
        t=big.render("GAME OVER",True,RED)
        screen.blit(t,(WIDTH//2-t.get_width()//2,220))
        screen.blit(font.render("Press R to Restart",True,WHITE),(380,290))
        screen.blit(font.render("Press ESC to Quit",True,WHITE),(380,320))

    pygame.display.update()

pygame.quit()
sys.exit()
