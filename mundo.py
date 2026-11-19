import pygame
import random
import math

TAM_BALDOSA = 96
TAM_CHUNK = 768

def generar_datos_chunk(cx, cy, semilla_mundo):
    rng = random.Random(hash((semilla_mundo, cx, cy)))
    dist_origen = math.hypot(cx, cy)

    if dist_origen < 3:
        bioma = "patio"
    elif dist_origen < 7:
        bioma = "bosque"
    else:
        bioma = "abismo"

    decoraciones = []
    for _ in range(rng.randint(3, 7)):
        dx = cx * TAM_CHUNK + rng.randint(40, TAM_CHUNK - 40)
        dy = cy * TAM_CHUNK + rng.randint(40, TAM_CHUNK - 40)
        tipo_dec = rng.choice(["grieta", "musgo", "runa"])
        decoraciones.append((dx, dy, tipo_dec, rng.randint(4, 12)))

    altar = None
    if (cx != 0 or cy != 0) and rng.random() < 0.24:
        ax = cx * TAM_CHUNK + rng.randint(150, TAM_CHUNK - 150)
        ay = cy * TAM_CHUNK + rng.randint(150, TAM_CHUNK - 150)
        altar = {"x": ax, "y": ay, "usado": False}

    cofre = None
    if (cx != 0 or cy != 0) and rng.random() < 0.30:
        kx = cx * TAM_CHUNK + rng.randint(120, TAM_CHUNK - 120)
        ky = cy * TAM_CHUNK + rng.randint(120, TAM_CHUNK - 120)
        cofre = {"x": kx, "y": ky}

    return {"bioma": bioma, "decoraciones": decoraciones, "altar": altar, "cofre": cofre}

def obtener_chunk(partida, cx, cy):
    clave = (cx, cy)
    if clave not in partida["chunks"]:
        chunk = generar_datos_chunk(cx, cy, partida["semilla"])
        partida["chunks"][clave] = chunk
        if chunk["cofre"] is not None:
            partida["cofres"].append({"x": float(chunk["cofre"]["x"]), "y": float(chunk["cofre"]["y"])})
    return partida["chunks"][clave]

def dibujar_mundo_infinito(superficie, partida, sprites, ancho, alto):
    cam_x = partida["wx"] - ancho // 2
    cam_y = partida["wy"] - alto // 2

    col_ini = int(math.floor(cam_x / TAM_BALDOSA)) - 1
    col_fin = int(math.ceil((cam_x + ancho) / TAM_BALDOSA)) + 1
    fila_ini = int(math.floor(cam_y / TAM_BALDOSA)) - 1
    fila_fin = int(math.ceil((cam_y + alto) / TAM_BALDOSA)) + 1

    for col in range(col_ini, col_fin):
        for fila in range(fila_ini, fila_fin):
            wx = col * TAM_BALDOSA
            wy = fila * TAM_BALDOSA
            sx = int(wx - cam_x)
            sy = int(wy - cam_y)

            cx = math.floor(wx / TAM_CHUNK)
            cy = math.floor(wy / TAM_CHUNK)
            chunk = obtener_chunk(partida, cx, cy)

            h = ((col * 73856093) ^ (fila * 19349663)) & 7
            if chunk["bioma"] == "patio":
                base = (22 + h, 25 + h, 34 + h)
            elif chunk["bioma"] == "bosque":
                base = (20 + h, 30 + h, 25 + h)
            else:
                base = (32 + h, 20 + h, 26 + h)

            pygame.draw.rect(superficie, base, (sx + 1, sy + 1, TAM_BALDOSA - 2, TAM_BALDOSA - 2), border_radius=5)

    c_x_ini = math.floor(cam_x / TAM_CHUNK)
    c_x_fin = math.floor((cam_x + ancho) / TAM_CHUNK)
    c_y_ini = math.floor(cam_y / TAM_CHUNK)
    c_y_fin = math.floor((cam_y + alto) / TAM_CHUNK)

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
                superficie.blit(sprites.altar, (sx - 27, sy - 27))

def dibujar_minimapa(superficie, partida, ancho, alto, fuente_nodo):
    radio_radar = 105
    cx_r = ancho - radio_radar - 32
    cy_r = alto - radio_radar - 32
    escala = 0.045  # ~2300 px de radio real en el radar

    radar = pygame.Surface((radio_radar * 2, radio_radar * 2), pygame.SRCALPHA)
    pygame.draw.circle(radar, (12, 15, 22, 195), (radio_radar, radio_radar), radio_radar)
    pygame.draw.circle(radar, (110, 120, 145, 160), (radio_radar, radio_radar), radio_radar, width=2)
    pygame.draw.circle(radar, (110, 120, 145, 65), (radio_radar, radio_radar), radio_radar // 2, width=1)

    # Origen (0, 0)
    ox = int(radio_radar + (0.0 - partida["wx"]) * escala)
    oy = int(radio_radar + (0.0 - partida["wy"]) * escala)
    if math.hypot(ox - radio_radar, oy - radio_radar) <= radio_radar - 4:
        pygame.draw.circle(radar, (140, 160, 200), (ox, oy), 3)

    # Cofres cercanos
    for c in partida["cofres"]:
        px = int(radio_radar + (c["x"] - partida["wx"]) * escala)
        py = int(radio_radar + (c["y"] - partida["wy"]) * escala)
        if math.hypot(px - radio_radar, py - radio_radar) <= radio_radar - 4:
            pygame.draw.circle(radar, (90, 215, 255), (px, py), 4)

    # Goblin mercader
    if partida["goblin"] is not None:
        gx = int(radio_radar + (partida["goblin"]["x"] - partida["wx"]) * escala)
        gy = int(radio_radar + (partida["goblin"]["y"] - partida["wy"]) * escala)
        ang = math.atan2(gy - radio_radar, gx - radio_radar)
        dist = min(radio_radar - 8, math.hypot(gx - radio_radar, gy - radio_radar))
        pygame.draw.circle(radar, (255, 215, 65), (int(radio_radar + math.cos(ang) * dist), int(radio_radar + math.sin(ang) * dist)), 5)

    # Jefe activo
    if partida["jefe"] is not None:
        jx = int(radio_radar + (partida["jefe"]["x"] - partida["wx"]) * escala)
        jy = int(radio_radar + (partida["jefe"]["y"] - partida["wy"]) * escala)
        ang = math.atan2(jy - radio_radar, jx - radio_radar)
        dist = min(radio_radar - 8, math.hypot(jx - radio_radar, jy - radio_radar))
        pygame.draw.circle(radar, (255, 45, 70), (int(radio_radar + math.cos(ang) * dist), int(radio_radar + math.sin(ang) * dist)), 6)

    # Jugador al centro del radar
    pygame.draw.circle(radar, (90, 235, 130), (radio_radar, radio_radar), 4)
    superficie.blit(radar, (cx_r - radio_radar, cy_r - radio_radar))

    lbl = fuente_nodo.render("RADAR", True, (185, 195, 215))
    superficie.blit(lbl, lbl.get_rect(center=(cx_r, cy_r - radio_radar - 12)))