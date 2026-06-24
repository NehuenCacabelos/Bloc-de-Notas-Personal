# Bloc de Notas Profesional con Spring Boot y JavaFX

Esta es una aplicación de escritorio moderna y profesional construida con **JavaFX 17** y gestionada por **Spring Boot 3.x** utilizando **Maven**.

La aplicación ofrece una interfaz oscura premium (estilo Catppuccin Mocha) con opciones avanzadas de formateo y visualización, optimizada para el rendimiento y la facilidad de uso.

## Características Principales

- **Editor de Texto Responsivo**: Un `TextArea` que se expande automáticamente y aprovecha todo el espacio disponible al redimensionar la ventana.
- **Formato Global Dinámico**:
  - **Negrita (B)**: Alterna de forma interactiva el peso de la fuente del editor.
  - **Selector de Color**: Cambia el color del texto mediante un selector nativo.
  - **Zoom (+ / - / 100%)**: Aumenta o disminuye el tamaño de la fuente dinámicamente, con un botón rápido para restablecer al tamaño por defecto (100%).
- **Barra de Estado Profesional**: Muestra información en tiempo real sobre la cantidad de caracteres, el número de palabras y el porcentaje de zoom actual.
- **Guardado Nativo**: Diálogo `FileChooser` nativo del sistema operativo para guardar el contenido del bloc de notas en un archivo local `.txt` codificado en UTF-8.
- **Inyección de Dependencias**: Ciclo de vida y componentes gestionados en su totalidad por Spring Framework.

---

## Requisitos Previos

- **Java Development Kit (JDK)** versión 17 o superior (Java 26 es compatible y testeado).
- Maven no requiere instalación global, ya que el proyecto incluye un script envoltura (`mvnw.cmd`) configurado para usar el motor de Maven disponible localmente.

---

## Estructura del Proyecto

```text
├── pom.xml                     # Configuración de dependencias Maven
├── mvnw.cmd                    # Envoltura de Maven local
├── README.md                   # Instrucciones del proyecto
└── src
    └── main
        ├── java
        │   └── com
        │       └── notepad
        │           ├── SpringBootApp.java          # Entrada principal (Spring Boot)
        │           ├── NotepadFXApplication.java   # Ciclo de vida de JavaFX
        │           ├── event
        │           │   └── StageReadyEvent.java    # Evento de ventana lista
        │           ├── init
        │           │   └── PrimaryStageInitializer.java # Construcción del Stage principal
        │           └── ui
        │               └── NotepadController.java  # Lógica de componentes e interfaz
        └── resources
            └── styles
                └── style.css                       # Hoja de estilos CSS oscuros
```

---

## Instrucciones de Ejecución

Para iniciar la aplicación en tu entorno local, abre una terminal (PowerShell o CMD) en el directorio raíz del proyecto y ejecuta el siguiente comando:

```powershell
.\mvnw.cmd spring-boot:run
```

Si estás en un sistema Unix/Linux/macOS y tienes Maven instalado globalmente, puedes usar:

```bash
mvn spring-boot:run
```

## Atajos de Teclado del Editor
- **Ctrl + S**: Abre el diálogo nativo para guardar el archivo actual.
- **Ctrl + Q**: Cierra y sale limpiamente de la aplicación.
=======
# Bloc-de-Notas-Personal
Block de notas de uso personal
>>>>>>> 0c7f32f9afeb0a394df1f7d1984cf56238ff995a
