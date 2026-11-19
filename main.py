import pygame
import random
import math
import json
import os

from sprites import BancoSprites
from mundo import TAM_CHUNK, obtener_chunk, dibujar_mundo_infinito, dibujar_minimapa
from audio import GestorAudio

# 1. Configuración inicial 1080p Pantalla Completa
pygame.init()
ANCHO, ALTO = 1920, 1080
pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Vampire Hunter - Infinite Roguelike v1.2")
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

sprites = BancoSprites()
audio = GestorAudio()

# 2. Red de Sangre Rebalanceada + Robo de Vida / Regeneración + Prestigio
def generar_red_sangre(nivel_red, prestigio, bonus_flechas_actual=0):
    cx, cy = ANCHO // 2, 515
    rng = random.Random(1000 + nivel_red * 37 + prestigio * 911)
    costo_1 = 8 + (nivel_red - 1) * 5
    costo_2 = 18 + (nivel_red - 1) * 8
    costo_3 = 32 + (nivel_red - 1) * 14

    nodos = [
        {"id": 0, "x": cx, "y": cy, "tipo": "centro", "nombre": f"RED {nivel_red}", "valor": 0, "costo": 0, "comprado": True, "padres": []}
    ]

    tipos_1 = [
        ("dano", "+3 ATK", 3),
        ("vida", "+8 HP", 8),
        ("regen", "+0.2 REGEN", 0.2),
        ("robo", "+0.25 ROBO", 0.25),
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
        ("dano", "+4 ATK", 4),
        ("vida", "+12 HP", 12),
        ("regen", "+0.3 REGEN", 0.3),
        ("robo", "+0.35 ROBO", 0.35),
        ("iman", "+10 RANGO", 10),
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

    nodo_especial = ("flecha", "+1 FLECHA", 1) if (nivel_red % 2 == 0 and bonus_flechas_actual < 2) else ("robo", "+0.5 ROBO", 0.5)
    tipos_3 = [
        nodo_especial,
        ("dano", "+6 ATK", 6),
        ("vida", "+18 HP", 18),
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
        "bonus_regen": 0.0,
        "bonus_robo": 0.0,
        "nodos": [],
    }
    if not os.path.exists(ARCHIVO_PROGRESO):
        default["nodos"] = generar_red_sangre(1, 0, 0)
        return default
    try:
        with open(ARCHIVO_PROGRESO, "r", encoding="utf-8") as f:
            data = json.load(f)
            default.update(data)
            if not default["nodos"]:
                default["nodos"] = generar_red_sangre(default["nivel_red"], default["prestigio"], default["bonus_flechas"])
            return default
    except (json.JSONDecodeError, OSError):
        default["nodos"] = generar_red_sangre(1, 0, 0)
        return default

progreso = cargar_progreso()

def guardar_progreso(prog):
    with open(ARCHIVO_PROGRESO, "w", encoding="utf-8") as f:
        json.dump(prog, f, indent=2)

def otorgar_corazones_directo(partida, cantidad_base):
    mult_p = 1.0 + (progreso["prestigio"] * 0.05)
    ganados = max(1, int(round(cantidad_base * mult_p)))
    partida["corazones_run"] += ganados
    progreso["corazones"] += ganados
    guardar_progreso(progreso)
    return ganados

def nodo_desbloqueable(nodo, todos_nodos):
    if nodo["comprado"]:
        return False
    mapa = {n["id"]: n for n in todos_nodos}
    return any(mapa[pid]["comprado"] for pid in nodo["padres"] if pid in mapa)

def aplicar_nodo_comprado(nodo):
    t, v = nodo["tipo"], nodo["valor"]
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
    elif t == "regen":
        progreso["bonus_regen"] = round(progreso["bonus_regen"] + float(v), 2)
    elif t == "robo":
        progreso["bonus_robo"] = round(progreso["bonus_robo"] + float(v), 2)

    if all(n["comprado"] for n in progreso["nodos"]):
        progreso["nivel_red"] += 1
        progreso["nodos"] = generar_red_sangre(progreso["nivel_red"], progreso["prestigio"], progreso["bonus_flechas"])

def ejecutar_prestigio():
    progreso["prestigio"] += 1
    progreso["nivel_red"] = 1
    progreso["bonus_flechas"] = 0
    progreso["bonus_dano"] = 0
    progreso["bonus_vida"] = 0
    progreso["bonus_iman"] = 0
    progreso["bonus_cadencia"] = 0
    progreso["bonus_vel"] = 0.0
    progreso["bonus_regen"] = 0.0
    progreso["bonus_robo"] = 0.0
    progreso["nodos"] = generar_red_sangre(1, progreso["prestigio"], 0)
    guardar_progreso(progreso)

# 3. Botones UI
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

# 4. Estado inicial de partida
def iniciar_partida():
    mult_prestigio = 1.0 + (progreso["prestigio"] * 0.05)
    hp_inicial = 110 + progreso["bonus_vida"]
    dano_inicial = int((24 + progreso["bonus_dano"]) * mult_prestigio)
    cd_inicial = max(22, int(50 * (1.0 - progreso["bonus_cadencia"] / 100.0)))
    vel_inicial = min(VEL_MAX_JUGADOR, round(4.9 + progreso["bonus_vel"], 2))

    p = {
        "semilla": random.randint(1, 999999),
        "chunks": {},
        "wx": 0.0,
        "wy": 0.0,
        "mirando_izq": False,
        "vel_jugador": vel_inicial,
        "hp_max": hp_inicial,
        "hp": float(hp_inicial),
        "regen_hp": round(0.30 + progreso["bonus_regen"], 2),     # HP por segundo
        "robo_vida": round(0.35 + progreso["bonus_robo"], 2),     # HP curado por impacto de flecha
        "xp": 0,
        "xp_siguiente": 7,
        "nivel": 1,
        "puntos": 0,
        "corazones_run": 0,
        "rango_base": 75 + progreso["bonus_iman"],
        "cantidad_flechas": min(MAX_FLECHAS, 1 + progreso["bonus_flechas"]),
        "flechas_homing": 0,
        "flecha_rebote": False,
        "cooldown_flecha": cd_inicial,
        "timer_flecha": 0,
        "dano_flecha": dano_inicial,
        "vel_flecha": 13.0,
        "cd_dash": 0,
        "dash_activo": 0,
        "dash_vx": 0.0,
        "dash_vy": 0.0,
        "enemigos": [],
        "jefe": None,
        "proyectiles_enemigos": [],
        "flechas": [],
        "gemas_xp": [],
        "corazones_suelo": [],
        "carcajes_suelo": [],
        "cofres": [],
        "goblin": None,
        "frames_jugados": 0,
        "frames_quieto": 0,
        "timer_spawn": 0,
        "timer_horda": 0,
        "mensaje_aviso": "",
        "timer_aviso": 0,
    }
    for cx in (-1, 0, 1):
        for cy in (-1, 0, 1):
            obtener_chunk(p, cx, cy)
    return p

def obtener_rango_recogida(partida):
    return partida["rango_base"] + (partida["nivel"] - 1) * 9

def mostrar_aviso(partida, texto):
    partida["mensaje_aviso"] = texto
    partida["timer_aviso"] = 165

def generar_enemigo(partida, forzar_tipo=None):
    ang = random.uniform(0, 2 * math.pi)
    dist_spawn = random.uniform(1120, 1280)
    wx = partida["wx"] + math.cos(ang) * dist_spawn
    wy = partida["wy"] + math.sin(ang) * dist_spawn

    mins = (partida["frames_jugados"] // 60) // 60
    dist_mundo = math.hypot(partida["wx"], partida["wy"]) / 2200.0
    escala_dificultad = 1.0 + (mins * 0.42) + (dist_mundo * 0.22)

    roll = random.random()
    tipo = forzar_tipo
    if tipo is None:
        if partida["nivel"] >= 2 and roll < min(0.28, 0.08 + partida["nivel"] * 0.02):
            tipo = "elite"
        elif roll < 0.22:
            tipo = "errante"     # Vampiro que merodea y hace el tonto por su cuenta
        elif (mins >= 1 or partida["nivel"] >= 3) and roll < 0.48:
            tipo = "acechador"
        elif (mins >= 1 or partida["nivel"] >= 4) and roll < 0.65:
            tipo = "mago"
        else:
            tipo = "normal"

    ang_errante = random.uniform(0, 2 * math.pi)
    if tipo == "elite":
        hp = int((155 + partida["nivel"] * 34) * escala_dificultad)
        vel = min(4.5, 2.15 + partida["nivel"] * 0.05)
    elif tipo == "acechador":
        hp = int((48 + partida["nivel"] * 13) * escala_dificultad)
        vel = min(5.6, 3.2 + partida["nivel"] * 0.06)
    elif tipo == "mago":
        hp = int((60 + partida["nivel"] * 16) * escala_dificultad)
        vel = min(3.3, 1.9 + partida["nivel"] * 0.04)
    elif tipo == "errante":
        hp = int((45 + partida["nivel"] * 12) * escala_dificultad)
        vel = 1.65
    else:
        hp = int((60 + partida["nivel"] * 18) * escala_dificultad)
        vel = min(4.8, 2.35 + partida["nivel"] * 0.05)

    partida["enemigos"].append({
        "x": wx,
        "y": wy,
        "hp": hp,
        "vel": vel,
        "tipo": tipo,
        "cd_ataque": random.randint(90, 150),
        "ang_errante": ang_errante,
        "timer_errante": random.randint(35, 95),
        "pausa_errante": 0,
        "mirando_izq": False
    })

def invocar_jefe(partida):
    if partida["jefe"] is not None:
        return
    ang = random.uniform(0, 2 * math.pi)
    jx = partida["wx"] + math.cos(ang) * 850
    jy = partida["wy"] + math.sin(ang) * 850
    mins = max(1, (partida["frames_jugados"] // 60) // 60)
    hp_jefe = int((1250 + partida["nivel"] * 220) * (1.0 + mins * 0.35))

    partida["jefe"] = {
        "x": jx,
        "y": jy,
        "hp": hp_jefe,
        "hp_max": hp_jefe,
        "vel": 2.3,
        "cd_patron": 155,
        "mirando_izq": False
    }
    audio.tocar("jefe")
    mostrar_aviso(partida, "¡LORD VAMPIRO HA APARECIDO! REVISA EL RADAR")

def aplicar_mejora_cofre(partida):
    mejoras = [
        ("DAÑO DE FLECHA +4", "dano"),
        ("ROBO DE VIDA +0.15", "robo"),
        ("REGENERACION +0.25/s", "regen"),
        ("VIDA MAX +12 Y CURACION", "vida"),
        ("CADENCIA DE TIRO +5%", "cadencia"),
    ]
    if partida["vel_jugador"] < VEL_MAX_JUGADOR:
        mejoras.append(("VELOCIDAD +4%", "vel"))
    if partida["cantidad_flechas"] < MAX_FLECHAS and random.random() < 0.28:
        mejoras.append(("¡MULTIDISPARO! +1 FLECHA", "flecha"))

    nombre, tipo = random.choice(mejoras)
    if tipo == "flecha":
        partida["cantidad_flechas"] = min(MAX_FLECHAS, partida["cantidad_flechas"] + 1)
    elif tipo == "dano":
        partida["dano_flecha"] += 4
    elif tipo == "robo":
        partida["robo_vida"] = round(partida["robo_vida"] + 0.15, 2)
    elif tipo == "regen":
        partida["regen_hp"] = round(partida["regen_hp"] + 0.25, 2)
    elif tipo == "cadencia":
        partida["cooldown_flecha"] = max(14, int(partida["cooldown_flecha"] * 0.95))
    elif tipo == "vel":
        partida["vel_jugador"] = min(VEL_MAX_JUGADOR, round(partida["vel_jugador"] * 1.04, 2))
    elif tipo == "vida":
        partida["hp_max"] += 12
        partida["hp"] = min(float(partida["hp_max"]), partida["hp"] + 30)

    audio.tocar("cofre")
    mostrar_aviso(partida, f"COFRE: {nombre}")

def activar_altar_mundo(partida):
    mejoras_altar = [
        ("BENDICION DE SANGRE: +5 ATK", "dano"),
        ("VAMPIRO ANCESTRAL: +0.25 ROBO DE VIDA", "robo"),
        ("SANGRE VIVA: +0.35 REGEN/s", "regen"),
        ("VITALIDAD ANTIGUA: +15 HP MAX", "vida"),
    ]
    if partida["cantidad_flechas"] < MAX_FLECHAS and random.random() < 0.35:
        mejoras_altar.append(("RELIQUIA DE CAZA: +1 FLECHA", "flecha"))

    nombre, tipo = random.choice(mejoras_altar)
    if tipo == "dano":
        partida["dano_flecha"] += 5
    elif tipo == "robo":
        partida["robo_vida"] = round(partida["robo_vida"] + 0.25, 2)
    elif tipo == "regen":
        partida["regen_hp"] = round(partida["regen_hp"] + 0.35, 2)
    elif tipo == "vida":
        partida["hp_max"] += 15
        partida["hp"] = min(float(partida["hp_max"]), partida["hp"] + 35)
    elif tipo == "flecha":
        partida["cantidad_flechas"] = min(MAX_FLECHAS, partida["cantidad_flechas"] + 1)

    audio.tocar("cofre")
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
    audio.tocar("cofre")
    mostrar_aviso(partida, "¡GOBLIN MERCADER CERCA! SIGUE EL PUNTO DORADO EN EL RADAR")

def dibujar_indicador_borde(superficie, origen_wx, origen_wy, destino_wx, destino_wy, color, etiqueta):
    dx = destino_wx - origen_wx
    dy = destino_wy - origen_wy
    sx = ANCHO // 2 + dx
    sy = ALTO // 2 + dy
    if 30 <= sx <= ANCHO - 30 and 30 <= sy <= ALTO - 30:
        return
    ang = math.atan2(dy, dx)
    bx = ANCHO // 2 + math.cos(ang) * (ANCHO // 2 - 55)
    by = ALTO // 2 + math.sin(ang) * (ALTO // 2 - 55)
    pygame.draw.circle(superficie, color, (int(bx), int(by)), 12)
    pygame.draw.circle(superficie, (255, 255, 255), (int(bx), int(by)), 12, width=2)
    lbl = fuente_nodo.render(etiqueta, True, color)
    superficie.blit(lbl, lbl.get_rect(center=(int(bx), int(by) - 20)))

# Botones UI
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

# 5. Bucle principal
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

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_m:
                silencio = audio.alternar_mute()
                if estado == "JUGANDO":
                    mostrar_aviso(partida, "AUDIO SILENCIADO (M)" if silencio else "AUDIO ACTIVADO (M)")

            if evento.key == pygame.K_ESCAPE:
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

            if estado == "JUGANDO" and evento.key in (pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT):
                if partida["cd_dash"] <= 0 and partida["dash_activo"] <= 0:
                    teclas_now = pygame.key.get_pressed()
                    ddx = (teclas_now[pygame.K_d] or teclas_now[pygame.K_RIGHT]) - (teclas_now[pygame.K_a] or teclas_now[pygame.K_LEFT])
                    ddy = (teclas_now[pygame.K_s] or teclas_now[pygame.K_DOWN]) - (teclas_now[pygame.K_w] or teclas_now[pygame.K_UP])
                    if ddx == 0 and ddy == 0:
                        ddx = -1.0 if partida["mirando_izq"] else 1.0
                    norm = math.hypot(ddx, ddy) or 1.0
                    vel_dash = 15.5
                    partida["dash_vx"] = (ddx / norm) * vel_dash
                    partida["dash_vy"] = (ddy / norm) * vel_dash
                    partida["dash_activo"] = 12
                    partida["cd_dash"] = 75
                    audio.tocar("dash")

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
                            audio.tocar("pickup")
                            break

                if btn_prestigio.collidepoint(pos_mouse) and progreso["nivel_red"] >= 5:
                    ejecutar_prestigio()
                    audio.tocar("cofre")
                elif btn_volver_red.collidepoint(pos_mouse):
                    estado = "MENU"

            elif estado == "PAUSA":
                if btn_continuar.collidepoint(pos_mouse):
                    estado = "JUGANDO"
                elif btn_reiniciar.collidepoint(pos_mouse):
                    partida = iniciar_partida()
                    estado = "JUGANDO"
                elif btn_pausa_menu.collidepoint(pos_mouse):
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
                        audio.tocar("cofre")
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
            f"Infinite Roguelike v1.2  |  Prestigio P{progreso['prestigio']} (+{progreso['prestigio']*5}% Bono)  |  Red Lvl {progreso['nivel_red']}",
            True, (245, 200, 80)
        )
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 175)))
        pantalla.blit(subtitulo, subtitulo.get_rect(center=(ANCHO // 2, 240)))

        pantalla.blit(pygame.transform.scale(sprites.corazon, (34, 31)), (ANCHO // 2 - 180, 300))
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
            f"Prestigio: P{progreso['prestigio']} (+{progreso['prestigio']*5}% Bono)  |  "
            f"ATK +{progreso['bonus_dano']}  |  HP +{progreso['bonus_vida']}  |  REGEN +{progreso['bonus_regen']}/s  |  ROBO +{progreso['bonus_robo']}",
            True, (210, 215, 230)
        )
        pantalla.blit(resumen_bonos, resumen_bonos.get_rect(center=(ANCHO // 2, 125)))

        pantalla.blit(pygame.transform.scale(sprites.corazon, (30, 28)), (ANCHO // 2 - 190, 162))
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
        sinergia_activa = partida["flechas_homing"] > 0 and partida["flecha_rebote"]

        # Daño escalado para que al minuto 10 las flechas sigan teniendo pegada real
        mins_actuales = (partida["frames_jugados"] // 60) // 60
        dano_efectivo = partida["dano_flecha"] + (partida["nivel"] - 1) * 2 + mins_actuales * 6

        if estado == "JUGANDO":
            partida["frames_jugados"] += 1
            if partida["cd_dash"] > 0:
                partida["cd_dash"] -= 1

            # Regeneración pasiva de vida por segundo
            if partida["hp"] < partida["hp_max"]:
                partida["hp"] = min(float(partida["hp_max"]), partida["hp"] + (partida["regen_hp"] / 60.0))

            # Jefe Vampiro cada 3 minutos exactos
            if partida["frames_jugados"] > 0 and partida["frames_jugados"] % 10800 == 0:
                invocar_jefe(partida)

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

            if partida["dash_activo"] > 0:
                partida["dash_activo"] -= 1
                partida["wx"] += partida["dash_vx"]
                partida["wy"] += partida["dash_vy"]
                partida["frames_quieto"] = 0
            else:
                teclas = pygame.key.get_pressed()
                dx = (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - (teclas[pygame.K_a] or teclas[pygame.K_LEFT])
                dy = (teclas[pygame.K_s] or teclas[pygame.K_DOWN]) - (teclas[pygame.K_w] or teclas[pygame.K_UP])

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

            partida["timer_spawn"] += 1
            partida["timer_horda"] += 1
            if partida["timer_horda"] >= 2700:
                partida["timer_horda"] = 0
                for _ in range(5):
                    generar_enemigo(partida, forzar_tipo="acechador")
                mostrar_aviso(partida, "¡EVENTO DE HORDA! ACECHADORES EN CAMINO")

            intervalo_spawn = max(8, 56 - partida["nivel"] * 4)
            if partida["timer_spawn"] >= intervalo_spawn:
                generar_enemigo(partida)
                if partida["nivel"] >= 6 and random.random() < 0.35:
                    generar_enemigo(partida)
                partida["timer_spawn"] = 0

            partida["timer_flecha"] += 1
            objetivos_posibles = list(partida["enemigos"])
            if partida["jefe"] is not None:
                objetivos_posibles.append(partida["jefe"])

            if partida["timer_flecha"] >= partida["cooldown_flecha"] and objetivos_posibles:
                objetivo = min(
                    objetivos_posibles,
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
                        "mult_dano": 1.0,
                        "golpeados": set(),
                        "vida_frames": 120,
                    })
                partida["timer_flecha"] = 0
                audio.tocar("disparo")

            # Actualizar flechas + Robo de vida al impactar
            for f in partida["flechas"][:]:
                f["vida_frames"] -= 1
                if f["vida_frames"] <= 0:
                    partida["flechas"].remove(f)
                    continue

                if f["tipo"] == "homing" and objetivos_posibles:
                    blanco = min(
                        objetivos_posibles,
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

                impacto_ocurrido = False

                if partida["jefe"] is not None and id(partida["jefe"]) not in f["golpeados"]:
                    if math.hypot(partida["jefe"]["x"] - f["x"], partida["jefe"]["y"] - f["y"]) <= 52:
                        partida["jefe"]["hp"] -= int(dano_efectivo * f["mult_dano"])
                        partida["hp"] = min(float(partida["hp_max"]), partida["hp"] + partida["robo_vida"])
                        f["golpeados"].add(id(partida["jefe"]))
                        impacto_ocurrido = True
                        audio.tocar("golpe")
                        if partida["jefe"]["hp"] <= 0:
                            jx, jy = partida["jefe"]["x"], partida["jefe"]["y"]
                            for k in range(12):
                                ang_b = (2 * math.pi * k) / 12
                                partida["corazones_suelo"].append({"x": jx + math.cos(ang_b) * 35, "y": jy + math.sin(ang_b) * 35})
                            partida["cofres"].append({"x": jx, "y": jy})
                            partida["puntos"] += 350
                            partida["jefe"] = None
                            audio.tocar("cofre")
                            mostrar_aviso(partida, "¡LORD VAMPIRO DERROTADO! COFRE Y CORAZONES SOLTADOS")

                if not impacto_ocurrido:
                    for e in partida["enemigos"][:]:
                        if id(e) in f["golpeados"]:
                            continue
                        if math.hypot(e["x"] - f["x"], e["y"] - f["y"]) <= 30:
                            e["hp"] -= int(dano_efectivo * f["mult_dano"])
                            partida["hp"] = min(float(partida["hp_max"]), partida["hp"] + partida["robo_vida"])
                            f["golpeados"].add(id(e))
                            impacto_ocurrido = True
                            audio.tocar("golpe")

                            if e["hp"] <= 0:
                                ex, ey = e["x"], e["y"]
                                partida["gemas_xp"].append({"x": ex, "y": ey})
                                if e["tipo"] == "elite" or random.random() < 0.34:
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
                            break

                if impacto_ocurrido:
                    if f["tipo"] == "rebote" and f["rebotes"] > 0:
                        f["rebotes"] -= 1
                        if sinergia_activa:
                            f["mult_dano"] += 0.25
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
                        elif f in partida["flechas"]:
                            partida["flechas"].remove(f)
                    elif f in partida["flechas"]:
                        partida["flechas"].remove(f)

            # Mover enemigos: los "errantes" hacen el tonto patrullando/pausando antes de acercarse
            frenesi = 1.35 if partida["frames_quieto"] > 120 else 1.0
            dano_contacto = 0.50 + (partida["nivel"] * 0.035)
            invulnerable = partida["dash_activo"] > 0

            for e in partida["enemigos"]:
                dist_e = math.hypot(partida["wx"] - e["x"], partida["wy"] - e["y"])
                if dist_e > 1650:
                    ang_re = random.uniform(0, 2 * math.pi)
                    e["x"] = partida["wx"] + math.cos(ang_re) * 1150
                    e["y"] = partida["wy"] + math.sin(ang_re) * 1150
                    continue

                if e["tipo"] == "errante":
                    if e["pausa_errante"] > 0:
                        e["pausa_errante"] -= 1
                        vx, vy = 0.0, 0.0
                    else:
                        e["timer_errante"] -= 1
                        if e["timer_errante"] <= 0:
                            e["timer_errante"] = random.randint(40, 100)
                            if random.random() < 0.30:
                                e["pausa_errante"] = random.randint(25, 65)
                            elif dist_e < 340 and random.random() < 0.45:
                                # Ocasionalmente mira hacia el jugador
                                e["ang_errante"] = math.atan2(partida["wy"] - e["y"], partida["wx"] - e["x"])
                            else:
                                # Cambia de rumbo sin lógica hacia cualquier lado
                                e["ang_errante"] += random.uniform(-2.2, 2.2)
                        vx = math.cos(e["ang_errante"]) * e["vel"] * frenesi
                        vy = math.sin(e["ang_errante"]) * e["vel"] * frenesi
                else:
                    ang = math.atan2(partida["wy"] - e["y"], partida["wx"] - e["x"])
                    factor_avance = 0.35 if (e["tipo"] == "mago" and dist_e < 430) else 1.0
                    vx = math.cos(ang) * e["vel"] * frenesi * factor_avance
                    vy = math.sin(ang) * e["vel"] * frenesi * factor_avance

                    if e["tipo"] == "mago" and dist_e < 760:
                        e["cd_ataque"] -= 1
                        if e["cd_ataque"] <= 0:
                            e["cd_ataque"] = 145
                            partida["proyectiles_enemigos"].append({
                                "x": e["x"], "y": e["y"],
                                "vx": math.cos(ang) * 5.2, "vy": math.sin(ang) * 5.2,
                                "dano": 10 + partida["nivel"], "vida": 160
                            })

                if abs(vx) > 0.05:
                    e["mirando_izq"] = vx < 0
                e["x"] += vx
                e["y"] += vy

                if not invulnerable and dist_e <= 36:
                    mult_tipo = 1.5 if e["tipo"] == "elite" else (1.2 if e["tipo"] == "acechador" else 0.85)
                    partida["hp"] -= dano_contacto * mult_tipo

            if partida["jefe"] is not None:
                jf = partida["jefe"]
                dist_j = math.hypot(partida["wx"] - jf["x"], partida["wy"] - jf["y"])
                if dist_j > 1600:
                    ang_j = random.uniform(0, 2 * math.pi)
                    jf["x"] = partida["wx"] + math.cos(ang_j) * 900
                    jf["y"] = partida["wy"] + math.sin(ang_j) * 900
                else:
                    ang_j = math.atan2(partida["wy"] - jf["y"], partida["wx"] - jf["x"])
                    vx_j = math.cos(ang_j) * jf["vel"]
                    jf["mirando_izq"] = vx_j < 0
                    jf["x"] += vx_j
                    jf["y"] += math.sin(ang_j) * jf["vel"]

                    jf["cd_patron"] -= 1
                    if jf["cd_patron"] <= 0:
                        jf["cd_patron"] = 165
                        for k in range(10):
                            ang_o = (2 * math.pi * k) / 10 + (tick_global * 0.05)
                            partida["proyectiles_enemigos"].append({
                                "x": jf["x"], "y": jf["y"],
                                "vx": math.cos(ang_o) * 4.8, "vy": math.sin(ang_o) * 4.8,
                                "dano": 13 + partida["nivel"], "vida": 180
                            })

                    if not invulnerable and dist_j <= 56:
                        partida["hp"] -= dano_contacto * 1.6

            for pe in partida["proyectiles_enemigos"][:]:
                pe["vida"] -= 1
                if pe["vida"] <= 0:
                    partida["proyectiles_enemigos"].remove(pe)
                    continue
                pe["x"] += pe["vx"]
                pe["y"] += pe["vy"]
                if not invulnerable and math.hypot(partida["wx"] - pe["x"], partida["wy"] - pe["y"]) <= 24:
                    partida["hp"] -= pe["dano"]
                    partida["proyectiles_enemigos"].remove(pe)

            for c in partida["cofres"][:]:
                if math.hypot(partida["wx"] - c["x"], partida["wy"] - c["y"]) <= 44:
                    partida["cofres"].remove(c)
                    partida["puntos"] += 50
                    aplicar_mejora_cofre(partida)

            for k in partida["carcajes_suelo"][:]:
                if math.hypot(partida["wx"] - k["x"], partida["wy"] - k["y"]) <= 44:
                    partida["carcajes_suelo"].remove(k)
                    audio.tocar("pickup")
                    if partida["cantidad_flechas"] < MAX_FLECHAS:
                        partida["cantidad_flechas"] += 1
                        mostrar_aviso(partida, f"¡CARCAJ! FLECHAS: {partida['cantidad_flechas']}/{MAX_FLECHAS}")
                    else:
                        dano_efectivo += 4
                        partida["dano_flecha"] += 4
                        mostrar_aviso(partida, "¡MAXIMO DE FLECHAS! +4 ATK")
                    partida["puntos"] += 75

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
                    audio.tocar("pickup")
                    if partida["xp"] >= partida["xp_siguiente"]:
                        partida["nivel"] += 1
                        partida["xp"] = 0
                        partida["xp_siguiente"] = int(partida["xp_siguiente"] * 1.48)
                        mostrar_aviso(partida, f"¡NIVEL {partida['nivel']}! RANGO +9px")

            # Corazones se suman automáticamente a tu Red de Sangre al recogerlos
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
                    otorgar_corazones_directo(partida, 1)
                    partida["puntos"] += 10
                    audio.tocar("pickup")

            if partida["hp"] <= 0:
                guardar_progreso(progreso)
                guardar_score(partida["puntos"], partida["nivel"], progreso["prestigio"])
                estado = "GAME_OVER"

        # --- RENDERIZADO ---
        dibujar_mundo_infinito(pantalla, partida, sprites, ANCHO, ALTO)

        aura = pygame.Surface((rango_actual * 2, rango_actual * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura, (120, 210, 255, 16), (rango_actual, rango_actual), rango_actual)
        pygame.draw.circle(aura, (120, 210, 255, 50), (rango_actual, rango_actual), rango_actual, width=2)
        pantalla.blit(aura, (ANCHO // 2 - rango_actual, ALTO // 2 - rango_actual))

        for c in partida["cofres"]:
            sx, sy = int(c["x"] - cam_x), int(c["y"] - cam_y)
            if -60 <= sx <= ANCHO + 60 and -60 <= sy <= ALTO + 60:
                pantalla.blit(sprites.cofre, (sx - 22, sy - 19))

        if partida["goblin"] is not None:
            gx, gy = int(partida["goblin"]["x"] - cam_x), int(partida["goblin"]["y"] - cam_y)
            if -80 <= gx <= ANCHO + 80 and -80 <= gy <= ALTO + 80:
                halo_g = pygame.Surface((90, 90), pygame.SRCALPHA)
                pygame.draw.circle(halo_g, (245, 200, 65, 45), (45, 45), 42)
                pantalla.blit(halo_g, (gx - 45, gy - 45))
                pantalla.blit(sprites.goblin, (gx - 26, gy - 26))
                segs_g = max(1, partida["goblin"]["tiempo_restante"] // 60)
                lbl_g = fuente_hud.render(f"GOBLIN ({segs_g}s)", True, (255, 225, 80))
                pantalla.blit(lbl_g, lbl_g.get_rect(center=(gx, gy - 42)))
            else:
                dibujar_indicador_borde(pantalla, partida["wx"], partida["wy"], partida["goblin"]["x"], partida["goblin"]["y"], (255, 215, 65), "GOBLIN")

        if partida["cofres"]:
            cofre_cercano = min(partida["cofres"], key=lambda c: math.hypot(c["x"] - partida["wx"], c["y"] - partida["wy"]))
            dibujar_indicador_borde(pantalla, partida["wx"], partida["wy"], cofre_cercano["x"], cofre_cercano["y"], (110, 215, 255), "COFRE")

        for k in partida["carcajes_suelo"]:
            sx, sy = int(k["x"] - cam_x), int(k["y"] - cam_y)
            if -50 <= sx <= ANCHO + 50 and -50 <= sy <= ALTO + 50:
                pantalla.blit(sprites.carcaj, (sx - 17, sy - 17))

        for g in partida["gemas_xp"]:
            sx, sy = int(g["x"] - cam_x), int(g["y"] - cam_y)
            if -20 <= sx <= ANCHO + 20 and -20 <= sy <= ALTO + 20:
                pygame.draw.circle(pantalla, (85, 215, 255), (sx, sy), 6)

        for cor in partida["corazones_suelo"]:
            sx, sy = int(cor["x"] - cam_x), int(cor["y"] - cam_y)
            if -30 <= sx <= ANCHO + 30 and -30 <= sy <= ALTO + 30:
                pantalla.blit(sprites.corazon, (sx - 12, sy - 11))

        for pe in partida["proyectiles_enemigos"]:
            sx, sy = int(pe["x"] - cam_x), int(pe["y"] - cam_y)
            if -30 <= sx <= ANCHO + 30 and -30 <= sy <= ALTO + 30:
                pygame.draw.circle(pantalla, (210, 65, 255), (sx, sy), 9)
                pygame.draw.circle(pantalla, (255, 190, 255), (sx, sy), 4)

        for e in partida["enemigos"]:
            sx, sy = int(e["x"] - cam_x), int(e["y"] - cam_y)
            if -60 <= sx <= ANCHO + 60 and -60 <= sy <= ALTO + 60:
                if e["tipo"] == "elite":
                    base_spr = sprites.vampiro_elite
                elif e["tipo"] == "acechador":
                    base_spr = sprites.vampiro_acechador
                elif e["tipo"] == "mago":
                    base_spr = sprites.vampiro_mago
                elif e["tipo"] == "errante":
                    base_spr = sprites.vampiro_errante
                else:
                    base_spr = sprites.vampiro
                spr = pygame.transform.flip(base_spr, True, False) if e["mirando_izq"] else base_spr
                pantalla.blit(spr, (sx - 23, sy - 23))

        if partida["jefe"] is not None:
            jf = partida["jefe"]
            jsx, jsy = int(jf["x"] - cam_x), int(jf["y"] - cam_y)
            if -120 <= jsx <= ANCHO + 120 and -120 <= jsy <= ALTO + 120:
                halo_j = pygame.Surface((130, 130), pygame.SRCALPHA)
                pygame.draw.circle(halo_j, (230, 30, 60, 48), (65, 65), 62)
                pantalla.blit(halo_j, (jsx - 65, jsy - 65))
                spr_j = pygame.transform.flip(sprites.jefe, True, False) if jf["mirando_izq"] else sprites.jefe
                pantalla.blit(spr_j, (jsx - 42, jsy - 42))
            else:
                dibujar_indicador_borde(pantalla, partida["wx"], partida["wy"], jf["x"], jf["y"], (255, 45, 70), "JEFE")

        for f in partida["flechas"]:
            sx, sy = int(f["x"] - cam_x), int(f["y"] - cam_y)
            if -50 <= sx <= ANCHO + 50 and -50 <= sy <= ALTO + 50:
                if f["tipo"] == "homing":
                    base_f = sprites.flecha_homing
                elif f["tipo"] == "rebote":
                    base_f = sprites.flecha_rebote
                else:
                    base_f = sprites.flecha_normal
                ang_deg = -math.degrees(math.atan2(f["vy"], f["vx"]))
                spr_f = pygame.transform.rotate(base_f, ang_deg)
                pantalla.blit(spr_f, spr_f.get_rect(center=(sx, sy)))

        spr_jug = pygame.transform.flip(sprites.hunter, True, False) if partida["mirando_izq"] else sprites.hunter
        if partida["dash_activo"] > 0:
            aura_d = pygame.Surface((68, 68), pygame.SRCALPHA)
            pygame.draw.circle(aura_d, (120, 240, 255, 85), (34, 34), 32)
            pantalla.blit(aura_d, (ANCHO // 2 - 34, ALTO // 2 - 34))
        pantalla.blit(spr_jug, (ANCHO // 2 - 24, ALTO // 2 - 24))

        dibujar_minimapa(pantalla, partida, ANCHO, ALTO, fuente_nodo)

        if partida["jefe"] is not None:
            jf = partida["jefe"]
            bw, bh = 540, 22
            bx = ANCHO // 2 - bw // 2
            by = ALTO - 70
            pygame.draw.rect(pantalla, (35, 20, 28), (bx, by, bw, bh), border_radius=6)
            pct = max(0.0, jf["hp"] / max(1, jf["hp_max"]))
            pygame.draw.rect(pantalla, (225, 35, 65), (bx, by, int(bw * pct), bh), border_radius=6)
            pygame.draw.rect(pantalla, (245, 200, 75), (bx, by, bw, bh), width=2, border_radius=6)
            lbl_j = fuente_hud.render(f"LORD VAMPIRO: {int(jf['hp'])}/{jf['hp_max']}", True, (255, 225, 230))
            pantalla.blit(lbl_j, lbl_j.get_rect(center=(ANCHO // 2, by - 16)))

        if partida["frames_quieto"] > 120 and estado == "JUGANDO":
            alerta_afk = fuente_aviso.render("¡MUÉVETE! LA OSCURIDAD TE CONSUME", True, (255, 65, 85))
            pantalla.blit(alerta_afk, alerta_afk.get_rect(center=(ANCHO // 2, ALTO // 2 - 75)))

        # HUD Superior
        mins = (partida["frames_jugados"] // 60) // 60
        segs = (partida["frames_jugados"] // 60) % 60
        dash_txt = "LISTO [ESPACIO]" if partida["cd_dash"] <= 0 else f"CD {round(partida['cd_dash']/60, 1)}s"
        hud_izq = fuente_hud.render(
            f"HP: {int(partida['hp'])}/{partida['hp_max']}  |  LVL: {partida['nivel']} ({partida['xp']}/{partida['xp_siguiente']})  |  TIEMPO: {mins:02d}:{segs:02d}  |  DASH: {dash_txt}",
            True, (245, 245, 250)
        )
        pantalla.blit(hud_izq, (32, 22))

        pantalla.blit(sprites.corazon, (32, 56))
        sin_tag = "  |  SINERGIA" if sinergia_activa else ""
        mute_tag = "  |  [MUTE]" if audio.muteado else ""
        hud_cor = fuente_hud.render(
            f"RUN: x{partida['corazones_run']} (RED: {progreso['corazones']})  |  REGEN: +{partida['regen_hp']}/s  |  ROBO: +{partida['robo_vida']}{sin_tag}{mute_tag}",
            True, (255, 110, 130)
        )
        pantalla.blit(hud_cor, (64, 55))

        hud_der = fuente_hud.render(
            f"FLECHAS: {partida['cantidad_flechas']}/{MAX_FLECHAS} (Homing: {partida['flechas_homing']})  |  ATK: {dano_efectivo}  |  VEL: {partida['vel_jugador']}/{VEL_MAX_JUGADOR}",
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

            pantalla.blit(pygame.transform.scale(sprites.goblin, (84, 84)), (ANCHO // 2 - 42, 95))
            txt_g = fuente_titulo.render("MERCADER GOBLIN", True, (110, 225, 100))
            pantalla.blit(txt_g, txt_g.get_rect(center=(ANCHO // 2, 215)))

            pantalla.blit(pygame.transform.scale(sprites.corazon, (30, 28)), (ANCHO // 2 - 190, 260))
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
        resumen = fuente_boton.render(
            f"Puntaje: {partida['puntos']} PTS  |  Nivel: {partida['nivel']}  |  Corazones sumados a tu Red: {partida['corazones_run']}",
            True, (240, 240, 245)
        )
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 340)))
        pantalla.blit(resumen, resumen.get_rect(center=(ANCHO // 2, 440)))
        dibujar_boton(pantalla, "VOLVER AL MENU", btn_volver, pos_mouse)

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()