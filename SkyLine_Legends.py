import pygame
import random
import sys
import os

from modo_carrera import iniciar_modo_carrera
# Inicializar pygame
pygame.init()

pygame.mixer.init()
motor_sonido = pygame.mixer.Sound("nissan_skyline.wav")
motor_sonido.set_volume(0.3)  # Volumen de 0.0 a 1.0
choque_sonido = pygame.mixer.Sound("choque.wav")
choque_sonido.set_volume(0.5)  # Puedes ajustar el volumen
# Constantes
ANCHO, ALTO = 1366, 768
FPS = 60
VELOCIDAD_JUEGO = 12
VELOCIDAD_OBSTACULOS = 12
ANCHO_AUTO = 50
ALTO_AUTO = 100

# Pantalla
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("SkyLine Legends")
clock = pygame.time.Clock()
# Configuración de carretera y paisajes
ancho_carretera = 600
x_carretera = ANCHO // 2 - ancho_carretera // 2
# Cargar imágenes de autos
auto_jugador_img = pygame.image.load("auto_jugador.png")
auto_jugador_img = pygame.transform.scale(auto_jugador_img, (ANCHO_AUTO, ALTO_AUTO))

auto_enemigo_img = pygame.image.load("auto_enemigo.png")
auto_enemigo_img = pygame.transform.scale(auto_enemigo_img, (ANCHO_AUTO, ALTO_AUTO))
# Cargar y escalar imágenes de carretera y paisaje
carretera_img = pygame.image.load("carretera.png")
carretera_img = pygame.transform.scale(carretera_img, (ancho_carretera, ALTO))

paisaje_izq = pygame.image.load("paisaje_izquierda.png")
paisaje_der = pygame.image.load("paisaje_derecha.png")
ancho_paisaje = (ANCHO - ancho_carretera) // 2

paisaje_izq = pygame.transform.scale(paisaje_izq, (ancho_paisaje, ALTO))
paisaje_der = pygame.transform.scale(paisaje_der, (ancho_paisaje, ALTO))

vida_img = pygame.image.load("vida.png")
vida_img = pygame.transform.scale(vida_img, (40, 40))
curacion_sonido = pygame.mixer.Sound("curacion.wav")
curacion_sonido.set_volume(0.5)

menu_fondo = pygame.image.load("menu_fondo.jpg")
menu_fondo = pygame.transform.scale(menu_fondo, (ANCHO, ALTO))

fondo_salida = pygame.image.load("fondo_salida.jpg")
fondo_salida = pygame.transform.scale(fondo_salida, (ANCHO, ALTO))
playlist = ["Blinded_in_Chains.mp3", "Hand_Of_Blood.mp3", "Nine_Thou.mp3"]
cancion_actual = 0
musica_pausada = False

# Clase Auto (Jugador)
class Auto:
    def __init__(self):
        self.x = x_carretera + ancho_carretera // 2 - ANCHO_AUTO // 2
        self.y = ALTO - ALTO_AUTO - 10
        self.velocidad = 7

    def mover(self, teclas):
        if teclas[pygame.K_LEFT] and self.x > x_carretera:
            self.x -= self.velocidad
        if teclas[pygame.K_RIGHT] and self.x < x_carretera + ancho_carretera - ANCHO_AUTO:
            self.x += self.velocidad

    def render(self):
        pantalla.blit(auto_jugador_img, (self.x, self.y))  ### NUEVO

    def hitbox(self):
        return pygame.Rect(self.x, self.y, ANCHO_AUTO, ALTO_AUTO)

# Clase Obstaculo (otros autos)
class Obstaculo:
    def __init__(self):
        self.x = random.randint(x_carretera, x_carretera + ancho_carretera - ANCHO_AUTO)
        self.y = -ALTO_AUTO
        self.velocidad = VELOCIDAD_OBSTACULOS

    def mover(self):
        self.y += self.velocidad

    def render(self):
        pantalla.blit(auto_enemigo_img, (self.x, self.y))  ### NUEVO

    def hitbox(self):
        return pygame.Rect(self.x, self.y, ANCHO_AUTO, ALTO_AUTO)

class VidaExtra:
    def __init__(self):
        self.x = random.randint(50, ANCHO - 50)
        self.y = -40
        self.velocidad = 3
        self.tiempo_creacion = pygame.time.get_ticks()

    def mover(self):
        self.y += self.velocidad

    def render(self):
        pantalla.blit(vida_img, (self.x, self.y))

    def hitbox(self):
        return pygame.Rect(self.x, self.y, 40, 40)
    
