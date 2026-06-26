import sys
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import sqlite3

# Configuración de variables globales
current_file = None
font_size = 11
is_spanish = True
is_modified = False
DB_PATH = "ProjectRoot/src/tasks.db"

# ----------------- Funciones de Base de Datos y ProjectRoot -----------------

def init_project_root():
    """Crea la estructura de carpetas y archivos por defecto del proyecto e inicializa las tablas SQLite."""
    # Crear directorios del proyecto
    os.makedirs("ProjectRoot/docs", exist_ok=True)
    os.makedirs("ProjectRoot/src", exist_ok=True)
    
    # readme.md por defecto (se crea de fondo por si el usuario lo requiere)
    readme_path = "ProjectRoot/docs/readme.md"
    if not os.path.exists(readme_path):
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("# Documentación del Proyecto\n\n"
                    "Este es el archivo de documentación principal del bloc de notas.\n\n"
                    "## Flujo de Trabajo\n"
                    "A continuación se presenta el diagrama del sistema en formato de texto:\n\n"
                    "[Usuario] -> [Editor] -> [DB]\n\n"
                    "Puedes editar este texto y presionar 'Actualizar' o guardar el archivo para ver los cambios.\n")
                    
    # diagrama.svg por defecto
    svg_path = "ProjectRoot/docs/diagrama.svg"
    if not os.path.exists(svg_path):
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write('<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">\n'
                    '  <rect width="200" height="100" style="fill:rgb(30,30,30);stroke-width:3;stroke:rgb(60,60,60)" />\n'
                    '  <text x="50" y="55" fill="white" font-family="Segoe UI">Diagrama SVG</text>\n'
                    '</svg>\n')
                    
    # main.py por defecto
    main_py_path = "ProjectRoot/src/main.py"
    if not os.path.exists(main_py_path):
        with open(main_py_path, "w", encoding="utf-8") as f:
            f.write("# Archivo principal del proyecto\n\ndef main():\n    print('¡Hola desde main.py!')\n\nif __name__ == '__main__':\n    main()\n")
            
    # Inicialización de SQLite y Creación de Tablas
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session (
            last_file TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_PATH)

# ----------------- Funciones de Configuración de Sesión y Configs -----------------

def get_setting(key, default=None):
    """Recupera un ajuste de configuración de la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key, value):
    """Guarda o actualiza un ajuste de configuración en la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_last_session_file():
    """Recupera la ruta del último archivo guardado/abierto en la sesión anterior."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT last_file FROM session")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def update_session_file(file_path):
    """Registra la ruta del último archivo de sesión."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM session")
    if file_path:
        cursor.execute("INSERT INTO session (last_file) VALUES (?)", (os.path.abspath(file_path),))
    conn.commit()
    conn.close()

# ----------------- Función Principal de Ejecución -----------------

