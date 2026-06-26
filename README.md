# Suite Bloc de Notas en Modo Oscuro (Bloc de Notas)

Una suite moderna y premium de bloc de notas en modo oscuro con dos implementaciones, caracterizada por su diseño estético, interfaces responsivas y estilos personalizados.

Este repositorio contiene dos implementaciones:
1. **Versión de Python (`notepad.py`)**: Una aplicación de escritorio ligera construida con Tkinter, que incluye una barra superior al estilo de Windows 11, guardado automático de sesiones y un ejecutable independiente precompilado con un icono personalizado.
2. **Versión de Java (`src/main/`)**: Una robusta aplicación de escritorio gestionada por **Spring Boot 3.x** y construida con **JavaFX 17** y **Maven**.

---

## 🐍 Implementación en Python (Tkinter)

Un bloc de notas minimalista y veloz con modo oscuro, guardado de archivos personalizado y carga automática de la última sesión.

### Características Principales
- **Barra Superior de Nombre**: Campo de entrada de nombre con borrado automático del marcador de posición ("Sin nombre") y legibilidad mejorada.
- **Restaurar Sesión Automática**: Recuerda y reabre automáticamente el último archivo que estabas editando.
- **Icono Personalizado**: Incluye un icono premium con estética cyberpunk y texturas translúcidas.
- **Ejecutable Compilado**: Versión `.exe` independiente precompilada y disponible en la carpeta `dist/`.

### Inicio Rápido
Para ejecutar la versión de Python:
```powershell
py notepad.py
```
O simplemente haz doble clic en el ejecutable independiente en:
`dist/notepad.exe`

---

## ☕ Implementación en Java (Spring Boot y JavaFX)

Un editor de texto profesional de escritorio que utiliza la inyección de dependencias de Spring y estilos personalizados mediante CSS en JavaFX.

### Características Principales
- **Gestión del Ciclo de Vida de Spring**: La configuración y los controladores de la interfaz de usuario se gestionan por completo como componentes del contexto de Spring.
- **Barra de Estado Completa**: Muestra el nivel de zoom, la línea/columna del cursor en tiempo real, la codificación y el tipo de salto de línea (CRLF).
- **Formato Global Dinámico**: Zoom de fuente (+ / - / 100%), formato (negrita) y personalización del editor.

### Inicio Rápido
Para compilar y ejecutar la versión de Java usando el wrapper de Maven local:
```powershell
.\mvnw.cmd spring-boot:run
```

---

## ⌨️ Atajos de Teclado del Editor
- **Ctrl + N**: Nuevo archivo
- **Ctrl + O**: Abrir archivo
- **Ctrl + S**: Guardar archivo
- **Ctrl + Shift + S**: Guardar como
- **Ctrl + =** / **Ctrl + -**: Acercar / Alejar zoom
- **Ctrl + 0**: Restablecer zoom al 100%
- **Ctrl + Q**: Salir de la aplicación
