import pygame
import random
import math
import json
import os

# 1. Configuración inicial 1080p Pantalla Completa
pygame.init()
ANCHO, ALTO = 1920, 1080
pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Vampire Hunter - Infinite Roguelike")
reloj = pygame.time.Clock()

fuente_titulo = pygame.font.SysFont("monospace", 66, bold=True)
fuente_sub = pygame.font.SysFont("monospace", 24, bold=True)
fuente_boton = pygame.font.SysFont("monospace", 26, bold=True)
fuente_hud = pygame.font.SysFont("monospace", 21, bold=True)
fuente_nodo = pygame.font.SysFont("monospace", 15, bold=True)
fuente_aviso = pygame.font.SysFont("monospace", 25, bold=True)

ARCHIVO_SCORES = "scores.json"
ARCHIVO_PROGRESO = "progreso.json"

VEL_MAX_JUGADOR = 7.4
MAX_FLECHAS = 10
TAM_BALDOSA = 96
TAM_CHUNK = 768  # 8x8 baldosas por chunk del mundo infinito

# 2. Generador de Sprites Pixel-Art
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
    # Estructura permanente generada en el mundo infinito
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

SPRITE_HUNTER = crear_sprite_hunter()
SPRITE_VAMPIRO = crear_sprite_vampiro("normal")
SPRITE_VAMPIRO_ELITE = crear_sprite_vampiro("elite")
SPRITE_VAMPIRO_ACECHADOR = crear_sprite_vampiro("acechador")
SPRITE_GOBLIN = crear_sprite_goblin()
SPRITE_COFRE = crear_sprite_cofre()
SPRITE_ALTAR = crear_sprite_altar()
SPRITE_CORAZON = crear_sprite_corazon()
SPRITE_FLECHA_NORMAL = crear_sprite_flecha("normal")
SPRITE_FLECHA_HOMING = crear_sprite_flecha("homing")
SPRITE_FLECHA_REBOTE = crear_sprite_flecha("rebote")
SPRITE_CARCAJ = crear_sprite_carcaj()

# 3. Generador de Mundo Infinito (Chunks deterministas + Biomas + Altares)
def generar_datos_chunk(cx, cy, semilla_mundo):
    rng = random.Random(hash((semilla_mundo, cx, cy)))
    dist_origen = math.hypot(cx, cy)

    # Bioma según distancia al origen
    if dist_origen < 3:
        bioma = "patio"      # Piedra gris azulada
    elif dist_origen < 7:
        bioma = "bosque"     # Tierra oscura y musgo
    else:
        bioma = "abismo"     # Piedra volcánica carmesí

    decoraciones = []
    for _ in range(rng.randint(3, 7)):
        dx = cx * TAM_CHUNK + rng.randint(40, TAM_CHUNK - 40)
        dy = cy * TAM_CHUNK + rng.randint(40, TAM_CHUNK - 40)
        tipo_dec = rng.choice(["grieta", "musgo", "runa"])
        decoraciones.append((dx, dy, tipo_dec, rng.randint(4, 12)))

    # Altares permanentes en ciertos chunks (no en el chunk inicial 0,0)
    altar = None
    if (cx != 0 or cy != 0) and rng.random() < 0.24:
        ax = cx * TAM_CHUNK + rng.randint(150, TAM_CHUNK - 150)
        ay = cy * TAM_CHUNK + rng.randint(150, TAM_CHUNK - 150)
        altar = {"x": ax, "y": ay, "usado": False}

    # Cofres naturales explorables en el mundo
    cofre = None
    if (cx != 0 or cy != 0) and rng.random() < 0.30:
        kx = cx * TAM_CHUNK + rng.randint(120, TAM_CHUNK - 120)
        ky = cy * TAM_CHUNK + rng.randint(120, TAM_CHUNK - 120)
        cofre = {"x": kx, "y": ky}

    return {"bioma": bioma, "decoraciones": decoraciones, "altar": altar, "cofre": cofre}

def dibujar_mundo_infinito(superficie, partida):
    cam_x = partida["wx"] - ANCHO // 2
    cam_y = partida["wy"] - ALTO // 2

    # Calcular baldosas visibles en pantalla
    col_ini = int(math.floor(cam_x / TAM_BALDOSA)) - 1
    col_fin = int(math.ceil((cam_x + ANCHO) / TAM_BALDOSA)) + 1
    fila_ini = int(math.floor(cam_y / TAM_BALDOSA)) - 1
    fila_fin = int(math.ceil((cam_y + ALTO) / TAM_BALDOSA)) + 1

    for col in range(col_ini, col_fin):
        for fila in range(fila_ini, fila_fin):
            wx = col * TAM_BALDOSA
            wy = fila * TAM_BALDOSA
            sx = int(wx - cam_x)
            sy = int(wy - cam_y)

            cx = math.floor(wx / TAM_CHUNK)
            cy = math.floor(wy / TAM_CHUNK)
            chunk = obtener_chunk(partida, cx, cy)

            # Tono determinista por baldosa
            h = ((col * 73856093) ^ (fila * 19349663)) & 7
            if chunk["bioma"] == "patio":
                base = (22 + h, 25 + h, 34 + h)
            elif chunk["bioma"] == "bosque":
                base = (20 + h, 30 + h, 25 + h)
            else:
                base = (32 + h, 20 + h, 26 + h)

            pygame.draw.rect(superficie, base, (sx + 1, sy + 1, TAM_BALDOSA - 2, TAM_BALDOSA - 2), border_radius=5)

    # Dibujar decoraciones y estructuras de los chunks visibles
    c_x_ini = math.floor(cam_x / TAM_CHUNK)
    c_x_fin = math.floor((cam_x + ANCHO) / TAM_CHUNK)
    c_y_ini = math.floor(cam_y / TAM_CHUNK)
    c_y_fin = math.floor((cam_y + ALTO) / TAM_CHUNK)

    for cx in range(c_x_ini, c_x_fin + 1):
        for cy in range(c_y_ini, c_y_fin + 1):
            chunk = obtener_chunk(partida, cx, cy)
            for dx, dy, tipo_dec, radio in chunk["decoraciones"]:
                sx, sy = int(dx - cam_x), int(dy - cam_y)
                if tipo_dec == "grieta":
                    pygame.draw.line(superficie, (12, 14, 19), (sx, sy), (sx + radio * 2, sy + radio), 2)
                elif tipo_dec == "musgo":
                    pygame.draw.circle(superficie, (28, 48, 36), (sx, sy), radio)
                else:
                    pygame.draw.circle(superficie, (65, 35, 55), (sx, sy), radio, width=1)

            if chunk["altar"] is not None:
                alt = chunk["altar"]
                sx, sy = int(alt["x"] - cam_x), int(alt["y"] - cam_y)
                if not alt["usado"]:
                    halo = pygame.Surface((96, 96), pygame.SRCALPHA)
                    pygame.draw.circle(halo, (220, 40, 75, 42), (48, 48), 44)
                    superficie.blit(halo, (sx - 48, sy - 48))
                superficie.blit(SPRITE_ALTAR, (sx - 27, sy - 27))

def obtener_chunk(partida, cx, cy):
    clave = (cx, cy)
    if clave not in partida["chunks"]:
        chunk = generar_datos_chunk(cx, cy, partida["semilla"])
        partida["chunks"][clave] = chunk
        if chunk["cofre"] is not None:
            partida["cofres"].append({"x": float(chunk["cofre"]["x"]), "y": float(chunk["cofre"]["y"])})
    return partida["chunks"][clave]