def main():
    global current_file, is_modified
    
    # Inicializar la estructura física de ProjectRoot
    init_project_root()
    
    root = tk.Tk()
    root.title("Sin nombre - Bloc de Notas")
    root.geometry("800x560")
    root.configure(bg="#131720")
    
    # Establecer icono de la ventana
    try:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
        if os.path.exists(icon_path):
            img_icon = tk.PhotoImage(file=icon_path)
            root.iconphoto(False, img_icon)
    except Exception:
        pass
    
    # Habilitar la barra de título oscura en Windows 10/11
    if sys.platform.startswith("win"):
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
            dark_mode = 1
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, ctypes.byref(ctypes.c_int(dark_mode)), ctypes.sizeof(ctypes.c_int(dark_mode))
            )
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 19, ctypes.byref(ctypes.c_int(dark_mode)), ctypes.sizeof(ctypes.c_int(dark_mode))
            )
        except Exception:
            pass

    # Configuración de estilos para scrollbars
    style = ttk.Style()
    style.theme_use('clam')
    
    # Scrollbar vertical azul sobrio
    style.configure(
        "Vertical.TScrollbar",
        gripcount=0,
        background="#323f53",
        troughcolor="#131720",
        bordercolor="#323f53",
        lightcolor="#323f53",
        darkcolor="#323f53",
        arrowcolor="#e2e8f0"
    )
    style.map(
        "Vertical.TScrollbar",
        background=[('pressed', '#4a7bb0'), ('active', '#475975')]
    )
    
    # Scrollbar horizontal azul sobrio
    style.configure(
        "Horizontal.TScrollbar",
        gripcount=0,
        background="#323f53",
        troughcolor="#131720",
        bordercolor="#323f53",
        lightcolor="#323f53",
        darkcolor="#323f53",
        arrowcolor="#e2e8f0"
    )
    style.map(
        "Horizontal.TScrollbar",
        background=[('pressed', '#4a7bb0'), ('active', '#475975')]
    )

    # --- BARRA SUPERIOR: Nombre de archivo uniforme ---
    top_bar = tk.Frame(root, bg="#131720", height=38)
    top_bar.pack(side=tk.TOP, fill=tk.X)
    
    top_border = tk.Frame(top_bar, bg="#273145", height=1)
    top_border.pack(side=tk.BOTTOM, fill=tk.X)
    
    file_lbl = tk.Label(top_bar, text=" FILE_NAME >", bg="#131720", fg="#4a7bb0", font=("Consolas", 10, "bold"))
    file_lbl.pack(side=tk.LEFT, padx=(15, 5), pady=5)
    
    filename_entry = tk.Entry(
        top_bar,
        bg="#1b212f",
        fg="#e2e8f0",
        insertbackground="#e2e8f0",
        bd=0,
        highlightthickness=1,
        highlightbackground="#273145",
        highlightcolor="#4a7bb0",
        font=("Consolas", 10)
    )
    # Pack filename_entry ocupando todo el ancho sin botón al lado
    filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 15), pady=5, ipady=3)
    
    # Inicializar con "Sin nombre"
    filename_entry.insert(0, "Sin nombre" if is_spanish else "Unnamed")
    filename_entry.config(fg="#94a3b8")
    
    def on_filename_focus_in(event):
        if filename_entry.get() in ("Sin nombre", "Unnamed", "Sin título", "Untitled"):
            filename_entry.delete(0, tk.END)
            filename_entry.config(fg="#e2e8f0")
            
    def on_filename_focus_out(event):
        if not filename_entry.get().strip():
            filename_entry.insert(0, "Sin nombre" if is_spanish else "Unnamed")
            filename_entry.config(fg="#94a3b8")
            
    filename_entry.bind("<FocusIn>", on_filename_focus_in)
    filename_entry.bind("<FocusOut>", on_filename_focus_out)

    def get_current_file():
        global current_file
        return current_file

    def set_filename_in_entry(filepath):
        filename_entry.delete(0, tk.END)
        filename_entry.config(fg="#e2e8f0")
        if filepath:
            filename_entry.insert(0, os.path.basename(filepath)) # Mostrar solo nombre de archivo estilo Google Docs
        else:
            filename_entry.insert(0, "Sin nombre" if is_spanish else "Unnamed")
            filename_entry.config(fg="#94a3b8")

    # --- Editor de Texto ---
    editor_frame = tk.Frame(root, bg="#131720")
    
    text_area = tk.Text(
        editor_frame,
        bg="#131720",
        fg="#e2e8f0",
        insertbackground="#e2e8f0",
        selectbackground="#273145",
        selectforeground="#e2e8f0",
        font=("Consolas", font_size),
        undo=True,
        maxundo=100,
        bd=0,
        highlightthickness=0,
        wrap="word"
    )
    
    scrollbar = ttk.Scrollbar(editor_frame, orient="vertical", command=text_area.yview)
    text_area.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=4)

    # 4. Barra de Estado (Status Bar) uniforme
    status_bar = tk.Frame(root, bg="#131720", height=24, bd=0)
    
    status_border = tk.Frame(status_bar, bg="#273145", height=1)
    status_border.pack(side=tk.TOP, fill=tk.X)

    status_content = tk.Frame(status_bar, bg="#131720")
    status_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=2)

    prompt_label = tk.Label(status_content, text="user@cyber-console:~/notepad$", bg="#131720", fg="#4a7bb0", font=("Consolas", 9, "bold"))
    prompt_label.pack(side=tk.LEFT)

    cursor_label = tk.Label(status_content, text="Ln 1, Col 1", bg="#131720", fg="#e2e8f0", font=("Consolas", 9))
    cursor_label.pack(side=tk.LEFT, padx=(10, 0))

    encoding_label = tk.Label(status_content, text="UTF-8", bg="#131720", fg="#e2e8f0", font=("Consolas", 9))
    encoding_label.pack(side=tk.RIGHT)

    sep2 = tk.Label(status_content, text="  |  ", bg="#131720", fg="#273145", font=("Consolas", 9))
    sep2.pack(side=tk.RIGHT)

    line_ending_label = tk.Label(status_content, text="LF", bg="#131720", fg="#e2e8f0", font=("Consolas", 9))
    line_ending_label.pack(side=tk.RIGHT)

    sep1 = tk.Label(status_content, text="  |  ", bg="#131720", fg="#273145", font=("Consolas", 9))
    sep1.pack(side=tk.RIGHT)

    zoom_label = tk.Label(status_content, text="100%", bg="#131720", fg="#e2e8f0", font=("Consolas", 9))
    zoom_label.pack(side=tk.RIGHT)

    # Empaquetado global
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    editor_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # 5. Funciones auxiliares y eventos del editor
    def update_cursor_pos(event=None):
        pos = text_area.index("insert")
        line, col = pos.split(".")
        cursor_label.config(text=f"Ln {line}, Col {int(col) + 1}")

    text_area.bind("<KeyRelease>", update_cursor_pos)
    text_area.bind("<ButtonRelease>", update_cursor_pos)

    # Rastrear modificaciones del archivo
    def on_text_modify(event=None):
        global is_modified
        if text_area.edit_modified():
            is_modified = True
            text_area.edit_modified(False) # Restablecer bandera para registrar futuros cambios

    text_area.bind("<<Modified>>", on_text_modify)

    def update_title():
        name = os.path.basename(current_file) if current_file else ("Sin nombre" if is_spanish else "Unnamed")
        app_name = "Bloc de Notas" if is_spanish else "Notepad"
        root.title(f"{name} - {app_name}")

    def update_font():
        font_style = ("Consolas", font_size, "bold" if is_bold.get() else "normal")
        text_area.config(font=font_style)
        zoom_pct = int((font_size / 11) * 100)
        zoom_label.config(text=f"{zoom_pct}%")

    def zoom_in(event=None):
        global font_size
        font_size = min(36, font_size + 1)
        update_font()
        return "break"

    def zoom_out(event=None):
        global font_size
        font_size = max(6, font_size - 1)
        update_font()
        return "break"

    def reset_zoom(event=None):
        global font_size
        font_size = 11
        update_font()
        return "break"

    def save_file(event=None):
        global current_file, is_modified
        path_input = filename_entry.get().strip()
        if not path_input or path_input in ("Sin nombre", "Unnamed", "Sin título", "Untitled"):
            save_file_as()
            return
            
        # Determinar ruta final basada en el directorio del archivo previo o la carpeta por defecto
        if current_file:
            directory = os.path.dirname(current_file)
            file_path = os.path.abspath(os.path.join(directory, path_input))
        else:
            default_dir = get_setting("default_save_dir", os.path.abspath("ProjectRoot/docs"))
            os.makedirs(default_dir, exist_ok=True)
            file_path = os.path.abspath(os.path.join(default_dir, path_input))
            
        try:
            content = text_area.get("1.0", tk.END)[:-1]
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            current_file = file_path
            set_filename_in_entry(file_path)
            update_title()
            update_session_file(file_path)
            
            # Marcar archivo como guardado sin modificaciones pendientes
            text_area.edit_modified(False)
            is_modified = False
        except Exception as e:
            err_title = "Error al guardar" if is_spanish else "Error saving file"
            messagebox.showerror(err_title, str(e))

    def save_file_as(event=None):
        global current_file, is_modified
        title = "Guardar como..." if is_spanish else "Save As..."
        file_types = [("Archivos de texto (*.txt)", "*.txt"), ("Todos los archivos", "*.*")]
        
        path_input = filename_entry.get().strip()
        sugg_name = path_input if path_input not in ("Sin nombre", "Unnamed", "Sin título", "Untitled") else "notas.txt"
        
        file_path = filedialog.asksaveasfilename(title=title, filetypes=file_types, defaultextension=".txt", initialfile=sugg_name)
        if file_path:
            set_filename_in_entry(file_path)
            save_file()

    def new_file(event=None):
        global current_file, is_modified
        text_area.config(state=tk.NORMAL)
        text_area.delete("1.0", tk.END)
        current_file = None
        
        set_filename_in_entry(None)
        update_title()
        update_cursor_pos()
        update_session_file(None)
        
        # Limpiar banderas de modificación
        text_area.edit_modified(False)
        is_modified = False

    def open_file(event=None):
        global current_file, is_modified
        title = "Abrir archivo" if is_spanish else "Open file"
        file_types = [("Archivos compatibles (*.txt;*.md;*.py)", "*.txt;*.md;*.py"), ("Todos los archivos", "*.*")]
        file_path = filedialog.askopenfilename(title=title, filetypes=file_types)
        if file_path:
            try:
                text_area.config(state=tk.NORMAL)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                text_area.delete("1.0", tk.END)
                text_area.insert("1.0", content)
                current_file = file_path
                set_filename_in_entry(file_path)
                update_title()
                update_cursor_pos()
                update_session_file(file_path)
                
                # Limpiar banderas de modificación
                text_area.edit_modified(False)
                is_modified = False
            except Exception as e:
                err_title = "Error al abrir" if is_spanish else "Error opening file"
                messagebox.showerror(err_title, str(e))

    def set_default_save_dir():
        """Abre un cuadro de diálogo para seleccionar la carpeta de guardado por defecto."""
        current_dir = get_setting("default_save_dir", os.path.abspath("ProjectRoot/docs"))
        new_dir = filedialog.askdirectory(title="Seleccionar Carpeta de Guardado por Defecto" if is_spanish else "Select Default Save Directory", initialdir=current_dir)
        if new_dir:
            set_setting("default_save_dir", os.path.abspath(new_dir))
            msg_title = "Carpeta guardada" if is_spanish else "Directory Saved"
            msg_text = f"La carpeta de guardado por defecto ahora es:\n{new_dir}" if is_spanish else f"Default save directory is now:\n{new_dir}"
            messagebox.showinfo(msg_title, msg_text)

    # Ventana de diálogo de guardado antes de salir
    def confirm_exit():
        global is_modified
        if is_modified:
            title = "Cambios sin guardar" if is_spanish else "Unsaved Changes"
            msg = "El archivo actual tiene cambios sin guardar. ¿Deseas guardarlos antes de salir?" if is_spanish else "The current file has unsaved changes. Do you want to save them before exiting?"
            ans = messagebox.askyesnocancel(title, msg)
            if ans is True: # Sí, guardar
                save_file()
                if not is_modified: # Si guardó correctamente
                    root.destroy()
            elif ans is False: # No, salir sin guardar
                root.destroy()
            # Si ans es None (Cancelar), no se hace nada
        else:
            root.destroy()

    def exit_app(event=None):
        confirm_exit()

    # Interceptar el protocolo de cierre de ventana (botón X superior)
    root.protocol("WM_DELETE_WINDOW", confirm_exit)

    # Guardar archivo al presionar ENTER en el Entry del nombre
    filename_entry.bind("<Return>", lambda e: save_file())

    def toggle_word_wrap():
        if wrap_text.get():
            text_area.config(wrap="word")
        else:
            text_area.config(wrap="none")

    def toggle_status_bar():
        if show_status.get():
            status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            status_bar.pack_forget()



    def show_about():
        title = "Acerca de Bloc de Notas" if is_spanish else "About Notepad"
        message = (
            "Bloc de Notas en Modo Oscuro (Windows 11 Style)\n\n"
            "Desarrollado en Python con Tkinter.\n"
            "Representación precisa de la estética minimalista."
            if is_spanish else
            "Notepad in Dark Mode (Windows 11 Style)\n\n"
            "Developed in Python using Tkinter.\n"
            "Accurate representation of the minimalist aesthetic."
        )
        messagebox.showinfo(title, message)

    # 6. Creación y actualización de la Barra de Menú
    menu_bar = tk.Menu(root, bg="#1b212f", fg="#e2e8f0", activebackground="#4a7bb0", activeforeground="#e2e8f0", bd=0)
    root.config(menu=menu_bar)

    wrap_text = tk.BooleanVar(value=True)
    is_bold = tk.BooleanVar(value=False)
    show_status = tk.BooleanVar(value=True)
    lang_var = tk.StringVar(value="es")

    file_menu = tk.Menu(menu_bar, tearoff=0, bg="#1b212f", fg="#e2e8f0", activebackground="#4a7bb0", activeforeground="#e2e8f0", bd=0)
    edit_menu = tk.Menu(menu_bar, tearoff=0, bg="#1b212f", fg="#e2e8f0", activebackground="#4a7bb0", activeforeground="#e2e8f0", bd=0)
    format_menu = tk.Menu(menu_bar, tearoff=0, bg="#1b212f", fg="#e2e8f0", activebackground="#4a7bb0", activeforeground="#e2e8f0", bd=0)
    view_menu = tk.Menu(menu_bar, tearoff=0, bg="#1b212f", fg="#e2e8f0", activebackground="#4a7bb0", activeforeground="#e2e8f0", bd=0)
    zoom_menu = tk.Menu(view_menu, tearoff=0, bg="#1b212f", fg="#e2e8f0", activebackground="#4a7bb0", activeforeground="#e2e8f0", bd=0)
    lang_menu = tk.Menu(menu_bar, tearoff=0, bg="#1b212f", fg="#e2e8f0", activebackground="#4a7bb0", activeforeground="#e2e8f0", bd=0)
    help_menu = tk.Menu(menu_bar, tearoff=0, bg="#1b212f", fg="#e2e8f0", activebackground="#4a7bb0", activeforeground="#e2e8f0", bd=0)

    zoom_menu.add_command(accelerator="Ctrl+=", command=zoom_in)
    zoom_menu.add_command(accelerator="Ctrl+-", command=zoom_out)
    zoom_menu.add_command(accelerator="Ctrl+0", command=reset_zoom)

    def change_lang(lang):
        global is_spanish
        is_spanish = (lang == "es")
        update_language_ui()

    lang_menu.add_radiobutton(label="Español", variable=lang_var, value="es", command=lambda: change_lang("es"))
    lang_menu.add_radiobutton(label="English", variable=lang_var, value="en", command=lambda: change_lang("en"))

    def update_language_ui():
        if is_spanish:
            # Archivo
            menu_bar.entryconfig(1, label="Archivo")
            file_menu.entryconfig(0, label="Nuevo")
            file_menu.entryconfig(1, label="Abrir...")
            file_menu.entryconfig(2, label="Guardar")
            file_menu.entryconfig(3, label="Guardar como...")
            file_menu.entryconfig(4, label="Establecer carpeta por defecto...")
            file_menu.entryconfig(6, label="Salir")
            
            # Edición
            menu_bar.entryconfig(2, label="Edición")
            edit_menu.entryconfig(0, label="Deshacer")
            edit_menu.entryconfig(1, label="Rehacer")
            edit_menu.entryconfig(3, label="Cortar")
            edit_menu.entryconfig(4, label="Copiar")
            edit_menu.entryconfig(5, label="Pegar")
            edit_menu.entryconfig(7, label="Seleccionar todo")

            # Formato
            menu_bar.entryconfig(3, label="Formato")
            format_menu.entryconfig(0, label="Ajuste de línea")
            format_menu.entryconfig(1, label="Fuente en negrita")

            # Ver
            menu_bar.entryconfig(4, label="Ver")
            view_menu.entryconfig(0, label="Zoom")
            view_menu.entryconfig(1, label="Barra de estado")
            zoom_menu.entryconfig(0, label="Acercar")
            zoom_menu.entryconfig(1, label="Alejar")
            zoom_menu.entryconfig(2, label="Restablecer zoom")

            # Idioma y Ayuda
            menu_bar.entryconfig(5, label="Idioma")
            menu_bar.entryconfig(6, label="Ayuda")
            help_menu.entryconfig(0, label="Acerca de")
            
            file_lbl.config(text=" FILE_NAME >")
        else:
            # File
            menu_bar.entryconfig(1, label="File")
            file_menu.entryconfig(0, label="New")
            file_menu.entryconfig(1, label="Open...")
            file_menu.entryconfig(2, label="Save")
            file_menu.entryconfig(3, label="Save As...")
            file_menu.entryconfig(4, label="Set Default Folder...")
            file_menu.entryconfig(6, label="Exit")

            # Edit
            menu_bar.entryconfig(2, label="Edit")
            edit_menu.entryconfig(0, label="Undo")
            edit_menu.entryconfig(1, label="Redo")
            edit_menu.entryconfig(3, label="Cut")
            edit_menu.entryconfig(4, label="Copy")
            edit_menu.entryconfig(5, label="Paste")
            edit_menu.entryconfig(7, label="Select All")

            # Format
            menu_bar.entryconfig(3, label="Format")
            format_menu.entryconfig(0, label="Word Wrap")
            format_menu.entryconfig(1, label="Bold Font")

            # View
            menu_bar.entryconfig(4, label="View")
            view_menu.entryconfig(0, label="Zoom")
            view_menu.entryconfig(1, label="Status Bar")
            zoom_menu.entryconfig(0, label="Zoom In")
            zoom_menu.entryconfig(1, label="Zoom Out")
            zoom_menu.entryconfig(2, label="Restore Default Zoom")

            # Language & Help
            menu_bar.entryconfig(5, label="Language")
            menu_bar.entryconfig(6, label="Help")
            help_menu.entryconfig(0, label="About Notepad")
            
            file_lbl.config(text=" FILE_NAME >")

        update_title()

    menu_bar.add_cascade(menu=file_menu)
    menu_bar.add_cascade(menu=edit_menu)
    menu_bar.add_cascade(menu=format_menu)
    menu_bar.add_cascade(menu=view_menu)
    menu_bar.add_cascade(menu=lang_menu)
    menu_bar.add_cascade(menu=help_menu)

    file_menu.add_command(accelerator="Ctrl+N", command=new_file)
    file_menu.add_command(accelerator="Ctrl+O", command=open_file)
    file_menu.add_command(accelerator="Ctrl+S", command=save_file)
    file_menu.add_command(accelerator="Ctrl+Shift+S", command=save_file_as)
    file_menu.add_command(command=set_default_save_dir)
    file_menu.add_separator()
    file_menu.add_command(accelerator="Ctrl+Q", command=exit_app)

    edit_menu.add_command(accelerator="Ctrl+Z", command=lambda: text_area.event_generate("<<Undo>>"))
    edit_menu.add_command(accelerator="Ctrl+Y", command=lambda: text_area.event_generate("<<Redo>>"))
    edit_menu.add_separator()
    edit_menu.add_command(accelerator="Ctrl+X", command=lambda: text_area.event_generate("<<Cut>>"))
    edit_menu.add_command(accelerator="Ctrl+C", command=lambda: text_area.event_generate("<<Copy>>"))
    edit_menu.add_command(accelerator="Ctrl+V", command=lambda: text_area.event_generate("<<Paste>>"))
    edit_menu.add_separator()
    edit_menu.add_command(accelerator="Ctrl+A", command=lambda: (text_area.tag_add("sel", "1.0", tk.END), "break"))

    format_menu.add_checkbutton(variable=wrap_text, command=toggle_word_wrap)
    format_menu.add_checkbutton(variable=is_bold, command=update_font)

    view_menu.add_cascade(menu=zoom_menu)
    view_menu.add_checkbutton(variable=show_status, command=toggle_status_bar)

    help_menu.add_command(command=show_about)

    # Cargar el último archivo de sesión abierta si existe y es válido
    last_session_path = get_last_session_file()
    if last_session_path and os.path.exists(last_session_path):
        try:
            with open(last_session_path, "r", encoding="utf-8") as f:
                content = f.read()
            text_area.insert("1.0", content)
            current_file = os.path.abspath(last_session_path)
            set_filename_in_entry(current_file)
            update_title()
            update_cursor_pos()
        except Exception:
            current_file = None
            set_filename_in_entry(None)
    else:
        # Abrir archivo nuevo en blanco por defecto al arrancar
        current_file = None
        set_filename_in_entry(None)

    # Restablecer estado de modificación inicial (ignora las inserciones del arranque)
    text_area.edit_modified(False)
    is_modified = False

    update_language_ui()

    # Shortcuts globales (Teclado)
    root.bind("<Control-n>", new_file)
    root.bind("<Control-o>", open_file)
    root.bind("<Control-s>", save_file)
    root.bind("<Control-S>", save_file_as)
    root.bind("<Control-q>", exit_app)

    root.bind("<Control-equal>", zoom_in)
    root.bind("<Control-plus>", zoom_in)
    root.bind("<Control-minus>", zoom_out)
    root.bind("<Control-0>", reset_zoom)

    root.mainloop()

if __name__ == "__main__":
    main()
