import cv2
import mediapipe as mp
import webbrowser
import pyautogui
import time
import platform, os, subprocess

# Inicializar MediaPipe
mp_manos = mp.solutions.hands
mp_dibujo = mp.solutions.drawing_utils

# Detectar sistema operativo
SISTEMA_OPERATIVO = platform.system()  # 'Windows', 'Linux', 'Darwin' (macOS)

# Constantes
DELAY_SEGUNDOS = 3
CONFIANZA_MINIMA_DETECCION = 0.7
CONFIANZA_MINIMA_SEGUIMIENTO = 0.7
UMBRAL_SEPARACION_DEDOS = 0.05


class ManejadorSenales:
    """Detecta diferentes gestos de manos"""
    
    def __init__(self):
        # Índices de puntos de referencia
        self.PUNTAS = {'pulgar': 4, 'indice': 8, 'medio': 12, 'anular': 16, 'menique': 20}
        self.BASES = {'indice': 5, 'medio': 9, 'anular': 13, 'menique': 17}
    
    def _esta_dedo_extendido(self, puntos_mano, nombre_dedo):
        """Verifica si un dedo está extendido"""
        punta = puntos_mano.landmark[self.PUNTAS[nombre_dedo]]
        base = puntos_mano.landmark[self.BASES[nombre_dedo]]
        return punta.y < base.y
    
    def _esta_dedo_doblado(self, puntos_mano, nombre_dedo):
        """Verifica si un dedo está doblado"""
        return not self._esta_dedo_extendido(puntos_mano, nombre_dedo)
    
    def es_paz(self, puntos_mano):
        """Detecta señal de paz (✌️)"""
        indice_extendido = self._esta_dedo_extendido(puntos_mano, 'indice')
        medio_extendido = self._esta_dedo_extendido(puntos_mano, 'medio')
        anular_doblado = self._esta_dedo_doblado(puntos_mano, 'anular')
        menique_doblado = self._esta_dedo_doblado(puntos_mano, 'menique')
        
        # Verificar separación entre dedos
        indice = puntos_mano.landmark[self.PUNTAS['indice']]
        medio = puntos_mano.landmark[self.PUNTAS['medio']]
        distancia_dedos = abs(indice.x - medio.x)
        separados = distancia_dedos > UMBRAL_SEPARACION_DEDOS
        
        return (indice_extendido and medio_extendido and 
                anular_doblado and menique_doblado and separados)
    
    def mano_cerrada(self, puntos_mano):
        """Detecta puño cerrado (✊)"""
        return all(self._esta_dedo_doblado(puntos_mano, dedo) 
                   for dedo in ['indice', 'medio', 'anular', 'menique'])
    
    def indice_levantado(self, puntos_mano):
        indice_extendido = self._esta_dedo_extendido(puntos_mano, 'indice')
        medio_doblado = self._esta_dedo_doblado(puntos_mano,'medio')
        anular_doblado = self._esta_dedo_doblado(puntos_mano,'anular')
        menique_doblado = self._esta_dedo_doblado(puntos_mano,'menique')

        pulgar = puntos_mano.landmark[self.PUNTAS['pulgar']].y > puntos_mano.landmark[self.PUNTAS['indice']].y

        return (indice_extendido and medio_doblado and anular_doblado and menique_doblado and pulgar)
    
    def rock(self, puntos_mano):
        """Detecta seña de Rock"""
        # Todos los dedos doblados excepto el pulgar
        dedos_doblados = all(self._esta_dedo_doblado(puntos_mano, dedo) 
                            for dedo in ['medio', 'anular'])
        
        return dedos_doblados
    

