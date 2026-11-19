import pygame

def crear_sprite_hunter():
    surf = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (175, 30, 45), [(10, 20), (38, 20), (44, 46), (4, 46)])
    pygame.draw.rect(surf, (45, 50, 65), (14, 20, 20, 24), border_radius=4)
    pygame.draw.rect(surf, (235, 195, 60), (14, 31, 20, 4))
    pygame.draw.rect(surf, (240, 200, 170), (16, 10, 16, 12), border_radius=3)
    pygame.draw.rect(surf, (30, 30, 40), (19, 14, 3, 3))
    pygame.draw.rect(surf, (30, 30, 40), (26, 14, 3, 3))
    pygame.draw.rect(surf, (30, 25, 35), (6, 8, 36, 4), border_radius=2)
    pygame.draw.rect(surf, (38, 32, 44), (13, 1, 22, 8), border_radius=2)
    pygame.draw.rect(surf, (195, 40, 50), (13, 6, 22, 2))
    return surf

def crear_sprite_vampiro(tipo="normal"):
    surf = pygame.Surface((46, 46), pygame.SRCALPHA)
    if tipo == "elite":
        capa_ext, capa_int, ojos = (130, 20, 45), (220, 160, 40), (255, 220, 50)
    elif tipo == "acechador":
        capa_ext, capa_int, ojos = (25, 70, 85), (45, 150, 170), (90, 255, 240)
    elif tipo == "mago":
        capa_ext, capa_int, ojos = (70, 25, 115), (150, 55, 210), (255, 110, 220)
    elif tipo == "errante":
        capa_ext, capa_int, ojos = (70, 78, 95), (125, 135, 155), (245, 215, 75)
    else:
        capa_ext, capa_int, ojos = (55, 20, 75), (130, 20, 40), (255, 40, 40)

    pygame.draw.polygon(surf, capa_ext, [(6, 12), (40, 12), (44, 44), (2, 44)])
    pygame.draw.polygon(surf, capa_int, [(10, 10), (36, 10), (38, 24), (8, 24)])
    pygame.draw.rect(surf, (25, 25, 32), (14, 18, 18, 22), border_radius=3)
    pygame.draw.rect(surf, (215, 220, 230), (15, 8, 16, 13), border_radius=3)
    pygame.draw.polygon(surf, (20, 20, 25), [(15, 8), (31, 8), (23, 13)])
    pygame.draw.rect(surf, ojos, (18, 13, 3, 3))
    pygame.draw.rect(surf, ojos, (25, 13, 3, 3))
    pygame.draw.rect(surf, (255, 255, 255), (19, 18, 2, 3))
    pygame.draw.rect(surf, (255, 255, 255), (25, 18, 2, 3))
    return surf

def crear_sprite_jefe():
    surf = pygame.Surface((84, 84), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (115, 12, 32), [(10, 22), (74, 22), (80, 80), (4, 80)])
    pygame.draw.polygon(surf, (225, 165, 35), [(18, 18), (66, 18), (70, 42), (14, 42)])
    pygame.draw.rect(surf, (28, 22, 36), (24, 30, 36, 44), border_radius=6)
    pygame.draw.rect(surf, (225, 220, 235), (26, 12, 32, 22), border_radius=5)
    pygame.draw.polygon(surf, (245, 195, 50), [(24, 13), (30, 3), (42, 11), (54, 3), (60, 13)])
    pygame.draw.rect(surf, (255, 35, 55), (32, 20, 5, 5))
    pygame.draw.rect(surf, (255, 35, 55), (47, 20, 5, 5))
    pygame.draw.rect(surf, (255, 255, 255), (35, 30, 3, 5))
    pygame.draw.rect(surf, (255, 255, 255), (46, 30, 3, 5))
    return surf

def crear_sprite_goblin():
    surf = pygame.Surface((52, 52), pygame.SRCALPHA)
    pygame.draw.circle(surf, (195, 145, 45), (14, 30), 12)
    pygame.draw.circle(surf, (245, 200, 70), (14, 30), 12, width=2)
    pygame.draw.rect(surf, (65, 115, 55), (18, 22, 22, 24), border_radius=5)
    pygame.draw.rect(surf, (235, 185, 55), (18, 32, 22, 4))
    pygame.draw.polygon(surf, (85, 175, 75), [(12, 13), (20, 10), (20, 18)])
    pygame.draw.polygon(surf, (85, 175, 75), [(46, 13), (38, 10), (38, 18)])
    pygame.draw.rect(surf, (95, 190, 80), (20, 8, 18, 15), border_radius=4)
    pygame.draw.polygon(surf, (150, 45, 90), [(18, 9), (40, 9), (29, 1)])
    pygame.draw.rect(surf, (255, 230, 60), (23, 13, 3, 3))
    pygame.draw.rect(surf, (255, 230, 60), (31, 13, 3, 3))
    return surf