# Clase Juego 
class Juego:
    def __init__(self):
        self.auto = Auto()
        self.obstaculos = []
        self.contador_frames = 0
        self.puntos = 0
        self.jugando = True
        self.vida = 3
        self.max_vida = 3
        self.vida_extra = None
        self.tiempo_vida_extra = 0
# Scroll de fondo ### NUEVO
        self.y_fondo1 = 0
        self.y_fondo2 = -ALTO
        self.vel_fondo = VELOCIDAD_JUEGO
        self.vida = 3
        self.max_vida = 3
        self.vida_extra = None
        self.tiempo_vida_extra = 0
    def generar_obstaculos(self):
        if self.contador_frames % 60 == 0:  # Cada segundo
            self.obstaculos.append(Obstaculo())

    def detectar_colision(self):
        for obs in self.obstaculos:
            if self.auto.hitbox().colliderect(obs.hitbox()):
               choque_sonido.play()
               self.vida -= 1          # 💥 Pierde una vida
               self.obstaculos.remove(obs)  # Eliminar el obstáculo para evitar repetición

            if self.vida <= 0:
               self.jugando = False

    def actualizar(self):
        teclas = pygame.key.get_pressed()
        self.auto.mover(teclas)

        for obs in self.obstaculos:
            obs.mover()

        self.obstaculos = [o for o in self.obstaculos if o.y < ALTO]

        self.detectar_colision()
        self.contador_frames += 1
        self.puntos += 1
# Mover fondo ### NUEVO
        self.y_fondo1 += self.vel_fondo
        self.y_fondo2 += self.vel_fondo

# Resetear fondo para scroll infinito
        if self.y_fondo1 >= ALTO:
            self.y_fondo1 = -ALTO
        if self.y_fondo2 >= ALTO:
            self.y_fondo2 = -ALTO
# Aparecer vida extra cada 10 segundos
        if pygame.time.get_ticks() - self.tiempo_vida_extra > 10000 and self.vida_extra is None:
            self.vida_extra = VidaExtra()
            self.tiempo_vida_extra = pygame.time.get_ticks()
  
# Mover y eliminar si sale de pantalla
        if self.vida_extra:
            self.vida_extra.mover()
            if self.vida_extra.y > ALTO:
                self.vida_extra = None

# Recolección
        if self.vida_extra and self.auto.hitbox().colliderect(self.vida_extra.hitbox()):
           if self.vida < self.max_vida:
               self.vida += 1
           if 'curacion_sonido' in globals():
            curacion_sonido.play()
           self.vida_extra = None

    def render(self):
# Dibujar fondo (2 imágenes) ### NUEVO
        pantalla.blit(paisaje_izq, (0, self.y_fondo1))
        pantalla.blit(paisaje_izq, (0, self.y_fondo2))
        pantalla.blit(paisaje_der, (ANCHO - ancho_paisaje, self.y_fondo1))
        pantalla.blit(paisaje_der, (ANCHO - ancho_paisaje, self.y_fondo2))
        pantalla.blit(carretera_img, (x_carretera, self.y_fondo1))
        pantalla.blit(carretera_img, (x_carretera, self.y_fondo2))

# Dibujar jugador y obstáculos
        self.auto.render()
        for obs in self.obstaculos:
            obs.render()

# Dibujar vida extra si existe
        if self.vida_extra:
            self.vida_extra.render()

# Dibujar puntaje
        font = pygame.font.SysFont("Arial", 30)
        texto = font.render(f"Puntaje: {self.puntos}", True, (255, 255, 255))
        pantalla.blit(texto, (10, 10))
# Dibujar barra de vida ❤️
        barra_ancho = 200
        barra_altura = 20
        x = 10
        y = 50

# Fondo de la barra
        pygame.draw.rect(pantalla, (100, 100, 100), (x, y, barra_ancho, barra_altura))

# Vida actual
        vida_ancho = barra_ancho * (self.vida / self.max_vida)
        pygame.draw.rect(pantalla, (0, 255, 0), (x, y, vida_ancho, barra_altura))

# Borde
        pygame.draw.rect(pantalla, (255, 255, 255), (x, y, barra_ancho, barra_altura), 2)
        pygame.display.update()

