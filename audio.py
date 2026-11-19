import pygame
import math
import array

def _generar_tono(frecuencia, duracion_seg, volumen=0.14, barrido_fin=None, ruido=False):
    sample_rate = 22050
    n_samples = int(sample_rate * duracion_seg)
    buf = array.array("h")
    fase = 0.0

    for i in range(n_samples):
        t = i / sample_rate
        envolvente = 1.0 - (i / max(1, n_samples))
        if ruido:
            # Pseudo-ruido determinista ligero
            val = math.sin(i * 12.9898 + frecuencia) * 43758.5453
            onda = (val - math.floor(val)) * 2.0 - 1.0
        else:
            freq_act = frecuencia
            if barrido_fin is not None:
                freq_act = frecuencia + (barrido_fin - frecuencia) * (i / max(1, n_samples))
            fase += 2.0 * math.pi * freq_act / sample_rate
            onda = math.sin(fase)

        muestra = int(onda * envolvente * volumen * 32767)
        buf.append(max(-32767, min(32767, muestra)))

    return pygame.mixer.Sound(buffer=buf)

class GestorAudio:
    def __init__(self):
        self.activo = False
        self.muteado = False
        self.sonidos = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.activo = True
            self.sonidos = {
                "disparo": _generar_tono(520, 0.05, volumen=0.06, barrido_fin=260),
                "golpe": _generar_tono(190, 0.06, volumen=0.08, barrido_fin=95),
                "pickup": _generar_tono(680, 0.07, volumen=0.08, barrido_fin=980),
                "dash": _generar_tono(280, 0.11, volumen=0.10, barrido_fin=620),
                "cofre": _generar_tono(440, 0.18, volumen=0.11, barrido_fin=880),
                "jefe": _generar_tono(110, 0.35, volumen=0.14, barrido_fin=55, ruido=True),
            }
        except pygame.error:
            self.activo = False

    def tocar(self, nombre):
        if self.activo and not self.muteado and nombre in self.sonidos:
            self.sonidos[nombre].play()

    def alternar_mute(self):
        self.muteado = not self.muteado
        return self.muteado