# 4. Red de Sangre Rebalanceada (progresión medida y justa)
def generar_red_sangre(nivel_red, prestigio):
    cx, cy = ANCHO // 2, 515
    rng = random.Random(1000 + nivel_red * 37 + prestigio * 911)
    costo_1 = 10 + (nivel_red - 1) * 6
    costo_2 = 22 + (nivel_red - 1) * 10
    costo_3 = 40 + (nivel_red - 1) * 16

    nodos = [
        {"id": 0, "x": cx, "y": cy, "tipo": "centro", "nombre": f"RED {nivel_red}", "valor": 0, "costo": 0, "comprado": True, "padres": []}
    ]

    tipos_1 = [
        ("dano", "+2 ATK", 2),
        ("vida", "+6 HP", 6),
        ("iman", "+8 RANGO", 8),
        ("cadencia", "+2% CAD", 2),
    ]
    for i in range(4):
        ang = math.radians(45 + i * 90)
        nx = int(cx + math.cos(ang) * 145)
        ny = int(cy + math.sin(ang) * 130)
        tipo, nombre, val = tipos_1[i % len(tipos_1)]
        nodos.append({
            "id": i + 1, "x": nx, "y": ny, "tipo": tipo, "nombre": nombre,
            "valor": val, "costo": costo_1, "comprado": False, "padres": [0]
        })

    tipos_2 = [
        ("dano", "+3 ATK", 3),
        ("vida", "+10 HP", 10),
        ("iman", "+10 RANGO", 10),
        ("vel", "+0.1 VEL", 0.1),
        ("cadencia", "+3% CAD", 3),
    ]
    for i in range(6):
        ang = math.radians(i * 60)
        nx = int(cx + math.cos(ang) * 285)
        ny = int(cy + math.sin(ang) * 235)
        tipo, nombre, val = rng.choice(tipos_2)
        nodos.append({
            "id": i + 5, "x": nx, "y": ny, "tipo": tipo, "nombre": nombre,
            "valor": val, "costo": costo_2, "comprado": False, "padres": [1 + (i % 4)]
        })

    # Solo 1 nodo de +1 Flecha cada 2 niveles de Red para no romper el juego
    nodo_especial = ("flecha", "+1 FLECHA", 1) if (nivel_red % 2 == 0 and progreso.get("bonus_flechas", 0) < 2) else ("dano", "+5 ATK", 5)
    tipos_3 = [
        nodo_especial,
        ("dano", "+5 ATK", 5),
        ("vida", "+16 HP", 16),
    ]
    for i in range(3):
        ang = math.radians(30 + i * 120)
        nx = int(cx + math.cos(ang) * 435)
        ny = int(cy + math.sin(ang) * 320)
        tipo, nombre, val = tipos_3[i]
        nodos.append({
            "id": i + 11, "x": nx, "y": ny, "tipo": tipo, "nombre": nombre,
            "valor": val, "costo": costo_3, "comprado": False, "padres": [5 + (i * 2)]
        })

    return nodos

