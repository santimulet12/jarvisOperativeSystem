# Detector de Gestos con Manos 👋

Sistema de reconocimiento de gestos de manos en tiempo real que permite controlar tu computadora mediante señas capturadas por la cámara web.

## 🎯 Características

Este programa utiliza visión por computadora para detectar gestos de manos y ejecutar acciones en tu sistema operativo:

- **Señal de Paz (✌️)**: Abre Google en tu navegador predeterminado
- **Puño Cerrado (✊)**: Navega entre ventanas abiertas (Alt+Tab)
- **Índice Levantado (☝️)**: Abre el explorador de archivos

## 📋 Requisitos

### Dependencias

```bash
pip install opencv-python mediapipe pyautogui
```

### Librerías necesarias:
- **OpenCV (cv2)**: Procesamiento de video y visualización
- **MediaPipe**: Detección y seguimiento de manos
- **PyAutoGUI**: Automatización de teclado
- **webbrowser**: Apertura de URLs
- **os, platform, subprocess**: Interacción con el sistema operativo

### Requisitos de hardware:
- Cámara web funcional
- Sistema operativo: Windows o Linux

## 🚀 Uso

### Ejecutar el programa:

```bash
python manos.py
```

### Controles:
- Presiona **'q'** para salir del programa

### Gestos reconocidos:

1. **Señal de Paz**: Extiende los dedos índice y medio manteniendo los demás doblados
2. **Puño Cerrado**: Cierra todos los dedos en un puño
3. **Índice Levantado**: Extiende solo el dedo índice con el pulgar hacia abajo

## ⚙️ Configuración

Puedes ajustar estos parámetros en el código:

```python
DELAY_SEGUNDOS = 3  # Tiempo de espera entre ejecuciones del mismo gesto
CONFIANZA_MINIMA_DETECCION = 0.7  # Precisión mínima para detectar manos
CONFIANZA_MINIMA_SEGUIMIENTO = 0.7  # Precisión mínima para seguir manos
UMBRAL_SEPARACION_DEDOS = 0.05  # Distancia mínima entre dedos para paz
```

## 🏗️ Arquitectura del Código

### Clases principales:

#### `ManejadorSenales`
Detecta los diferentes gestos de manos analizando las posiciones de los puntos de referencia de MediaPipe.

**Métodos principales:**
- `es_paz()`: Detecta señal de paz
- `mano_cerrada()`: Detecta puño cerrado
- `indice_levantado()`: Detecta índice extendido

#### `FuncionesSenal`
Ejecuta las acciones asociadas a cada gesto detectado.

**Métodos principales:**
- `funcion_es_paz()`: Abre el navegador
- `funcion_mano_cerrada()`: Gestiona Alt+Tab
- `funcion_indice()`: Abre explorador de archivos

#### `DetectorGestos`
Clase principal que coordina la detección y ejecución de gestos, evitando ejecuciones repetidas mediante un sistema de cooldown.

## 🔧 Funcionamiento Técnico

1. **Captura de video**: Obtiene frames de la cámara web en tiempo real
2. **Procesamiento**: Convierte cada frame a RGB para MediaPipe
3. **Detección**: MediaPipe identifica puntos de referencia de las manos
4. **Análisis**: Evalúa la posición de cada dedo para reconocer gestos
5. **Ejecución**: Ejecuta la acción correspondiente si ha pasado el tiempo de espera
6. **Visualización**: Muestra feedback visual en pantalla

## 🎨 Interfaz Visual

El programa muestra:
- Video en tiempo real con efecto espejo
- Puntos y conexiones de las manos detectadas
- Estado actual: "Mano detectada" o "No hay manos"
- Mensajes de acción cuando se ejecuta un gesto
- Temporizador de cooldown cuando un gesto está en espera

## ⚠️ Notas Importantes

- El programa requiere permisos de acceso a la cámara
- PyAutoGUI puede requerir permisos especiales en algunos sistemas
- El delay de 3 segundos evita ejecuciones accidentales repetidas
- El sistema mantiene Alt presionado durante 1 segundo para facilitar la navegación entre ventanas
- Compatible con Windows y Linux (macOS no incluido en este momento)

## 🐛 Solución de Problemas

**La cámara no se abre:**
- Verifica que la cámara no esté siendo usada por otra aplicación
- Prueba cambiar el índice de cámara: `cv2.VideoCapture(1)` en lugar de `(0)`

**Los gestos no se detectan:**
- Asegúrate de tener buena iluminación
- Mantén la mano visible y enfocada
- Ajusta los valores de confianza mínima

**PyAutoGUI no funciona:**
- En Linux, puede requerir instalar: `sudo apt-get install python3-xlib`

## 📄 Licencia

Este proyecto está disponible para uso educativo y personal.

## 🤝 Contribuciones

Las mejoras y nuevos gestos son bienvenidos. Algunas ideas:
- Agregar más gestos (pulgar arriba, OK, etc.)
- Soporte para macOS
- Acciones personalizables por el usuario
- Interfaz gráfica de configuración