def mostrar_menu_inicio():
    fuente_titulo = pygame.font.Font("Mostwasted.ttf", 160)
    fuente_opciones = pygame.font.Font("Mostwasted.ttf", 100)
    corriendo = True

    while corriendo:
        pantalla.blit(menu_fondo, (0, 0))  # Fondo con imagen
        titulo = fuente_titulo.render("SkyLine Legends", True, (255, 255, 255))
        jugar = fuente_opciones.render("JUGAR", True, (0, 255, 0))
        modo_carrera = fuente_opciones.render("MODO CARRERA", True, (0, 150, 255))
        salir = fuente_opciones.render("SALIR", True, (255, 0, 0))

        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 150))
        pantalla.blit(jugar, (ANCHO // 2 - jugar.get_width() // 2, 300))
        pantalla.blit(modo_carrera, (ANCHO // 2 - modo_carrera.get_width() // 2, 370))
        pantalla.blit(salir, (ANCHO // 2 - salir.get_width() // 2, 440))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if ANCHO // 2 - jugar.get_width() // 2 < x < ANCHO // 2 + jugar.get_width() // 2 and 300 < y < 370:
                    corriendo = False  # Salir del menú e iniciar juego
                if ANCHO // 2 - modo_carrera.get_width() // 2 < x < ANCHO // 2 + modo_carrera.get_width() // 2 and 370 < y < 440:
                    iniciar_modo_carrera()
                if ANCHO // 2 - salir.get_width() // 2 < x < ANCHO // 2 + salir.get_width() // 2 and 440 < y < 510:
                    pygame.quit()
                    sys.exit()

def mostrar_game_over(puntos):
    fuente_opciones = pygame.font.Font("Mostwasted.ttf", 100)
    corriendo = True

    while corriendo:
        pantalla.blit(fondo_salida, (0, 0))  # Fondo con imagen
        texto = fuente_opciones.render("GAME OVER", True, (255, 0, 0))
        puntaje = fuente_opciones.render(f"Puntaje: {puntos}", True, (255, 255, 255))
        reintentar = fuente_opciones.render("REINTENTAR", True, (0, 255, 0))
        salir = fuente_opciones.render("SALIR AL MENÚ", True, (255, 255, 0))
        
        pantalla.blit(texto, (ANCHO // 2 - texto.get_width() // 2, 200))
        pantalla.blit(puntaje, (ANCHO // 2 - puntaje.get_width() // 2, 300))
        pantalla.blit(reintentar, (ANCHO // 2 - reintentar.get_width() // 2, 430))
        pantalla.blit(salir, (ANCHO // 2 - salir.get_width() // 2, 510))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if ANCHO // 2 - reintentar.get_width() // 2 < x < ANCHO // 2 + reintentar.get_width() // 2 and 430 < y < 480:
                    return "reintentar"
                if ANCHO // 2 - salir.get_width() // 2 < x < ANCHO // 2 + salir.get_width() // 2 and 510 < y < 560:
                    return "menu"
def reproducir_intro():
    carpeta_frames = "frames"
    fps = 30  # Fotogramas por segundo

    # Cargar audio
    if os.path.exists("intro_audio.wav"):
        pygame.mixer.music.load("intro_audio.wav")
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play()
    
    # Obtener lista de frames en orden
    frames = sorted(
        [f for f in os.listdir(carpeta_frames) if f.endswith(".png")]
    )

    reloj = pygame.time.Clock()

    for frame in frames:
        ruta = os.path.join(carpeta_frames, frame)
        imagen = pygame.image.load(ruta)
        imagen = pygame.transform.scale(imagen, (ANCHO, ALTO))
        pantalla.blit(imagen, (0, 0))
        pygame.display.update()
        reloj.tick(fps)

    pygame.mixer.music.stop()
# Bucle principal
def main():
    global cancion_actual, musica_pausada
    reproducir_intro()  # 🔥 Intro antes del menú
    while True:
        mostrar_menu_inicio()
        pygame.mixer.music.load(playlist[cancion_actual])
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)

        motor_sonido.play(loops=-1)  # ▶️ Inicia motor
        juego = Juego() 
        while juego.jugando:
            clock.tick(FPS)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_n:
                        cancion_actual = (cancion_actual + 1) % len(playlist)
                        pygame.mixer.music.load(playlist[cancion_actual])
                        pygame.mixer.music.play(-1)

                    elif evento.key == pygame.K_b:
                        cancion_actual = (cancion_actual - 1) % len(playlist)
                        pygame.mixer.music.load(playlist[cancion_actual])
                        pygame.mixer.music.play(-1)

                    elif evento.key == pygame.K_p:
                        if musica_pausada:
                            pygame.mixer.music.unpause()
                            musica_pausada = False
                        else:
                            pygame.mixer.music.pause()
                            musica_pausada = True
            juego.generar_obstaculos()
            juego.actualizar()
            juego.render()
        motor_sonido.stop()  # 🛑 Apaga motor
        pygame.mixer.music.stop()
        # Cuando se pierde
        opcion = mostrar_game_over(juego.puntos)
        if opcion == "menu":
            continue  # Vuelve al menú
        elif opcion == "reintentar":
            pass  # Vuelve a iniciar el juego automáticamente
if __name__ == "__main__":
    main()