def crear_sprite_cofre():
    surf = pygame.Surface((44, 38), pygame.SRCALPHA)
    pygame.draw.rect(surf, (135, 80, 35), (2, 6, 40, 30), border_radius=5)
    pygame.draw.rect(surf, (165, 100, 45), (2, 4, 40, 13), border_radius=4)
    pygame.draw.rect(surf, (245, 200, 65), (2, 4, 40, 32), width=3, border_radius=5)
    pygame.draw.line(surf, (245, 200, 65), (2, 17), (42, 17), 3)
    pygame.draw.rect(surf, (255, 235, 110), (18, 13, 8, 9), border_radius=2)
    return surf

def crear_sprite_altar():
    surf = pygame.Surface((54, 54), pygame.SRCALPHA)
    pygame.draw.rect(surf, (55, 58, 72), (6, 36, 42, 14), border_radius=4)
    pygame.draw.rect(surf, (75, 78, 94), (12, 18, 30, 20), border_radius=3)
    pygame.draw.polygon(surf, (210, 35, 65), [(27, 4), (36, 14), (27, 24), (18, 14)])
    pygame.draw.circle(surf, (255, 190, 90), (27, 14), 4)
    return surf

def crear_sprite_corazon():
    surf = pygame.Surface((24, 22), pygame.SRCALPHA)
    pygame.draw.circle(surf, (225, 25, 55), (7, 7), 6)
    pygame.draw.circle(surf, (225, 25, 55), (17, 7), 6)
    pygame.draw.polygon(surf, (225, 25, 55), [(1, 9), (23, 9), (12, 21)])
    pygame.draw.circle(surf, (255, 160, 175), (6, 5), 2)
    return surf

def crear_sprite_flecha(tipo="normal"):
    surf = pygame.Surface((36, 14), pygame.SRCALPHA)
    if tipo == "homing":
        pluma, astil, punta = (195, 70, 255), (235, 175, 255), (255, 125, 255)
    elif tipo == "rebote":
        pluma, astil, punta = (50, 220, 130), (170, 245, 200), (120, 255, 180)
    else:
        pluma, astil, punta = (225, 65, 65), (215, 170, 110), (225, 240, 255)

    pygame.draw.polygon(surf, pluma, [(0, 2), (8, 7), (0, 12), (4, 7)])
    pygame.draw.line(surf, astil, (4, 7), (26, 7), 3)
    pygame.draw.polygon(surf, punta, [(24, 2), (36, 7), (24, 12)])
    return surf

def crear_sprite_carcaj():
    surf = pygame.Surface((34, 34), pygame.SRCALPHA)
    pygame.draw.rect(surf, (130, 75, 35), (10, 10, 14, 22), border_radius=4)
    pygame.draw.rect(surf, (240, 195, 60), (10, 14, 14, 3))
    for ox in (-4, 0, 4):
        pygame.draw.line(surf, (220, 180, 120), (17 + ox, 10), (17 + ox * 2, 2), 2)
        pygame.draw.circle(surf, (235, 65, 65), (17 + ox * 2, 2), 2)
    return surf

class BancoSprites:
    def __init__(self):
        self.hunter = crear_sprite_hunter()
        self.vampiro = crear_sprite_vampiro("normal")
        self.vampiro_elite = crear_sprite_vampiro("elite")
        self.vampiro_acechador = crear_sprite_vampiro("acechador")
        self.vampiro_mago = crear_sprite_vampiro("mago")
        self.vampiro_errante = crear_sprite_vampiro("errante")
        self.jefe = crear_sprite_jefe()
        self.goblin = crear_sprite_goblin()
        self.cofre = crear_sprite_cofre()
        self.altar = crear_sprite_altar()
        self.corazon = crear_sprite_corazon()
        self.flecha_normal = crear_sprite_flecha("normal")
        self.flecha_homing = crear_sprite_flecha("homing")
        self.flecha_rebote = crear_sprite_flecha("rebote")
        self.carcaj = crear_sprite_carcaj()