def cargar_scores():
    if not os.path.exists(ARCHIVO_SCORES):
        return []
    try:
        with open(ARCHIVO_SCORES, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

def guardar_score(puntos, nivel_alcanzado, prestigio):
    scores = cargar_scores()
    scores.append({"puntos": puntos, "nivel": nivel_alcanzado, "prestigio": prestigio})
    scores = sorted(scores, key=lambda s: s["puntos"], reverse=True)[:5]
    with open(ARCHIVO_SCORES, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)

def cargar_progreso():
    default = {
        "corazones": 0,
        "prestigio": 0,
        "nivel_red": 1,
        "bonus_flechas": 0,
        "bonus_dano": 0,
        "bonus_vida": 0,
        "bonus_iman": 0,
        "bonus_cadencia": 0,
        "bonus_vel": 0.0,
        "nodos": [],
    }
    if not os.path.exists(ARCHIVO_PROGRESO):
        default["nodos"] = generar_red_sangre(1, 0)
        return default
    try:
        with open(ARCHIVO_PROGRESO, "r", encoding="utf-8") as f:
            data = json.load(f)
            default.update(data)
            if not default["nodos"]:
                default["nodos"] = generar_red_sangre(default["nivel_red"], default["prestigio"])
            return default
    except (json.JSONDecodeError, OSError):
        default["nodos"] = generar_red_sangre(1, 0)
        return default

progreso = {}
progreso = cargar_progreso()

def guardar_progreso(prog):
    with open(ARCHIVO_PROGRESO, "w", encoding="utf-8") as f:
        json.dump(prog, f, indent=2)

def nodo_desbloqueable(nodo, todos_nodos):
    if nodo["comprado"]:
        return False
    mapa = {n["id"]: n for n in todos_nodos}
    return any(mapa[pid]["comprado"] for pid in nodo["padres"] if pid in mapa)

def aplicar_nodo_comprado(nodo):
    t = nodo["tipo"]
    v = nodo["valor"]
    if t == "flecha":
        progreso["bonus_flechas"] = min(2, progreso["bonus_flechas"] + int(v))
    elif t == "dano":
        progreso["bonus_dano"] += int(v)
    elif t == "vida":
        progreso["bonus_vida"] += int(v)
    elif t == "iman":
        progreso["bonus_iman"] += int(v)
    elif t == "cadencia":
        progreso["bonus_cadencia"] = min(30, progreso["bonus_cadencia"] + int(v))
    elif t == "vel":
        progreso["bonus_vel"] = round(min(1.0, progreso["bonus_vel"] + float(v)), 2)

    if all(n["comprado"] for n in progreso["nodos"]):
        progreso["nivel_red"] += 1
        progreso["nodos"] = generar_red_sangre(progreso["nivel_red"], progreso["prestigio"])

def ejecutar_prestigio():
    progreso["prestigio"] += 1
    progreso["nivel_red"] = 1
    progreso["bonus_flechas"] = 0
    progreso["bonus_dano"] = 0
    progreso["bonus_vida"] = 0
    progreso["bonus_iman"] = 0
    progreso["bonus_cadencia"] = 0
    progreso["bonus_vel"] = 0.0
    progreso["nodos"] = generar_red_sangre(1, progreso["prestigio"])
    guardar_progreso(progreso)

# 5. Botones UI
def dibujar_boton(superficie, texto, rect, pos_mouse, color_base=(42, 48, 64), color_hover=(185, 45, 60), activo=True):
    if not activo:
        color, borde, txt_color = (28, 31, 40), (80, 85, 95), (115, 120, 130)
    else:
        hover = rect.collidepoint(pos_mouse)
        color = color_hover if hover else color_base
        borde, txt_color = (230, 235, 245), (255, 255, 255)

    pygame.draw.rect(superficie, color, rect, border_radius=12)
    pygame.draw.rect(superficie, borde, rect, width=2, border_radius=12)
    render = fuente_boton.render(texto, True, txt_color)
    superficie.blit(render, render.get_rect(center=rect.center))
    return activo and rect.collidepoint(pos_mouse)

# 6. Estado inicial de partida (Mundo Infinito + Balance Roguelike)
def iniciar_partida():
    mult_prestigio = 1.0 + (progreso["prestigio"] * 0.05)  # +5% equilibrado por prestigio
    hp_inicial = 100 + progreso["bonus_vida"]
    dano_inicial = int((20 + progreso["bonus_dano"]) * mult_prestigio)
    cd_inicial = max(24, int(52 * (1.0 - progreso["bonus_cadencia"] / 100.0)))
    vel_inicial = min(VEL_MAX_JUGADOR, round(4.8 + progreso["bonus_vel"], 2))

    p = {
        "semilla": random.randint(1, 999999),
        "chunks": {},
        "wx": 0.0,                  # Posición del cazador en el mundo infinito
        "wy": 0.0,
        "mirando_izq": False,
        "vel_jugador": vel_inicial,
        "hp_max": hp_inicial,
        "hp": float(hp_inicial),
        "xp": 0,
        "xp_siguiente": 7,
        "nivel": 1,
        "puntos": 0,
        "corazones_run": 0,
        "rango_base": 70 + progreso["bonus_iman"],
        "cantidad_flechas": min(MAX_FLECHAS, 1 + progreso["bonus_flechas"]),
        "flechas_homing": 0,
        "flecha_rebote": False,
        "cooldown_flecha": cd_inicial,
        "timer_flecha": 0,
        "dano_flecha": dano_inicial,
        "vel_flecha": 12.5,
        "enemigos": [],             # Coordenadas absolutas del mundo (x, y)
        "flechas": [],              # Coordenadas absolutas del mundo (x, y)
        "gemas_xp": [],             # Permanecen en el mundo para siempre
        "corazones_suelo": [],      # Permanecen en el mundo para siempre
        "carcajes_suelo": [],       # Permanecen en el mundo para siempre
        "cofres": [],               # Permanecen en el mundo para siempre
        "goblin": None,
        "frames_jugados": 0,
        "frames_quieto": 0,         # Contador anti-AFK
        "timer_spawn": 0,
        "mensaje_aviso": "",
        "timer_aviso": 0,
    }
    # Precargar chunks alrededor del origen
    for cx in (-1, 0, 1):
        for cy in (-1, 0, 1):
            obtener_chunk(p, cx, cy)
    return p

def obtener_rango_recogida(partida):
    return partida["rango_base"] + (partida["nivel"] - 1) * 9

def mostrar_aviso(partida, texto):
    partida["mensaje_aviso"] = texto
    partida["timer_aviso"] = 160

def generar_enemigo(partida):
    # Aparecen fuera del borde de la cámara actual del jugador
    ang = random.uniform(0, 2 * math.pi)
    dist_spawn = random.uniform(1120, 1280)
    wx = partida["wx"] + math.cos(ang) * dist_spawn
    wy = partida["wy"] + math.sin(ang) * dist_spawn

    mins = (partida["frames_jugados"] // 60) // 60
    dist_mundo = math.hypot(partida["wx"], partida["wy"]) / 2000.0
    escala_dificultad = 1.0 + (mins * 0.45) + (dist_mundo * 0.25)

    roll = random.random()
    if partida["nivel"] >= 2 and roll < min(0.32, 0.08 + partida["nivel"] * 0.02):
        tipo = "elite"
        hp = int((160 + partida["nivel"] * 38) * escala_dificultad)
        vel = min(4.6, 2.2 + partida["nivel"] * 0.05)
    elif (mins >= 1 or partida["nivel"] >= 3) and roll < 0.55:
        tipo = "acechador"  # Rápido y agresivo para evitar que te quedes quieto
        hp = int((50 + partida["nivel"] * 14) * escala_dificultad)
        vel = min(5.8, 3.3 + partida["nivel"] * 0.07)
    else:
        tipo = "normal"
        hp = int((65 + partida["nivel"] * 20) * escala_dificultad)
        vel = min(4.9, 2.45 + partida["nivel"] * 0.06)

    partida["enemigos"].append({
        "x": wx,
        "y": wy,
        "hp": hp,
        "vel": vel,
        "tipo": tipo,
        "mirando_izq": False
    })

def aplicar_mejora_cofre(partida):
    # Mejoras sutiles y progresivas (nada roto de golpe)
    mejoras = [
        ("DAÑO DE FLECHA +3", "dano"),
        ("CADENCIA DE TIRO +5%", "cadencia"),
        ("VIDA MAX +10 Y CURACION", "vida"),
        ("RANGO DE RECOGIDA +10px", "iman"),
    ]
    if partida["vel_jugador"] < VEL_MAX_JUGADOR:
        mejoras.append(("VELOCIDAD +4%", "vel"))
    if partida["cantidad_flechas"] < MAX_FLECHAS and random.random() < 0.28:
        mejoras.append(("¡MULTIDISPARO! +1 FLECHA", "flecha"))

    nombre, tipo = random.choice(mejoras)
    if tipo == "flecha":
        partida["cantidad_flechas"] = min(MAX_FLECHAS, partida["cantidad_flechas"] + 1)
    elif tipo == "dano":
        partida["dano_flecha"] += 3
    elif tipo == "cadencia":
        partida["cooldown_flecha"] = max(14, int(partida["cooldown_flecha"] * 0.95))
    elif tipo == "vel":
        partida["vel_jugador"] = min(VEL_MAX_JUGADOR, round(partida["vel_jugador"] * 1.04, 2))
    elif tipo == "vida":
        partida["hp_max"] += 10
        partida["hp"] = min(float(partida["hp_max"]), partida["hp"] + 25)
    elif tipo == "iman":
        partida["rango_base"] += 10

    mostrar_aviso(partida, f"COFRE: {nombre}")

def activar_altar_mundo(partida):
    mejoras_altar = [
        ("BENDICION DE SANGRE: +4 ATK PERMANENTE EN RUN", "dano"),
        ("VITALIDAD ANTIGUA: +15 HP MAX", "vida"),
        ("PULSO ARCANO: +6% CADENCIA", "cadencia"),
    ]
    if partida["cantidad_flechas"] < MAX_FLECHAS and random.random() < 0.35:
        mejoras_altar.append(("RELIQUIA DE CAZA: +1 FLECHA", "flecha"))

    nombre, tipo = random.choice(mejoras_altar)
    if tipo == "dano":
        partida["dano_flecha"] += 4
    elif tipo == "vida":
        partida["hp_max"] += 15
        partida["hp"] = min(float(partida["hp_max"]), partida["hp"] + 30)
    elif tipo == "cadencia":
        partida["cooldown_flecha"] = max(14, int(partida["cooldown_flecha"] * 0.94))
    elif tipo == "flecha":
        partida["cantidad_flechas"] = min(MAX_FLECHAS, partida["cantidad_flechas"] + 1)

    mostrar_aviso(partida, f"¡ALTAR ACTIVADO! {nombre}")

def invocar_goblin(partida):
    ang = random.uniform(0, 2 * math.pi)
    gx = partida["wx"] + math.cos(ang) * 420
    gy = partida["wy"] + math.sin(ang) * 420
    partida["goblin"] = {
        "x": gx,
        "y": gy,
        "tiempo_restante": 30 * 60
    }
    mostrar_aviso(partida, "¡GOBLIN MERCADER CERCA! SIGUE LA FLECHA DORADA")

def dibujar_indicador_borde(superficie, origen_wx, origen_wy, destino_wx, destino_wy, color, etiqueta):
    dx = destino_wx - origen_wx
    dy = destino_wy - origen_wy
    sx = ANCHO // 2 + dx
    sy = ALTO // 2 + dy
    # Solo dibujar brújula si el objetivo está fuera de la pantalla visible
    if 30 <= sx <= ANCHO - 30 and 30 <= sy <= ALTO - 30:
        return
    ang = math.atan2(dy, dx)
    bx = ANCHO // 2 + math.cos(ang) * (ANCHO // 2 - 55)
    by = ALTO // 2 + math.sin(ang) * (ALTO // 2 - 55)
    pygame.draw.circle(superficie, color, (int(bx), int(by)), 12)
    pygame.draw.circle(superficie, (255, 255, 255), (int(bx), int(by)), 12, width=2)
    lbl = fuente_nodo.render(etiqueta, True, color)
    superficie.blit(lbl, lbl.get_rect(center=(int(bx), int(by) - 20)))

# Botones de navegación
btn_jugar = pygame.Rect(ANCHO // 2 - 200, 410, 400, 64)
btn_bloodweb = pygame.Rect(ANCHO // 2 - 200, 495, 400, 64)
btn_scoreboard = pygame.Rect(ANCHO // 2 - 200, 580, 400, 64)
btn_salir = pygame.Rect(ANCHO // 2 - 200, 665, 400, 64)

btn_volver_red = pygame.Rect(60, 960, 320, 62)
btn_prestigio = pygame.Rect(ANCHO - 440, 960, 380, 62)
btn_volver = pygame.Rect(ANCHO // 2 - 190, 880, 380, 66)

btn_continuar = pygame.Rect(ANCHO // 2 - 190, 420, 380, 66)
btn_reiniciar = pygame.Rect(ANCHO // 2 - 190, 505, 380, 66)
btn_pausa_menu = pygame.Rect(ANCHO // 2 - 190, 590, 380, 66)

estado = "MENU"
partida = iniciar_partida()
tick_global = 0

# 7. Bucle principal
ejecutando = True
while ejecutando:
    tick_global += 1
    pos_mouse = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        if evento.type in (pygame.WINDOWFOCUSLOST, pygame.WINDOWMINIMIZED):
            if estado == "JUGANDO":
                estado = "PAUSA"

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            if estado == "JUGANDO":
                estado = "PAUSA"
            elif estado == "PAUSA":
                estado = "JUGANDO"
            elif estado == "GOBLIN_SHOP":
                estado = "JUGANDO"
            elif estado in ("BLOODWEB", "SCOREBOARD", "GAME_OVER"):
                estado = "MENU"
            elif estado == "MENU":
                ejecutando = False

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if estado == "MENU":
                if btn_jugar.collidepoint(pos_mouse):
                    partida = iniciar_partida()
                    estado = "JUGANDO"
                elif btn_bloodweb.collidepoint(pos_mouse):
                    estado = "BLOODWEB"
                elif btn_scoreboard.collidepoint(pos_mouse):
                    estado = "SCOREBOARD"
                elif btn_salir.collidepoint(pos_mouse):
                    ejecutando = False

            elif estado == "BLOODWEB":
                for nodo in progreso["nodos"]:
                    dist_clic = math.hypot(pos_mouse[0] - nodo["x"], pos_mouse[1] - nodo["y"])
                    if dist_clic <= 44 and nodo_desbloqueable(nodo, progreso["nodos"]):
                        if progreso["corazones"] >= nodo["costo"]:
                            progreso["corazones"] -= nodo["costo"]
                            nodo["comprado"] = True
                            aplicar_nodo_comprado(nodo)
                            guardar_progreso(progreso)
                            break

                if btn_prestigio.collidepoint(pos_mouse) and progreso["nivel_red"] >= 5:
                    ejecutar_prestigio()
                elif btn_volver_red.collidepoint(pos_mouse):
                    estado = "MENU"

            elif estado == "PAUSA":
                if btn_continuar.collidepoint(pos_mouse):
                    estado = "JUGANDO"
                elif btn_reiniciar.collidepoint(pos_mouse):
                    partida = iniciar_partida()
                    estado = "JUGANDO"
                elif btn_pausa_menu.collidepoint(pos_mouse):
                    bonus_p = 1.0 + (progreso["prestigio"] * 0.05)
                    progreso["corazones"] += int(round(partida["corazones_run"] * bonus_p))
                    guardar_progreso(progreso)
                    estado = "MENU"

            elif estado == "GOBLIN_SHOP":
                costo_homing = 14 + partida["flechas_homing"] * 6
                ofertas_goblin = [
                    ("homing", costo_homing, partida["flechas_homing"] >= MAX_FLECHAS),
                    ("rebote", 20, partida["flecha_rebote"]),
                    ("flecha", 18, partida["cantidad_flechas"] >= MAX_FLECHAS),
                    ("curar", 8, partida["hp"] >= partida["hp_max"]),
                ]
                for idx, (clave, costo, agotado) in enumerate(ofertas_goblin):
                    btn_buy = pygame.Rect(ANCHO // 2 + 230, 310 + idx * 110, 230, 62)
                    if btn_buy.collidepoint(pos_mouse) and not agotado and partida["corazones_run"] >= costo:
                        partida["corazones_run"] -= costo
                        if clave == "homing":
                            partida["flechas_homing"] = min(MAX_FLECHAS, partida["flechas_homing"] + 1)
                            if partida["flechas_homing"] > partida["cantidad_flechas"]:
                                partida["cantidad_flechas"] = partida["flechas_homing"]
                            mostrar_aviso(partida, f"¡FLECHAS PERSEGUIDORAS: {partida['flechas_homing']}/{MAX_FLECHAS}!")
                        elif clave == "rebote":
                            partida["flecha_rebote"] = True
                            mostrar_aviso(partida, "¡FLECHA REBOTADORA ACTIVADA!")
                        elif clave == "flecha":
                            partida["cantidad_flechas"] = min(MAX_FLECHAS, partida["cantidad_flechas"] + 1)
                            mostrar_aviso(partida, f"¡FLECHAS POR RAFAGA: {partida['cantidad_flechas']}/{MAX_FLECHAS}!")
                        elif clave == "curar":
                            partida["hp"] = float(partida["hp_max"])
                            mostrar_aviso(partida, "¡VIDA RESTAURADA AL 100%!")

                btn_cerrar_goblin = pygame.Rect(ANCHO // 2 - 190, 810, 380, 66)
                if btn_cerrar_goblin.collidepoint(pos_mouse):
                    estado = "JUGANDO"

            elif estado in ("SCOREBOARD", "GAME_OVER"):
                if btn_volver.collidepoint(pos_mouse):
                    estado = "MENU"

    pantalla.fill((16, 18, 24))

    # --- MENÚ PRINCIPAL ---
    if estado == "MENU":
        titulo = fuente_titulo.render("VAMPIRE HUNTER", True, (220, 55, 70))
        subtitulo = fuente_sub.render(
            f"Infinite Roguelike  |  Prestigio P{progreso['prestigio']} (+{progreso['prestigio']*5}% Bono)  |  Red Lvl {progreso['nivel_red']}",
            True, (245, 200, 80)
        )
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 175)))
        pantalla.blit(subtitulo, subtitulo.get_rect(center=(ANCHO // 2, 240)))

        pantalla.blit(pygame.transform.scale(SPRITE_CORAZON, (34, 31)), (ANCHO // 2 - 180, 300))
        txt_cor = fuente_boton.render(f"Corazones: {progreso['corazones']}", True, (255, 110, 130))
        pantalla.blit(txt_cor, (ANCHO // 2 - 135, 298))

        dibujar_boton(pantalla, "JUGAR", btn_jugar, pos_mouse)
        dibujar_boton(pantalla, "RED DE SANGRE (MEJORAS)", btn_bloodweb, pos_mouse, color_hover=(150, 35, 75))
        dibujar_boton(pantalla, "SCOREBOARD", btn_scoreboard, pos_mouse, color_hover=(65, 130, 180))
        dibujar_boton(pantalla, "SALIR", btn_salir, pos_mouse, color_hover=(100, 40, 45))

    # --- RED DE SANGRE ---
    elif estado == "BLOODWEB":
        titulo = fuente_titulo.render(f"RED DE SANGRE - NIVEL {progreso['nivel_red']}", True, (225, 55, 80))
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 70)))

        resumen_bonos = fuente_hud.render(
            f"Prestigio: P{progreso['prestigio']} (+{progreso['prestigio']*5}% Daño/Corazones)  |  "
            f"Bonos: +{progreso['bonus_flechas']} Flechas, +{progreso['bonus_dano']} ATK, +{progreso['bonus_vida']} HP, +{progreso['bonus_iman']} Imán",
            True, (210, 215, 230)
        )
        pantalla.blit(resumen_bonos, resumen_bonos.get_rect(center=(ANCHO // 2, 125)))

        pantalla.blit(pygame.transform.scale(SPRITE_CORAZON, (30, 28)), (ANCHO // 2 - 190, 162))
        txt_saldo = fuente_boton.render(f"Corazones: {progreso['corazones']}", True, (255, 220, 100))
        pantalla.blit(txt_saldo, (ANCHO // 2 - 150, 160))

        mapa_nodos = {n["id"]: n for n in progreso["nodos"]}

        for nodo in progreso["nodos"]:
            for pid in nodo["padres"]:
                if pid in mapa_nodos:
                    padre = mapa_nodos[pid]
                    if nodo["comprado"] and padre["comprado"]:
                        color_linea, grosor = (220, 45, 65), 6
                    elif nodo_desbloqueable(nodo, progreso["nodos"]):
                        color_linea, grosor = (155, 95, 105), 4
                    else:
                        color_linea, grosor = (55, 60, 75), 3
                    pygame.draw.line(pantalla, color_linea, (padre["x"], padre["y"]), (nodo["x"], nodo["y"]), grosor)

        for nodo in progreso["nodos"]:
            pos = (nodo["x"], nodo["y"])
            desbloq = nodo_desbloqueable(nodo, progreso["nodos"])
            hover = math.hypot(pos_mouse[0] - nodo["x"], pos_mouse[1] - nodo["y"]) <= 44

            if nodo["comprado"]:
                color_fondo, color_borde = (175, 30, 50), (255, 210, 90)
            elif desbloq:
                color_fondo = (75, 45, 60) if hover else (45, 48, 64)
                color_borde = (110, 225, 140) if progreso["corazones"] >= nodo["costo"] else (220, 90, 105)
            else:
                color_fondo, color_borde = (24, 26, 34), (70, 75, 90)

            pygame.draw.circle(pantalla, color_fondo, pos, 42)
            pygame.draw.circle(pantalla, color_borde, pos, 42, width=4 if (desbloq or nodo["comprado"]) else 2)

            lbl_n = fuente_nodo.render(nodo["nombre"], True, (250, 250, 255))
            pantalla.blit(lbl_n, lbl_n.get_rect(center=(nodo["x"], nodo["y"] - 8)))

            if not nodo["comprado"]:
                lbl_c = fuente_nodo.render(f"{nodo['costo']} ♥", True, (255, 160, 175) if desbloq else (120, 125, 135))
                pantalla.blit(lbl_c, lbl_c.get_rect(center=(nodo["x"], nodo["y"] + 14)))
            else:
                lbl_ok = fuente_nodo.render("ACTIVO", True, (255, 225, 110))
                pantalla.blit(lbl_ok, lbl_ok.get_rect(center=(nodo["x"], nodo["y"] + 14)))

        dibujar_boton(pantalla, "VOLVER AL MENU", btn_volver_red, pos_mouse)

        puede_prestigio = progreso["nivel_red"] >= 5
        txt_prest = "PRESTIGIAR (REQ. RED LVL 5)" if not puede_prestigio else f"PRESTIGIAR A P{progreso['prestigio'] + 1}"
        dibujar_boton(pantalla, txt_prest, btn_prestigio, pos_mouse, color_hover=(210, 145, 30), activo=puede_prestigio)

    # --- SCOREBOARD ---
    elif estado == "SCOREBOARD":
        titulo = fuente_titulo.render("TOP 5 CAZADORES", True, (245, 200, 65))
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 160)))

        scores = cargar_scores()
        if not scores:
            vacio = fuente_boton.render("Aun no hay cacerias registradas.", True, (180, 190, 210))
            pantalla.blit(vacio, vacio.get_rect(center=(ANCHO // 2, 460)))
        else:
            for idx, s in enumerate(scores, start=1):
                p_tag = f" [P{s.get('prestigio', 0)}]" if s.get("prestigio", 0) > 0 else ""
                linea = fuente_boton.render(f"#{idx}  -  {s['puntos']} PTS  (LVL {s['nivel']}){p_tag}", True, (235, 240, 250))
                pantalla.blit(linea, linea.get_rect(center=(ANCHO // 2, 290 + idx * 75)))

        dibujar_boton(pantalla, "VOLVER AL MENU", btn_volver, pos_mouse)

    # --- JUGANDO / PAUSA / GOBLIN SHOP ---
    elif estado in ("JUGANDO", "PAUSA", "GOBLIN_SHOP"):
        rango_actual = obtener_rango_recogida(partida)
        cam_x = partida["wx"] - ANCHO // 2
        cam_y = partida["wy"] - ALTO // 2

        if estado == "JUGANDO":
            partida["frames_jugados"] += 1

            # Goblin mercader cada 2 minutos exactos
            if partida["frames_jugados"] > 0 and partida["frames_jugados"] % 7200 == 0:
                invocar_goblin(partida)

            if partida["goblin"] is not None:
                partida["goblin"]["tiempo_restante"] -= 1
                dist_g = math.hypot(partida["wx"] - partida["goblin"]["x"], partida["wy"] - partida["goblin"]["y"])
                if partida["goblin"]["tiempo_restante"] <= 0:
                    partida["goblin"] = None
                    mostrar_aviso(partida, "El Goblin mercader se ha marchado...")
                elif dist_g <= 46:
                    partida["goblin"] = None
                    estado = "GOBLIN_SHOP"

            teclas = pygame.key.get_pressed()
            dx = (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - (teclas[pygame.K_a] or teclas[pygame.K_LEFT])
            dy = (teclas[pygame.K_s] or teclas[pygame.K_DOWN]) - (teclas[pygame.K_w] or teclas[pygame.K_UP])

            # Sistema Anti-AFK: penaliza quedarse quieto más de 2.5 segundos
            if dx == 0 and dy == 0:
                partida["frames_quieto"] += 1
                if partida["frames_quieto"] > 150:
                    partida["hp"] -= 0.12 + (partida["nivel"] * 0.015)
            else:
                partida["frames_quieto"] = 0

            if dx < 0:
                partida["mirando_izq"] = True
            elif dx > 0:
                partida["mirando_izq"] = False

            if dx != 0 and dy != 0:
                dx *= 0.7071
                dy *= 0.7071

            partida["wx"] += dx * partida["vel_jugador"]
            partida["wy"] += dy * partida["vel_jugador"]

            # Generar chunks nuevos alrededor del cazador mientras explora el mundo infinito
            cx_act = math.floor(partida["wx"] / TAM_CHUNK)
            cy_act = math.floor(partida["wy"] / TAM_CHUNK)
            for ox in (-1, 0, 1):
                for oy in (-1, 0, 1):
                    chunk = obtener_chunk(partida, cx_act + ox, cy_act + oy)
                    if chunk["altar"] is not None and not chunk["altar"]["usado"]:
                        if math.hypot(partida["wx"] - chunk["altar"]["x"], partida["wy"] - chunk["altar"]["y"]) <= 48:
                            chunk["altar"]["usado"] = True
                            partida["puntos"] += 100
                            activar_altar_mundo(partida)

            # Spawn progresivo y exigente de vampiros
            partida["timer_spawn"] += 1
            intervalo_spawn = max(8, 56 - partida["nivel"] * 4)
            if partida["timer_spawn"] >= intervalo_spawn:
                generar_enemigo(partida)
                # En niveles altos o lejos del origen aparecen en parejas
                if partida["nivel"] >= 6 and random.random() < 0.35:
                    generar_enemigo(partida)
                partida["timer_spawn"] = 0

            # Disparo automático en abanico
            partida["timer_flecha"] += 1
            if partida["timer_flecha"] >= partida["cooldown_flecha"] and partida["enemigos"]:
                objetivo = min(
                    partida["enemigos"],
                    key=lambda e: math.hypot(e["x"] - partida["wx"], e["y"] - partida["wy"])
                )
                ang_central = math.atan2(objetivo["y"] - partida["wy"], objetivo["x"] - partida["wx"])
                n_flechas = partida["cantidad_flechas"]
                n_homing = min(n_flechas, partida["flechas_homing"])
                separacion = math.radians(9)

                for i in range(n_flechas):
                    offset = (i - (n_flechas - 1) / 2) * separacion
                    ang = ang_central + offset

                    if i < n_homing:
                        tipo_f = "homing"
                    elif i == n_homing and partida["flecha_rebote"]:
                        tipo_f = "rebote"
                    else:
                        tipo_f = "normal"

                    partida["flechas"].append({
                        "x": partida["wx"],
                        "y": partida["wy"],
                        "vx": math.cos(ang) * partida["vel_flecha"],
                        "vy": math.sin(ang) * partida["vel_flecha"],
                        "tipo": tipo_f,
                        "rebotes": 3 if tipo_f == "rebote" else 0,
                        "golpeados": set(),
                        "vida_frames": 120,
                    })
                partida["timer_flecha"] = 0

            # Actualizar flechas en coordenadas del mundo
            for f in partida["flechas"][:]:
                f["vida_frames"] -= 1
                if f["vida_frames"] <= 0:
                    partida["flechas"].remove(f)
                    continue

                if f["tipo"] == "homing" and partida["enemigos"]:
                    blanco = min(
                        partida["enemigos"],
                        key=lambda e: math.hypot(e["x"] - f["x"], e["y"] - f["y"])
                    )
                    ang_obj = math.atan2(blanco["y"] - f["y"], blanco["x"] - f["x"])
                    ang_act = math.atan2(f["vy"], f["vx"])
                    diff = (ang_obj - ang_act + math.pi) % (2 * math.pi) - math.pi
                    ang_nuevo = ang_act + max(-0.14, min(0.14, diff))
                    f["vx"] = math.cos(ang_nuevo) * partida["vel_flecha"]
                    f["vy"] = math.sin(ang_nuevo) * partida["vel_flecha"]

                f["x"] += f["vx"]
                f["y"] += f["vy"]

                for e in partida["enemigos"][:]:
                    if id(e) in f["golpeados"]:
                        continue
                    if math.hypot(e["x"] - f["x"], e["y"] - f["y"]) <= 30:
                        e["hp"] -= partida["dano_flecha"]
                        f["golpeados"].add(id(e))

                        if e["hp"] <= 0:
                            ex, ey = e["x"], e["y"]
                            # Todos los drops quedan guardados en el mundo infinito para siempre
                            partida["gemas_xp"].append({"x": ex, "y": ey})

                            if e["tipo"] == "elite" or random.random() < 0.32:
                                partida["corazones_suelo"].append({"x": ex + 10, "y": ey - 8})

                            if (
                                e["tipo"] == "elite"
                                and partida["cantidad_flechas"] < MAX_FLECHAS
                                and (partida["cantidad_flechas"] + len(partida["carcajes_suelo"])) < MAX_FLECHAS
                                and random.random() < 0.16
                            ):
                                partida["carcajes_suelo"].append({"x": ex, "y": ey})

                            partida["enemigos"].remove(e)
                            partida["puntos"] += (45 if e["tipo"] == "elite" else 15) * partida["nivel"]

                        if f["tipo"] == "rebote" and f["rebotes"] > 0:
                            f["rebotes"] -= 1
                            candidatos = [
                                otro for otro in partida["enemigos"]
                                if id(otro) not in f["golpeados"]
                                and math.hypot(otro["x"] - f["x"], otro["y"] - f["y"]) < 360
                            ]
                            if candidatos:
                                sig = min(candidatos, key=lambda o: math.hypot(o["x"] - f["x"], o["y"] - f["y"]))
                                ang_reb = math.atan2(sig["y"] - f["y"], sig["x"] - f["x"])
                                f["vx"] = math.cos(ang_reb) * partida["vel_flecha"]
                                f["vy"] = math.sin(ang_reb) * partida["vel_flecha"]
                            else:
                                if f in partida["flechas"]:
                                    partida["flechas"].remove(f)
                        else:
                            if f in partida["flechas"]:
                                partida["flechas"].remove(f)
                        break

            # Mover vampiros hacia el cazador (frenesí extra si el jugador está AFK)
            frenesi = 1.35 if partida["frames_quieto"] > 120 else 1.0
            dano_contacto = 0.55 + (partida["nivel"] * 0.04)
            for e in partida["enemigos"]:
                dist_e = math.hypot(partida["wx"] - e["x"], partida["wy"] - e["y"])
                # Si un enemigo queda demasiado lejos atrás al explorar, reposicionarlo adelante
                if dist_e > 1650:
                    ang_re = random.uniform(0, 2 * math.pi)
                    e["x"] = partida["wx"] + math.cos(ang_re) * 1150
                    e["y"] = partida["wy"] + math.sin(ang_re) * 1150
                    continue

                ang = math.atan2(partida["wy"] - e["y"], partida["wx"] - e["x"])
                vx = math.cos(ang) * e["vel"] * frenesi
                e["mirando_izq"] = vx < 0
                e["x"] += vx
                e["y"] += math.sin(ang) * e["vel"] * frenesi
                if dist_e <= 36:
                    mult_tipo = 1.5 if e["tipo"] == "elite" else (1.2 if e["tipo"] == "acechador" else 1.0)
                    partida["hp"] -= dano_contacto * mult_tipo

            # Recoger cofres en el mundo infinito
            for c in partida["cofres"][:]:
                if math.hypot(partida["wx"] - c["x"], partida["wy"] - c["y"]) <= 44:
                    partida["cofres"].remove(c)
                    partida["puntos"] += 50
                    aplicar_mejora_cofre(partida)

            # Recoger carcajes en el mundo infinito
            for k in partida["carcajes_suelo"][:]:
                if math.hypot(partida["wx"] - k["x"], partida["wy"] - k["y"]) <= 44:
                    partida["carcajes_suelo"].remove(k)
                    if partida["cantidad_flechas"] < MAX_FLECHAS:
                        partida["cantidad_flechas"] += 1
                        mostrar_aviso(partida, f"¡CARCAJ! FLECHAS: {partida['cantidad_flechas']}/{MAX_FLECHAS}")
                    else:
                        partida["dano_flecha"] += 4
                        mostrar_aviso(partida, "¡MAXIMO DE FLECHAS! +4 ATK")
                    partida["puntos"] += 75

            # Atracción magnética rápida para Gemas XP
            for g in partida["gemas_xp"][:]:
                dist = math.hypot(partida["wx"] - g["x"], partida["wy"] - g["y"])
                if dist <= rango_actual:
                    ang = math.atan2(partida["wy"] - g["y"], partida["wx"] - g["x"])
                    factor = max(0.0, 1.0 - (dist / rango_actual))
                    vel_iman = 16.0 + factor * 18.0
                    g["x"] += math.cos(ang) * vel_iman
                    g["y"] += math.sin(ang) * vel_iman
                if dist <= 32:
                    partida["gemas_xp"].remove(g)
                    partida["xp"] += 1
                    partida["puntos"] += 5
                    if partida["xp"] >= partida["xp_siguiente"]:
                        partida["nivel"] += 1
                        partida["xp"] = 0
                        partida["xp_siguiente"] = int(partida["xp_siguiente"] * 1.48)
                        partida["dano_flecha"] += 1
                        mostrar_aviso(partida, f"¡NIVEL {partida['nivel']}! RANGO +9px")

            # Atracción magnética rápida para Corazones
            for cor in partida["corazones_suelo"][:]:
                dist = math.hypot(partida["wx"] - cor["x"], partida["wy"] - cor["y"])
                if dist <= rango_actual:
                    ang = math.atan2(partida["wy"] - cor["y"], partida["wx"] - cor["x"])
                    factor = max(0.0, 1.0 - (dist / rango_actual))
                    vel_iman = 16.0 + factor * 18.0
                    cor["x"] += math.cos(ang) * vel_iman
                    cor["y"] += math.sin(ang) * vel_iman
                if dist <= 32:
                    partida["corazones_suelo"].remove(cor)
                    partida["corazones_run"] += 1
                    partida["puntos"] += 10

            if partida["hp"] <= 0:
                bonus_p = 1.0 + (progreso["prestigio"] * 0.05)
                ganados = int(round(partida["corazones_run"] * bonus_p))
                progreso["corazones"] += ganados
                guardar_progreso(progreso)
                guardar_score(partida["puntos"], partida["nivel"], progreso["prestigio"])
                partida["corazones_finales"] = ganados
                estado = "GAME_OVER"

        # --- RENDERIZADO CON CÁMARA CENTRADA EN EL JUGADOR ---
        dibujar_mundo_infinito(pantalla, partida)

        # Aura de recogida en el centro de pantalla
        aura = pygame.Surface((rango_actual * 2, rango_actual * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura, (120, 210, 255, 16), (rango_actual, rango_actual), rango_actual)
        pygame.draw.circle(aura, (120, 210, 255, 50), (rango_actual, rango_actual), rango_actual, width=2)
        pantalla.blit(aura, (ANCHO // 2 - rango_actual, ALTO // 2 - rango_actual))

        for c in partida["cofres"]:
            sx, sy = int(c["x"] - cam_x), int(c["y"] - cam_y)
            if -60 <= sx <= ANCHO + 60 and -60 <= sy <= ALTO + 60:
                pantalla.blit(SPRITE_COFRE, (sx - 22, sy - 19))

        if partida["goblin"] is not None:
            gx, gy = int(partida["goblin"]["x"] - cam_x), int(partida["goblin"]["y"] - cam_y)
            if -80 <= gx <= ANCHO + 80 and -80 <= gy <= ALTO + 80:
                halo_g = pygame.Surface((90, 90), pygame.SRCALPHA)
                pygame.draw.circle(halo_g, (245, 200, 65, 45), (45, 45), 42)
                pantalla.blit(halo_g, (gx - 45, gy - 45))
                pantalla.blit(SPRITE_GOBLIN, (gx - 26, gy - 26))
                segs_g = max(1, partida["goblin"]["tiempo_restante"] // 60)
                lbl_g = fuente_hud.render(f"GOBLIN ({segs_g}s)", True, (255, 225, 80))
                pantalla.blit(lbl_g, lbl_g.get_rect(center=(gx, gy - 42)))
            else:
                dibujar_indicador_borde(pantalla, partida["wx"], partida["wy"], partida["goblin"]["x"], partida["goblin"]["y"], (255, 215, 65), "GOBLIN")

        # Brújula al cofre más cercano
        if partida["cofres"]:
            cofre_cercano = min(partida["cofres"], key=lambda c: math.hypot(c["x"] - partida["wx"], c["y"] - partida["wy"]))
            dibujar_indicador_borde(pantalla, partida["wx"], partida["wy"], cofre_cercano["x"], cofre_cercano["y"], (110, 215, 255), "COFRE")

        for k in partida["carcajes_suelo"]:
            sx, sy = int(k["x"] - cam_x), int(k["y"] - cam_y)
            if -50 <= sx <= ANCHO + 50 and -50 <= sy <= ALTO + 50:
                pantalla.blit(SPRITE_CARCAJ, (sx - 17, sy - 17))

        for g in partida["gemas_xp"]:
            sx, sy = int(g["x"] - cam_x), int(g["y"] - cam_y)
            if -20 <= sx <= ANCHO + 20 and -20 <= sy <= ALTO + 20:
                pygame.draw.circle(pantalla, (85, 215, 255), (sx, sy), 6)

        for cor in partida["corazones_suelo"]:
            sx, sy = int(cor["x"] - cam_x), int(cor["y"] - cam_y)
            if -30 <= sx <= ANCHO + 30 and -30 <= sy <= ALTO + 30:
                pantalla.blit(SPRITE_CORAZON, (sx - 12, sy - 11))

        for e in partida["enemigos"]:
            sx, sy = int(e["x"] - cam_x), int(e["y"] - cam_y)
            if -60 <= sx <= ANCHO + 60 and -60 <= sy <= ALTO + 60:
                if e["tipo"] == "elite":
                    base_spr = SPRITE_VAMPIRO_ELITE
                elif e["tipo"] == "acechador":
                    base_spr = SPRITE_VAMPIRO_ACECHADOR
                else:
                    base_spr = SPRITE_VAMPIRO
                spr = pygame.transform.flip(base_spr, True, False) if e["mirando_izq"] else base_spr
                pantalla.blit(spr, (sx - 23, sy - 23))

        for f in partida["flechas"]:
            sx, sy = int(f["x"] - cam_x), int(f["y"] - cam_y)
            if -50 <= sx <= ANCHO + 50 and -50 <= sy <= ALTO + 50:
                if f["tipo"] == "homing":
                    base_f = SPRITE_FLECHA_HOMING
                elif f["tipo"] == "rebote":
                    base_f = SPRITE_FLECHA_REBOTE
                else:
                    base_f = SPRITE_FLECHA_NORMAL
                ang_deg = -math.degrees(math.atan2(f["vy"], f["vx"]))
                spr_f = pygame.transform.rotate(base_f, ang_deg)
                pantalla.blit(spr_f, spr_f.get_rect(center=(sx, sy)))

        # Cazador siempre en el centro de la cámara
        spr_jug = pygame.transform.flip(SPRITE_HUNTER, True, False) if partida["mirando_izq"] else SPRITE_HUNTER
        pantalla.blit(spr_jug, (ANCHO // 2 - 24, ALTO // 2 - 24))

        # Aviso visual de Maldición Anti-AFK
        if partida["frames_quieto"] > 120 and estado == "JUGANDO":
            alerta_afk = fuente_aviso.render("¡MUÉVETE! LA OSCURIDAD TE CONSUME", True, (255, 65, 85))
            pantalla.blit(alerta_afk, alerta_afk.get_rect(center=(ANCHO // 2, ALTO // 2 - 75)))

        # HUD Superior
        mins = (partida["frames_jugados"] // 60) // 60
        segs = (partida["frames_jugados"] // 60) % 60
        hud_izq = fuente_hud.render(
            f"HP: {int(partida['hp'])}/{partida['hp_max']}  |  LVL: {partida['nivel']} ({partida['xp']}/{partida['xp_siguiente']})  |  TIEMPO: {mins:02d}:{segs:02d}",
            True, (245, 245, 250)
        )
        pantalla.blit(hud_izq, (32, 22))

        pantalla.blit(SPRITE_CORAZON, (32, 56))
        hud_cor = fuente_hud.render(
            f"x{partida['corazones_run']}  |  POS: ({int(partida['wx']//96)}, {int(partida['wy']//96)})  |  DROPS EN MUNDO: {len(partida['gemas_xp']) + len(partida['corazones_suelo'])}",
            True, (255, 110, 130)
        )
        pantalla.blit(hud_cor, (64, 55))

        hud_der = fuente_hud.render(
            f"FLECHAS: {partida['cantidad_flechas']}/{MAX_FLECHAS} (Homing: {partida['flechas_homing']})  |  ATK: {partida['dano_flecha']}  |  VEL: {partida['vel_jugador']}/{VEL_MAX_JUGADOR}",
            True, (245, 200, 65)
        )
        pantalla.blit(hud_der, (ANCHO - hud_der.get_width() - 32, 22))

        if partida["timer_aviso"] > 0 and estado == "JUGANDO":
            partida["timer_aviso"] -= 1
            aviso = fuente_aviso.render(partida["mensaje_aviso"], True, (255, 225, 90))
            pantalla.blit(aviso, aviso.get_rect(center=(ANCHO // 2, 105)))

        # --- TIENDA DEL GOBLIN ---
        if estado == "GOBLIN_SHOP":
            velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            velo.fill((10, 14, 12, 215))
            pantalla.blit(velo, (0, 0))

            pantalla.blit(pygame.transform.scale(SPRITE_GOBLIN, (84, 84)), (ANCHO // 2 - 42, 95))
            txt_g = fuente_titulo.render("MERCADER GOBLIN", True, (110, 225, 100))
            pantalla.blit(txt_g, txt_g.get_rect(center=(ANCHO // 2, 215)))

            pantalla.blit(pygame.transform.scale(SPRITE_CORAZON, (30, 28)), (ANCHO // 2 - 190, 260))
            txt_saldo_g = fuente_boton.render(f"Tus Corazones: {partida['corazones_run']}", True, (255, 120, 140))
            pantalla.blit(txt_saldo_g, (ANCHO // 2 - 150, 256))

            costo_homing = 14 + partida["flechas_homing"] * 6
            ofertas_goblin = [
                (f"+1 Flecha Perseguidora ({partida['flechas_homing']}/{MAX_FLECHAS} activas)", "homing", costo_homing, partida["flechas_homing"] >= MAX_FLECHAS),
                ("Flecha Rebotadora (rebota x3 veces)", "rebote", 20, partida["flecha_rebote"]),
                (f"+1 Flecha Extra ({partida['cantidad_flechas']}/{MAX_FLECHAS})", "flecha", 18, partida["cantidad_flechas"] >= MAX_FLECHAS),
                ("Pocion de Sangre (Restaura 100% HP)", "curar", 8, partida["hp"] >= partida["hp_max"]),
            ]

            for idx, (desc, clave, costo, agotado) in enumerate(ofertas_goblin):
                y_f = 310 + idx * 110
                panel = pygame.Rect(ANCHO // 2 - 500, y_f, 700, 62)
                pygame.draw.rect(pantalla, (30, 38, 34), panel, border_radius=10)
                pygame.draw.rect(pantalla, (95, 145, 95), panel, width=2, border_radius=10)
                lbl = fuente_hud.render(desc, True, (240, 245, 240))
                pantalla.blit(lbl, (panel.x + 20, panel.y + 18))

                btn_buy = pygame.Rect(ANCHO // 2 + 230, y_f, 230, 62)
                if agotado:
                    dibujar_boton(pantalla, "MAXIMO", btn_buy, pos_mouse, activo=False)
                else:
                    puede = partida["corazones_run"] >= costo
                    dibujar_boton(pantalla, f"{costo} Corazones", btn_buy, pos_mouse, color_hover=(75, 175, 85), activo=puede)

            btn_cerrar_goblin = pygame.Rect(ANCHO // 2 - 190, 810, 380, 66)
            dibujar_boton(pantalla, "SEGUIR CAZANDO", btn_cerrar_goblin, pos_mouse)

        # --- PAUSA ---
        elif estado == "PAUSA":
            velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            velo.fill((10, 12, 18, 185))
            pantalla.blit(velo, (0, 0))

            txt_pausa = fuente_titulo.render("JUEGO EN PAUSA", True, (245, 200, 65))
            pantalla.blit(txt_pausa, txt_pausa.get_rect(center=(ANCHO // 2, 280)))

            dibujar_boton(pantalla, "CONTINUAR (ESC)", btn_continuar, pos_mouse, color_hover=(60, 165, 105))
            dibujar_boton(pantalla, "REINICIAR PARTIDA", btn_reiniciar, pos_mouse)
            dibujar_boton(pantalla, "VOLVER AL MENU", btn_pausa_menu, pos_mouse, color_hover=(185, 45, 60))

    # --- GAME OVER ---
    elif estado == "GAME_OVER":
        titulo = fuente_titulo.render("HAS CAIDO ANTE LA HORDA", True, (220, 55, 70))
        ganados = partida.get("corazones_finales", partida["corazones_run"])
        resumen = fuente_boton.render(
            f"Puntaje: {partida['puntos']} PTS  |  Nivel: {partida['nivel']}  |  Corazones a tu Red: +{ganados}",
            True, (240, 240, 245)
        )
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 340)))
        pantalla.blit(resumen, resumen.get_rect(center=(ANCHO // 2, 440)))
        dibujar_boton(pantalla, "VOLVER AL MENU", btn_volver, pos_mouse)

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()