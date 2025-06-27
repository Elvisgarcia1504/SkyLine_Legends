import pygame
import random
import os
import json

pygame.init()
pygame.mixer.init()
motor_sonido = pygame.mixer.Sound("nissan_skyline.wav")
motor_sonido.set_volume(0.3)

choque_sonido = pygame.mixer.Sound("choque.wav")
choque_sonido.set_volume(0.5)

curacion_sonido = pygame.mixer.Sound("curacion.wav")
curacion_sonido.set_volume(0.5)
# Constantes
ANCHO, ALTO = 1366, 768
ANCHO_AUTO, ALTO_AUTO = 50, 100
BLANCO = (255, 255, 255)
MAX_NIVELES = 5

# Configuración de carretera y paisajes
ancho_carretera = 600
x_carretera = ANCHO // 2 - ancho_carretera // 2

# Recursos (se asume que ya existen en tu carpeta)
auto_jugador_img = pygame.transform.scale(pygame.image.load("auto_jugador.png"), (ANCHO_AUTO, ALTO_AUTO))
auto_enemigo_img = pygame.transform.scale(pygame.image.load("auto_enemigo.png"), (ANCHO_AUTO, ALTO_AUTO))
vida_img = pygame.transform.scale(pygame.image.load("vida.png"), (40, 40))

# Cargar y escalar imágenes de carretera y paisaje
carretera_img = pygame.transform.scale(pygame.image.load("carretera.png"), (ancho_carretera, ALTO))
paisaje_izq = pygame.image.load("paisaje_izquierda.png")
paisaje_der = pygame.image.load("paisaje_derecha.png")
ancho_paisaje = (ANCHO - ancho_carretera) // 2

paisaje_izq = pygame.transform.scale(paisaje_izq, (ancho_paisaje, ALTO))
paisaje_der = pygame.transform.scale(paisaje_der, (ancho_paisaje, ALTO))

# Clases básicas
class Auto:
    def __init__(self):
        self.x = ANCHO // 2 - ANCHO_AUTO // 2
        self.y = ALTO - ALTO_AUTO - 10
        self.velocidad = 7

    def mover(self, teclas):
        if teclas[pygame.K_LEFT] and self.x > x_carretera:
            self.x -= self.velocidad
        if teclas[pygame.K_RIGHT] and self.x < x_carretera + ancho_carretera - ANCHO_AUTO:
            self.x += self.velocidad

    def render(self, pantalla):
        pantalla.blit(auto_jugador_img, (self.x, self.y))

    def hitbox(self):
        return pygame.Rect(self.x, self.y, ANCHO_AUTO, ALTO_AUTO)

class Obstaculo:
    def __init__(self, velocidad):
        self.x = random.randint(x_carretera, x_carretera + ancho_carretera - ANCHO_AUTO)
        self.y = -ALTO_AUTO
        self.velocidad = velocidad

    def mover(self):
        self.y += self.velocidad

    def render(self, pantalla):
        pantalla.blit(auto_enemigo_img, (self.x, self.y))

    def hitbox(self):
        return pygame.Rect(self.x, self.y, ANCHO_AUTO, ALTO_AUTO)

class VidaExtra:
    def __init__(self):
        self.x = random.randint(50, ANCHO - 90)
        self.y = -40
        self.velocidad = 3
        self.tiempo_creacion = pygame.time.get_ticks()

    def mover(self):
        self.y += self.velocidad

    def render(self, pantalla):
        pantalla.blit(vida_img, (self.x, self.y))

    def hitbox(self):
        return pygame.Rect(self.x, self.y, 40, 40)

def configurar_nivel(nivel):
    velocidad = 10 + nivel * 3
    frecuencia = max(60 - nivel * 5, 20)  # Menos frames entre obstáculos
    return velocidad, frecuencia

def guardar_progreso(nivel):
    with open("progreso.json", "w") as f:
        json.dump({"nivel": nivel}, f)

def cargar_progreso():
    if os.path.exists("progreso.json"):
        with open("progreso.json", "r") as f:
            datos = json.load(f)
            return datos.get("nivel", 1)
    return 1