class FuncionesSenal:
    """Ejecuta funciones asociadas a cada gesto"""
    
    def __init__(self):
        self.alt_tab_activo = False
        self.tiempo_ultimo_tab = 0
        self.TIEMPO_MANTENER_ALT = 1.0  # Segundos para mantener Alt presionada
        self.ventana_maximizada = False  # Estado inicial (asumimos maximizada)
        self.sistema_operativo = SISTEMA_OPERATIVO
        
    def funcion_es_paz(self):
        """Abre Google en el navegador"""
        webbrowser.open("https://www.google.com")
    
    def funcion_mano_cerrada(self):
        """Cambia entre ventanas manteniendo Alt+Tab activo"""
        tiempo_actual = time.time()
        
        # Si es la primera vez o han pasado más de 2 segundos, iniciar Alt+Tab
        if not self.alt_tab_activo or (tiempo_actual - self.tiempo_ultimo_tab > self.TIEMPO_MANTENER_ALT):
            pyautogui.keyDown('alt')
            pyautogui.press('tab')
            self.alt_tab_activo = True
        else:
            # Si Alt+Tab está activo, solo presionar Tab para seguir navegando
            pyautogui.press('tab')
        
        self.tiempo_ultimo_tab = tiempo_actual
    
    def _maximizar_ventana_linux(self):
        """Maximiza la ventana activa en Linux"""
        try:
            result = subprocess.run(['xdotool', 'getactivewindow'], 
                                  capture_output=True, text=True, timeout=1)
            window_id = result.stdout.strip()
            
            if window_id:
                subprocess.run(['wmctrl', '-i', '-r', window_id, '-b', 
                              'add,maximized_vert,maximized_horz'], timeout=1)
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Error al maximizar (Linux): {e}")
            return False
        return False
    
    def _minimizar_ventana_linux(self):
        """Minimiza la ventana activa en Linux"""
        try:
            result = subprocess.run(['xdotool', 'getactivewindow'], 
                                  capture_output=True, text=True, timeout=1)
            window_id = result.stdout.strip()
            
            if window_id:
                subprocess.run(['xdotool', 'windowminimize', window_id], timeout=1)
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Error al minimizar (Linux): {e}")
            return False
        return False
    
    def _maximizar_ventana_windows(self):
        """Maximiza la ventana activa en Windows"""
        try:
            pyautogui.hotkey('win', 'up')
            return True
        except Exception as e:
            print(f"Error al maximizar (Windows): {e}")
            return False
    
    def _minimizar_ventana_windows(self):
        """Minimiza la ventana activa en Windows"""
        try:
            pyautogui.hotkey('win', 'down')
            pyautogui.hotkey('win', 'down')  # Doble para asegurar minimizar
            return True
        except Exception as e:
            print(f"Error al minimizar (Windows): {e}")
            return False
    
    def funcion_rock(self):
        """Maximiza o minimiza la ventana actual según el sistema operativo"""
        exito = False
        
        if self.sistema_operativo == "Linux":
            if self.ventana_maximizada:
                exito = self._minimizar_ventana_linux()
            else:
                exito = self._maximizar_ventana_linux()
        
        elif self.sistema_operativo == "Windows":
            if self.ventana_maximizada:
                exito = self._minimizar_ventana_windows()
            else:
                exito = self._maximizar_ventana_windows()

        # Solo cambiar el estado si la operación fue exitosa
        if exito:
            self.ventana_maximizada = not self.ventana_maximizada

    def liberar_alt_tab(self):
        """Libera la tecla Alt si ha pasado suficiente tiempo"""
        if self.alt_tab_activo:
            tiempo_actual = time.time()
            if tiempo_actual - self.tiempo_ultimo_tab > self.TIEMPO_MANTENER_ALT:
                pyautogui.keyUp('alt')
                self.alt_tab_activo = False
    
    def funcion_indice(self):
        """Abre el explorador de archivos del sistema operativo."""
        ruta = os.path.expanduser("~")
        
        # Verificar que la ruta existe
        if not os.path.exists(ruta):
            print(f"Error: La ruta '{ruta}' no existe")
            return
        
        sistema = platform.system()
        
        try:
            if sistema == "Windows":
                # En Windows usar explorer
                os.startfile(ruta)
                
            elif sistema == "Linux":
                # En Linux usar xdg-open (funciona con la mayoría de entornos de escritorio)
                subprocess.run(["xdg-open", ruta], check=True)

            print(f"Explorador abierto en: {ruta}")
            
        except Exception as e:
            print(f"Error al abrir el explorador: {e}")


