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
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)
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
    
    # Verificar si la columna file_path existe en la tabla tasks, si no, agregarla
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [col[1] for col in cursor.fetchall()]
    if "file_path" not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN file_path TEXT")
        conn.commit()
    
    # Reiniciar/Eliminar las tareas temporales (sin archivo asociado) de la sesión anterior
    cursor.execute("DELETE FROM tasks WHERE file_path IS NULL OR file_path = ''")
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def load_tasks_from_db(file_path):
    """Obtiene las tareas asociadas a la ruta de archivo especificada."""
    conn = get_db_connection()
    cursor = conn.cursor()
    fp = os.path.abspath(file_path) if file_path else ""
    cursor.execute("SELECT id, text, completed FROM tasks WHERE file_path = ?", (fp,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def initialize_default_task_if_empty(file_path):
    """Si es la primera vez que se accede a este archivo o si es un archivo nuevo/temporal,
    y la lista de tareas está vacía, agrega la tarea por defecto."""
    if not file_path:
        # Para archivos temporales/nuevos, no usamos settings de persistencia a largo plazo
        # pero si no hay tareas, ponemos la de por defecto.
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE file_path IS NULL OR file_path = ''")
        count = cursor.fetchone()[0]
        if count == 0:
            default_text = "Puedes cargar tus tareas" if is_spanish else "You can load your tasks"
            cursor.execute("INSERT INTO tasks (text, completed, file_path) VALUES (?, 0, '')", (default_text,))
            conn.commit()
        conn.close()
        return

    # Para archivos persistidos, guardamos un registro de inicialización en settings
    fp = os.path.abspath(file_path)
    setting_key = f"tasks_init_{fp}"
    
    # Comprobar si ya se ha inicializado alguna vez
    if get_setting(setting_key) is not None:
        # Ya se inicializó en el pasado. Si ahora tiene 0 tareas, es porque el usuario las borró.
        # No volvemos a crear la tarea de prueba.
        return
        
    # Primera vez que se abre este archivo.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE file_path = ?", (fp,))
    count = cursor.fetchone()[0]
    if count == 0:
        default_text = "Puedes cargar tus tareas" if is_spanish else "You can load your tasks"
        cursor.execute("INSERT INTO tasks (text, completed, file_path) VALUES (?, 0, ?)", (default_text, fp))
        conn.commit()
    conn.close()
    
    # Registrar que ya fue inicializado
    set_setting(setting_key, "1")

def add_task_to_db(text, file_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    fp = os.path.abspath(file_path) if file_path else ""
    cursor.execute("INSERT INTO tasks (text, completed, file_path) VALUES (?, 0, ?)", (text, fp))
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def update_task_completed_in_db(task_id, completed):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (1 if completed else 0, task_id))
    conn.commit()
    conn.close()

def update_task_text_in_db(task_id, text):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET text = ? WHERE id = ?", (text, task_id))
    conn.commit()
    conn.close()

def delete_task_from_db(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

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

def bind_temp_tasks_to_file(new_file_path):
    """Asocia las tareas temporales agregadas (sin archivo) con la nueva ruta absoluta del archivo guardado."""
    conn = get_db_connection()
    cursor = conn.cursor()
    old_fp = ""
    new_fp = os.path.abspath(new_file_path)
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE file_path = ?", (new_fp,))
    has_saved_tasks = cursor.fetchone()[0] > 0
    
    if not has_saved_tasks:
        cursor.execute("UPDATE tasks SET file_path = ? WHERE file_path = ?", (new_fp, old_fp))
    else:
        cursor.execute("DELETE FROM tasks WHERE file_path = ?", (old_fp,))
        
    conn.commit()
    conn.close()

# ----------------- Clases de UI de Tareas estilo Cyberpunk -----------------

class ConsoleCheckbutton(tk.Label):
    """Checkbox interactivo de consola. [ ] en cian/magenta y [✔] en verde neón."""
    def __init__(self, parent, text, completed, on_toggle, **kwargs):
        self.completed = completed
        self.on_toggle = on_toggle
        self.text_content = text
        
        display_text = f"[✔] {text}" if completed else f"[ ] {text}"
        super().__init__(
            parent,
            text=display_text,
            bg="#08080f",
            fg="#39ff14" if completed else "#00f0ff",
            font=("Consolas", 10, "overstrike" if completed else "normal"),
            anchor="w",
            justify=tk.LEFT,
            cursor="hand2",
            **kwargs
        )
        self.bind("<Button-1>", self._click)
        
    def _click(self, event):
        self.completed = not self.completed
        if self.completed:
            self.config(text=f"[✔] {self.text_content}", fg="#39ff14", font=("Consolas", 10, "overstrike"))
        else:
            self.config(text=f"[ ] {self.text_content}", fg="#00f0ff", font=("Consolas", 10, "normal"))
        self.on_toggle(self.completed)

    def update_text(self, new_text):
        self.text_content = new_text
        display_text = f"[✔] {new_text}" if self.completed else f"[ ] {new_text}"
        self.config(text=display_text)


class TaskRow(tk.Frame):
    """Representa una fila de tarea Cyberpunk con botones [✎] y [🗑] en hover."""
    def __init__(self, parent, task_id, text, completed, on_toggle, on_edit, on_delete):
        super().__init__(parent, bg="#08080f", padx=5, pady=4)
        self.task_id = task_id
        self.text = text
        self.on_toggle = on_toggle
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        self.cb = ConsoleCheckbutton(
            self,
            text=text,
            completed=completed,
            on_toggle=self.toggle
        )
        self.cb.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.btn_frame = tk.Frame(self, bg="#08080f")
        
        self.edit_btn = tk.Button(
            self.btn_frame,
            text="[✎]",
            bg="#08080f",
            fg="#00f0ff",
            activebackground="#1a1a24",
            activeforeground="#00f0ff",
            bd=0,
            padx=2,
            pady=1,
            font=("Consolas", 9, "bold"),
            command=lambda: self.on_edit(self.task_id, self.text)
        )
        self.delete_btn = tk.Button(
            self.btn_frame,
            text="[🗑]",
            bg="#08080f",
            fg="#ff007f",
            activebackground="#1a1a24",
            activeforeground="#ff007f",
            bd=0,
            padx=2,
            pady=1,
            font=("Consolas", 9, "bold"),
            command=lambda: self.on_delete(self.task_id)
        )
        
        self.edit_btn.pack(side=tk.LEFT, padx=1)
        self.delete_btn.pack(side=tk.LEFT, padx=1)
        
        self.btn_frame.pack_forget()
        
        # Enlaces de hover
        self.bind("<Enter>", self.show_buttons)
        self.bind("<Leave>", self.hide_buttons)
        self.cb.bind("<Enter>", self.show_buttons)
        self.cb.bind("<Leave>", self.hide_buttons)
        
    def show_buttons(self, event=None):
        self.btn_frame.pack(side=tk.RIGHT)
        
    def hide_buttons(self, event=None):
        x, y = self.winfo_pointerxy()
        widget = self.winfo_containing(x, y)
        if widget not in (self, self.cb, self.btn_frame, self.edit_btn, self.delete_btn):
            self.btn_frame.pack_forget()
            
    def toggle(self, completed):
        self.on_toggle(self.task_id, completed)


class TaskListFrame(tk.Frame):
    """Panel lateral de tareas completo, vinculado al archivo activo."""
    def __init__(self, parent, get_current_file_cb):
        super().__init__(parent, bg="#08080f")
        self.get_current_file = get_current_file_cb
        
        # Título
        self.title_label = tk.Label(self, text="[ LISTA DE TAREAS ]", font=("Consolas", 11, "bold"), bg="#08080f", fg="#ff007f")
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Fila de Entrada tipo Prompt
        input_frame = tk.Frame(self, bg="#08080f")
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        prompt_lbl = tk.Label(input_frame, text="$", font=("Consolas", 10, "bold"), bg="#08080f", fg="#00f0ff")
        prompt_lbl.pack(side=tk.LEFT, padx=(0, 5))
        
        self.entry = tk.Entry(
            input_frame,
            bg="#08080f",
            fg="#00f0ff",
            insertbackground="#00f0ff",
            bd=0,
            highlightthickness=1,
            highlightbackground="#1a1a24",
            highlightcolor="#ff007f",
            font=("Consolas", 10)
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3, ipadx=4)
        
        self.placeholder = "Nueva Tarea..."
        self.entry.insert(0, self.placeholder)
        self.entry.config(fg="#445566")
        self.entry.bind("<FocusIn>", self.clear_placeholder)
        self.entry.bind("<FocusOut>", self.restore_placeholder)
        
        # Guardar tarea directamente al pulsar ENTER
        self.entry.bind("<Return>", lambda e: self.add_task())
        
        self.add_btn = tk.Button(
            input_frame,
            text="[+]",
            bg="#08080f",
            fg="#ff007f",
            activebackground="#08080f",
            activeforeground="#ff007f",
            bd=0,
            padx=5,
            font=("Consolas", 10, "bold"),
            command=self.add_task
        )
        self.add_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Contenedor con Scroll
        self.canvas_frame = tk.Frame(self, bg="#08080f")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#08080f", bd=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        
        self.tasks_inner_frame = tk.Frame(self.canvas, bg="#08080f")
        self.tasks_inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.tasks_inner_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_tasks()
        
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
    def clear_placeholder(self, event):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg="#00f0ff")
            
    def restore_placeholder(self, event):
        # Solo restaura el placeholder si no tiene foco y el texto está vacío
        if not self.entry.get() and self.focus_get() != self.entry:
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg="#445566")
            
    def load_tasks(self):
        for widget in self.tasks_inner_frame.winfo_children():
            widget.destroy()
            
        try:
            rows = load_tasks_from_db(self.get_current_file())
            for task_id, text, completed in rows:
                self.create_task_row(task_id, text, completed)
        except Exception:
            pass
            
    def create_task_row(self, task_id, text, completed):
        row = TaskRow(self.tasks_inner_frame, task_id, text, completed, 
                      on_toggle=self.toggle_task, 
                      on_edit=self.edit_task, 
                      on_delete=self.delete_task)
        row.pack(fill=tk.X, pady=2)
        
    def add_task(self):
        text = self.entry.get().strip()
        if text and text != self.placeholder:
            try:
                task_id = add_task_to_db(text, self.get_current_file())
                self.create_task_row(task_id, text, 0)
                self.entry.delete(0, tk.END)
                self.entry.focus_set()  # Conservar foco listo para escribir otra tarea
                self.canvas.yview_moveto(1.0)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la tarea:\n{e}")
                
    def toggle_task(self, task_id, completed):
        update_task_completed_in_db(task_id, completed)
        
    def edit_task(self, task_id, current_text):
        edit_dialog = tk.Toplevel(self)
        edit_dialog.title("Editar Tarea" if is_spanish else "Edit Task")
        edit_dialog.geometry("320x130")
        edit_dialog.configure(bg="#08080f")
        edit_dialog.transient(self.winfo_toplevel())
        edit_dialog.grab_set()
        edit_dialog.geometry(f"+{self.winfo_toplevel().winfo_x() + 100}+{self.winfo_toplevel().winfo_y() + 100}")
        
        lbl = tk.Label(edit_dialog, text="$ editar --task-text:", bg="#08080f", fg="#ff007f", font=("Consolas", 10, "bold"))
        lbl.pack(pady=(10, 5), padx=10, anchor="w")
        
        entry = tk.Entry(edit_dialog, bg="#08080f", fg="#00f0ff", insertbackground="#00f0ff", bd=0, highlightthickness=1, highlightbackground="#1a1a24", highlightcolor="#ff007f", font=("Consolas", 10))
        entry.pack(fill=tk.X, padx=10, pady=5, ipady=3)
        entry.insert(0, current_text)
        entry.focus()
        
        def save():
            new_text = entry.get().strip()
            if new_text:
                update_task_text_in_db(task_id, new_text)
                self.load_tasks()
                edit_dialog.destroy()
                
        btn_frame = tk.Frame(edit_dialog, bg="#08080f")
        btn_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        btn_save = tk.Button(btn_frame, text="[Guardar]" if is_spanish else "[Save]", bg="#08080f", fg="#00f0ff", activebackground="#08080f", activeforeground="#00f0ff", bd=0, font=("Consolas", 10, "bold"), command=save)
        btn_save.pack(side=tk.RIGHT, padx=5)
        
        btn_cancel = tk.Button(btn_frame, text="[Cancelar]" if is_spanish else "[Cancel]", bg="#08080f", fg="#ff007f", activebackground="#08080f", activeforeground="#ff007f", bd=0, font=("Consolas", 10, "bold"), command=edit_dialog.destroy)
        btn_cancel.pack(side=tk.RIGHT)
        
        entry.bind("<Return>", lambda e: save())
        
    def delete_task(self, task_id):
        delete_task_from_db(task_id)
        self.load_tasks()

# ----------------- Función Principal de Ejecución -----------------

def main():
    global current_file, is_modified
    
    # Inicializar la estructura física de ProjectRoot
    init_project_root()
    
    root = tk.Tk()
    root.title("Sin título - Bloc de Notas")
    root.geometry("1000x680")
    root.configure(bg="#08080f")
    
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

    # Configuración de estilos Cyberpunk para scrollbars
    style = ttk.Style()
    style.theme_use('clam')
    
    # Scrollbar vertical magenta neón
    style.configure(
        "Vertical.TScrollbar",
        gripcount=0,
        background="#ff007f",
        troughcolor="#08080f",
        bordercolor="#ff007f",
        lightcolor="#ff007f",
        darkcolor="#ff007f",
        arrowcolor="#00f0ff"
    )
    style.map(
        "Vertical.TScrollbar",
        background=[('pressed', '#00f0ff'), ('active', '#ff33aa')]
    )
    
    # Scrollbar horizontal magenta neón
    style.configure(
        "Horizontal.TScrollbar",
        gripcount=0,
        background="#ff007f",
        troughcolor="#08080f",
        bordercolor="#ff007f",
        lightcolor="#ff007f",
        darkcolor="#ff007f",
        arrowcolor="#00f0ff"
    )
    style.map(
        "Horizontal.TScrollbar",
        background=[('pressed', '#00f0ff'), ('active', '#ff33aa')]
    )

    # --- BARRA SUPERIOR: Nombre de archivo uniforme ---
    top_bar = tk.Frame(root, bg="#08080f", height=38)
    top_bar.pack(side=tk.TOP, fill=tk.X)
    
    top_border = tk.Frame(top_bar, bg="#ff007f", height=1)
    top_border.pack(side=tk.BOTTOM, fill=tk.X)
    
    file_lbl = tk.Label(top_bar, text=" FILE_NAME >", bg="#08080f", fg="#00f0ff", font=("Consolas", 10, "bold"))
    file_lbl.pack(side=tk.LEFT, padx=(15, 5), pady=5)
    
    filename_entry = tk.Entry(
        top_bar,
        bg="#08080f",
        fg="#00f0ff",
        insertbackground="#00f0ff",
        bd=0,
        highlightthickness=1,
        highlightbackground="#1a1a24",
        highlightcolor="#ff007f",
        font=("Consolas", 10)
    )
    # Pack filename_entry ocupando todo el ancho sin botón al lado
    filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 15), pady=5, ipady=3)
    
    # Inicializar con "Sin título"
    filename_entry.insert(0, "Sin título" if is_spanish else "Untitled")
    filename_entry.config(fg="#445566")
    
    def on_filename_focus_in(event):
        if filename_entry.get() in ("Sin título", "Untitled"):
            filename_entry.delete(0, tk.END)
            filename_entry.config(fg="#00f0ff")
            
    def on_filename_focus_out(event):
        if not filename_entry.get().strip():
            filename_entry.insert(0, "Sin título" if is_spanish else "Untitled")
            filename_entry.config(fg="#445566")
            
    filename_entry.bind("<FocusIn>", on_filename_focus_in)
    filename_entry.bind("<FocusOut>", on_filename_focus_out)

    def get_current_file():
        global current_file
        return current_file

    def set_filename_in_entry(filepath):
        filename_entry.delete(0, tk.END)
        filename_entry.config(fg="#00f0ff")
        if filepath:
            filename_entry.insert(0, os.path.basename(filepath)) # Mostrar solo nombre de archivo estilo Google Docs
        else:
            filename_entry.insert(0, "Sin título" if is_spanish else "Untitled")
            filename_entry.config(fg="#445566")

    # Contenedor Principal en Dos Columnas
    paned_window = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
    
    # --- PANEL IZQUIERDO: Editor de Texto ---
    editor_frame = tk.Frame(paned_window, bg="#08080f")
    
    text_area = tk.Text(
        editor_frame,
        bg="#08080f",
        fg="#00f0ff",
        insertbackground="#00f0ff",
        selectbackground="#1a3a1a",
        selectforeground="#00f0ff",
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

    # --- PANEL DERECHO: Lista de Tareas (Alto completo) ---
    right_panel = tk.Frame(paned_window, bg="#08080f", width=280)
    right_panel.pack_propagate(False)
    
    task_frame = TaskListFrame(right_panel, get_current_file)
    task_frame.pack(fill=tk.BOTH, expand=True)

    # Registrar columnas en el PanedWindow
    paned_window.add(editor_frame, weight=3)
    paned_window.add(right_panel, weight=1)

    # 4. Barra de Estado (Status Bar) uniforme
    status_bar = tk.Frame(root, bg="#08080f", height=24, bd=0)
    
    status_border = tk.Frame(status_bar, bg="#ff007f", height=1)
    status_border.pack(side=tk.TOP, fill=tk.X)

    status_content = tk.Frame(status_bar, bg="#08080f")
    status_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=2)

    prompt_label = tk.Label(status_content, text="user@cyber-console:~/notepad$", bg="#08080f", fg="#00f0ff", font=("Consolas", 9, "bold"))
    prompt_label.pack(side=tk.LEFT)

    cursor_label = tk.Label(status_content, text="Ln 1, Col 1", bg="#08080f", fg="#00f0ff", font=("Consolas", 9))
    cursor_label.pack(side=tk.LEFT, padx=(10, 0))

    encoding_label = tk.Label(status_content, text="UTF-8", bg="#08080f", fg="#00f0ff", font=("Consolas", 9))
    encoding_label.pack(side=tk.RIGHT)

    sep2 = tk.Label(status_content, text="  |  ", bg="#08080f", fg="#ff007f", font=("Consolas", 9))
    sep2.pack(side=tk.RIGHT)

    line_ending_label = tk.Label(status_content, text="LF", bg="#08080f", fg="#00f0ff", font=("Consolas", 9))
    line_ending_label.pack(side=tk.RIGHT)

    sep1 = tk.Label(status_content, text="  |  ", bg="#08080f", fg="#ff007f", font=("Consolas", 9))
    sep1.pack(side=tk.RIGHT)

    zoom_label = tk.Label(status_content, text="100%", bg="#08080f", fg="#00f0ff", font=("Consolas", 9))
    zoom_label.pack(side=tk.RIGHT)

    # Empaquetado global
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    paned_window.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

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
        name = os.path.basename(current_file) if current_file else ("Sin título" if is_spanish else "Untitled")
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
        if not path_input or path_input in ("Sin título", "Untitled"):
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
            is_new = (current_file is None)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            current_file = file_path
            set_filename_in_entry(file_path)
            update_title()
            update_session_file(file_path)
            
            if is_new:
                # Migrar tareas temporales al nuevo archivo
                bind_temp_tasks_to_file(file_path)
                
            # Marcar archivo como guardado sin modificaciones pendientes
            text_area.edit_modified(False)
            is_modified = False
            
            task_frame.load_tasks()
        except Exception as e:
            err_title = "Error al guardar" if is_spanish else "Error saving file"
            messagebox.showerror(err_title, str(e))

    def save_file_as(event=None):
        global current_file, is_modified
        title = "Guardar como..." if is_spanish else "Save As..."
        file_types = [("Archivos de texto (*.txt)", "*.txt"), ("Todos los archivos", "*.*")]
        
        path_input = filename_entry.get().strip()
        sugg_name = path_input if path_input not in ("Sin título", "Untitled") else "notas.txt"
        
        file_path = filedialog.asksaveasfilename(title=title, filetypes=file_types, defaultextension=".txt", initialfile=sugg_name)
        if file_path:
            set_filename_in_entry(file_path)
            save_file()

    def new_file(event=None):
        global current_file, is_modified
        text_area.config(state=tk.NORMAL)
        text_area.delete("1.0", tk.END)
        current_file = None
        
        # Eliminar las tareas del archivo temporal anterior para empezar limpio
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE file_path IS NULL OR file_path = ''")
        conn.commit()
        conn.close()
        
        initialize_default_task_if_empty(None)
        set_filename_in_entry(None)
        update_title()
        update_cursor_pos()
        update_session_file(None)
        
        # Limpiar banderas de modificación
        text_area.edit_modified(False)
        is_modified = False
        
        task_frame.load_tasks()

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
                initialize_default_task_if_empty(file_path)
                set_filename_in_entry(file_path)
                update_title()
                update_cursor_pos()
                update_session_file(file_path)
                
                # Limpiar banderas de modificación
                text_area.edit_modified(False)
                is_modified = False
                
                task_frame.load_tasks()
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

    def toggle_task_list():
        if show_tasks.get():
            paned_window.add(right_panel, weight=1)
        else:
            paned_window.forget(right_panel)

    def toggle_task_list_shortcut(event=None):
        show_tasks.set(not show_tasks.get())
        toggle_task_list()

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
    menu_bar = tk.Menu(root, bg="#08080f", fg="#00f0ff", activebackground="#ff007f", activeforeground="#08080f", bd=0)
    root.config(menu=menu_bar)

    wrap_text = tk.BooleanVar(value=True)
    is_bold = tk.BooleanVar(value=False)
    show_status = tk.BooleanVar(value=True)
    show_tasks = tk.BooleanVar(value=True)
    lang_var = tk.StringVar(value="es")

    file_menu = tk.Menu(menu_bar, tearoff=0, bg="#08080f", fg="#00f0ff", activebackground="#ff007f", activeforeground="#08080f", bd=0)
    edit_menu = tk.Menu(menu_bar, tearoff=0, bg="#08080f", fg="#00f0ff", activebackground="#ff007f", activeforeground="#08080f", bd=0)
    format_menu = tk.Menu(menu_bar, tearoff=0, bg="#08080f", fg="#00f0ff", activebackground="#ff007f", activeforeground="#08080f", bd=0)
    view_menu = tk.Menu(menu_bar, tearoff=0, bg="#08080f", fg="#00f0ff", activebackground="#ff007f", activeforeground="#08080f", bd=0)
    zoom_menu = tk.Menu(view_menu, tearoff=0, bg="#08080f", fg="#00f0ff", activebackground="#ff007f", activeforeground="#08080f", bd=0)
    lang_menu = tk.Menu(menu_bar, tearoff=0, bg="#08080f", fg="#00f0ff", activebackground="#ff007f", activeforeground="#08080f", bd=0)
    help_menu = tk.Menu(menu_bar, tearoff=0, bg="#08080f", fg="#00f0ff", activebackground="#ff007f", activeforeground="#08080f", bd=0)

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
            view_menu.entryconfig(2, label="Lista de tareas")
            zoom_menu.entryconfig(0, label="Acercar")
            zoom_menu.entryconfig(1, label="Alejar")
            zoom_menu.entryconfig(2, label="Restablecer zoom")

            # Idioma y Ayuda
            menu_bar.entryconfig(5, label="Idioma")
            menu_bar.entryconfig(6, label="Ayuda")
            help_menu.entryconfig(0, label="Acerca de")
            
            # Textos dinámicos en paneles
            task_frame.title_label.config(text="[ LISTA DE TAREAS ]")
            task_frame.placeholder = "Nueva Tarea..."
            if task_frame.entry.get() in ("Nueva Tarea...", "New Task..."):
                task_frame.entry.delete(0, tk.END)
                task_frame.entry.insert(0, "Nueva Tarea...")
                task_frame.entry.config(fg="#445566")
            task_frame.add_btn.config(text="[+]")
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
            view_menu.entryconfig(2, label="Task List")
            zoom_menu.entryconfig(0, label="Zoom In")
            zoom_menu.entryconfig(1, label="Zoom Out")
            zoom_menu.entryconfig(2, label="Restore Default Zoom")

            # Language & Help
            menu_bar.entryconfig(5, label="Language")
            menu_bar.entryconfig(6, label="Help")
            help_menu.entryconfig(0, label="About Notepad")
            
            # Textos dinámicos en paneles
            task_frame.title_label.config(text="[ TASK LIST ]")
            task_frame.placeholder = "New Task..."
            if task_frame.entry.get() in ("Nueva Tarea...", "New Task..."):
                task_frame.entry.delete(0, tk.END)
                task_frame.entry.insert(0, "New Task...")
                task_frame.entry.config(fg="#445566")
            task_frame.add_btn.config(text="[+]")
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
    view_menu.add_checkbutton(variable=show_tasks, command=toggle_task_list, accelerator="Ctrl+T")

    help_menu.add_command(command=show_about)

    # Cargar el último archivo de sesión abierta si existe y es válido
    last_session_path = get_last_session_file()
    if last_session_path and os.path.exists(last_session_path):
        try:
            with open(last_session_path, "r", encoding="utf-8") as f:
                content = f.read()
            text_area.insert("1.0", content)
            current_file = os.path.abspath(last_session_path)
            initialize_default_task_if_empty(current_file)
            set_filename_in_entry(current_file)
            update_title()
            update_cursor_pos()
        except Exception:
            current_file = None
            initialize_default_task_if_empty(None)
            set_filename_in_entry(None)
    else:
        # Abrir archivo nuevo en blanco por defecto al arrancar
        current_file = None
        initialize_default_task_if_empty(None)
        set_filename_in_entry(None)

    # Carga inicial de las tareas en la UI
    task_frame.load_tasks()

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
    root.bind("<Control-t>", toggle_task_list_shortcut)
    root.bind("<Control-T>", toggle_task_list_shortcut)

    root.mainloop()

if __name__ == "__main__":
    main()