def mostrar_mensaje(texto, pantalla, fuente, espera=2000):
    pantalla.fill((0, 0, 0))
    mensaje = fuente.render(texto, True, BLANCO)
    pantalla.blit(mensaje, (ANCHO // 2 - mensaje.get_width() // 2, ALTO // 2))
    pygame.display.flip()
    pygame.time.delay(espera)

def jugar_nivel(pantalla, fuente, velocidad, frecuencia, nivel):
    reloj = pygame.time.Clock()
    jugador = Auto()
    obstaculos = []
    puntos = 0
    vidas = 3
    tiempo_nivel = 15000 + nivel * 5000  # 15 segundos por nivel
    vida_extra = None
    tiempo_vida_extra = pygame.time.get_ticks()
    max_vidas = 3  # o el número que uses como límite
    inicio = pygame.time.get_ticks()
    motor_sonido.play(loops=-1)
 # 🎯 Scroll de fondo
    y_fondo1 = 0
    y_fondo2 = -ALTO
    vel_fondo = velocidad  # o ajustalo si querés que el fondo sea más lento
    playlist = ["Blinded_in_Chains.mp3", "Hand_Of_Blood.mp3", "Nine_Thou.mp3"]
    cancion_actual = 0
    pygame.mixer.music.load(playlist[cancion_actual])
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)  # Bucle infinito
    musica_pausada = False
    corriendo = True
    while corriendo:
        reloj.tick(60)
        teclas = pygame.key.get_pressed()
    # Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                motor_sonido.stop()
                pygame.mixer.music.stop()
                return "salir"
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_n:  # ⏭ Siguiente canción
                    cancion_actual = (cancion_actual + 1) % len(playlist)
                    pygame.mixer.music.load(playlist[cancion_actual])
                    pygame.mixer.music.play(-1)

                elif evento.key == pygame.K_b:  # ⏮ Anterior canción
                    cancion_actual = (cancion_actual - 1) % len(playlist)
                    pygame.mixer.music.load(playlist[cancion_actual])
                    pygame.mixer.music.play(-1)

                elif evento.key == pygame.K_p:  # ⏸ Pausar o reanudar
                    if musica_pausada:
                       pygame.mixer.music.unpause()
                       musica_pausada = False
                    else:
                       pygame.mixer.music.pause()
                       musica_pausada = True

    # Mover fondo
        y_fondo1 += vel_fondo
        y_fondo2 += vel_fondo
        if y_fondo1 >= ALTO:
            y_fondo1 = -ALTO
        if y_fondo2 >= ALTO:
            y_fondo2 = -ALTO

    # Dibujar fondo (paisaje y carretera)
        pantalla.blit(paisaje_izq, (0, y_fondo1))
        pantalla.blit(paisaje_izq, (0, y_fondo2))
        pantalla.blit(paisaje_der, (ANCHO - ancho_paisaje, y_fondo1))
        pantalla.blit(paisaje_der, (ANCHO - ancho_paisaje, y_fondo2))
        pantalla.blit(carretera_img, (x_carretera, y_fondo1))
        pantalla.blit(carretera_img, (x_carretera, y_fondo2))

        jugador.mover(teclas)

        # Generar obstáculos
        if puntos % frecuencia == 0:
            obstaculos.append(Obstaculo(velocidad))

        for obs in obstaculos:
            obs.mover()
            if obs.y > ALTO:
                obstaculos.remove(obs)
# Aparecer vida extra cada 10 segundos
        if pygame.time.get_ticks() - tiempo_vida_extra > 10000 and vida_extra is None:
            vida_extra = VidaExtra()
            tiempo_vida_extra = pygame.time.get_ticks()

# Mover vida extra
        if vida_extra:
            vida_extra.mover()
            if vida_extra.y > ALTO:
                vida_extra = None

        # Colisiones
        for obs in obstaculos:
            if jugador.hitbox().colliderect(obs.hitbox()):
                choque_sonido.play()
                vidas -= 1
                obstaculos.remove(obs)
                if vidas <= 0:
                    motor_sonido.stop()
                    pygame.mixer.music.stop()
                    return "derrota"
# Recolectar vida extra
        if vida_extra and jugador.hitbox().colliderect(vida_extra.hitbox()):
            if vidas < max_vidas:
                vidas += 1
                curacion_sonido.play()
            vida_extra = None

        # Dibujar
        jugador.render(pantalla)
        for obs in obstaculos:
            obs.render(pantalla)

        texto = fuente.render(f"Nivel {nivel}  Vidas: {vidas}", True, BLANCO)
        pantalla.blit(texto, (20, 20))
        if vida_extra:
            vida_extra.render(pantalla)
        pygame.display.flip()
        puntos += 1

        if pygame.time.get_ticks() - inicio >= tiempo_nivel:
            motor_sonido.stop()
            pygame.mixer.music.stop()
            return "completado"

def iniciar_modo_carrera():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    fuente = pygame.font.Font("Mostwasted.ttf", 50)

    nivel_actual = cargar_progreso()
    corriendo = True

    while nivel_actual <= MAX_NIVELES and corriendo:
        mostrar_mensaje(f"Iniciando Nivel {nivel_actual}", pantalla, fuente)
        velocidad, frecuencia = configurar_nivel(nivel_actual)

        resultado = jugar_nivel(pantalla, fuente, velocidad, frecuencia, nivel_actual)

        if resultado == "completado":
            nivel_actual += 1
            guardar_progreso(nivel_actual)
        elif resultado == "derrota":
            mostrar_mensaje("¡Has perdido!", pantalla, fuente)
            break
        elif resultado == "salir":
            break

    if nivel_actual > MAX_NIVELES:
        mostrar_mensaje("¡Modo Carrera Completado!", pantalla, fuente)

    return