class DetectorGestos:
    """Clase principal para detectar y ejecutar gestos"""
    
    def __init__(self):
        self.manejador_senales = ManejadorSenales()
        self.funciones_senal = FuncionesSenal()
        self.ultimo_tiempo_ejecucion = {}
        
        # Mapeo de gestos a funciones y mensajes
        self.gestos = {
            'paz': {
                'detector': self.manejador_senales.es_paz,
                'funcion': self.funciones_senal.funcion_es_paz,
                'mensaje': 'Abriendo el navegador'
            },
            'mano_cerrada': {
                'detector': self.manejador_senales.mano_cerrada,
                'funcion': self.funciones_senal.funcion_mano_cerrada,
                'mensaje': 'Navegando ventanas'
            },
            'indice_levantado': {
                'detector': self.manejador_senales.indice_levantado,
                'funcion': self.funciones_senal.funcion_indice,
                'mensaje': 'Abriendo explorador'
            },
            'rock': {
                'detector': self.manejador_senales.rock,
                'funcion': self.funciones_senal.funcion_rock,
                'mensaje': 'Maximizar/Minimizar ventana'
            }
        }
    
    def puede_ejecutar(self, nombre_gesto):
        """Verifica si ha pasado suficiente tiempo para ejecutar el gesto"""
        tiempo_actual = time.time()
        ultimo_tiempo = self.ultimo_tiempo_ejecucion.get(nombre_gesto, 0)
        return tiempo_actual - ultimo_tiempo >= DELAY_SEGUNDOS
    
    def obtener_tiempo_restante(self, nombre_gesto):
        """Obtiene el tiempo restante de espera para un gesto"""
        tiempo_actual = time.time()
        ultimo_tiempo = self.ultimo_tiempo_ejecucion.get(nombre_gesto, 0)
        return int(DELAY_SEGUNDOS - (tiempo_actual - ultimo_tiempo))
    
    def procesar_gesto(self, puntos_mano, frame):
        """Procesa y ejecuta el gesto detectado"""
        gesto_detectado = False
        
        for nombre_gesto, config in self.gestos.items():
            if config['detector'](puntos_mano):
                gesto_detectado = True
                if self.puede_ejecutar(nombre_gesto):
                    cv2.putText(frame, config['mensaje'], (10, 70),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                    config['funcion']()
                    self.ultimo_tiempo_ejecucion[nombre_gesto] = time.time()
                else:
                    tiempo_restante = self.obtener_tiempo_restante(nombre_gesto)
                    cv2.putText(frame, f"Espera {tiempo_restante}s", (10, 70),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 165, 0), 3)
                return True
        
        # Si no hay gesto detectado, liberar Alt+Tab si estaba activo
        if not gesto_detectado:
            self.funciones_senal.liberar_alt_tab()
        
        return False


def verificar_dependencias_linux():
    """Verifica que las dependencias necesarias estén instaladas en Linux"""
    if SISTEMA_OPERATIVO != "Linux":
        return True
    
    herramientas_faltantes = []
    
    try:
        subprocess.run(['wmctrl', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        herramientas_faltantes.append('wmctrl')
    
    try:
        subprocess.run(['xdotool', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        herramientas_faltantes.append('xdotool')
    
    if herramientas_faltantes:
        print("⚠️  ADVERTENCIA: Faltan dependencias para controlar ventanas en Linux:")
        print(f"   Instala: sudo apt install {' '.join(herramientas_faltantes)}")
        print("   El gesto 'rock' no funcionará hasta instalar estas herramientas.\n")
        return False
    
    return True


def main():
    """Función principal"""
    print(f"Sistema operativo detectado: {SISTEMA_OPERATIVO}")
    verificar_dependencias_linux()
    
    # Iniciar cámara
    captura = cv2.VideoCapture(0)
    
    if not captura.isOpened():
        print("Error: No se puede abrir la cámara")
        return
    
    detector = DetectorGestos()
    
    print("\nPresiona 'q' para salir")
    with mp_manos.Hands(
        min_detection_confidence=CONFIANZA_MINIMA_DETECCION,
        min_tracking_confidence=CONFIANZA_MINIMA_SEGUIMIENTO
    ) as manos:
        
        while True:
            ret, frame = captura.read()
            
            if not ret:
                print("No se puede recibir frame. Saliendo...")
                break
            
            # Voltear frame horizontalmente (efecto espejo)
            frame = cv2.flip(frame, 1)
            
            # Convertir a RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Procesar frame
            resultados = manos.process(frame_rgb)
            
            # Procesar manos detectadas
            if resultados.multi_hand_landmarks:
                for puntos_mano in resultados.multi_hand_landmarks:
                    # Dibujar puntos y conexiones
                    mp_dibujo.draw_landmarks(
                        frame,
                        puntos_mano,
                        mp_manos.HAND_CONNECTIONS
                    )
                    
                    # Detectar y procesar gestos
                    detector.procesar_gesto(puntos_mano, frame)
                
                # Mostrar estado
                cv2.putText(frame, "Mano detectada", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            else:
                # Si no hay manos, liberar Alt+Tab
                detector.funciones_senal.liberar_alt_tab()
                cv2.putText(frame, "No hay manos", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Mostrar frame
            cv2.imshow('Detector de Senas', frame)
            
            # Salir con 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    # Limpiar recursos
    captura.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()