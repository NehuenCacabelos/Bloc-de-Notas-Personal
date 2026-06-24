import sys
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk

# Configuración de variables globales
current_file = None
font_size = 11
is_spanish = True

def main():
    root = tk.Tk()
    root.title("Sin título - Bloc de Notas")
    root.geometry("900x650")
    
    # 1. Habilitar la barra de título oscura en Windows 10/11
    if sys.platform.startswith("win"):
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
            dark_mode = 1
            # Windows 11 (atributo 20)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, ctypes.byref(ctypes.c_int(dark_mode)), ctypes.sizeof(ctypes.c_int(dark_mode))
            )
            # Windows 10 (atributo 19)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 19, ctypes.byref(ctypes.c_int(dark_mode)), ctypes.sizeof(ctypes.c_int(dark_mode))
            )
        except Exception:
            pass

    # 2. Configuración del estilo del Scrollbar de ttk para que sea plano y oscuro
    style = ttk.Style()
    style.theme_use('clam')
    style.configure(
        "Vertical.TScrollbar",
        gripcount=0,
        background="#3e3e3e",
        troughcolor="#1e1e1e",
        bordercolor="#1e1e1e",
        lightcolor="#3e3e3e",
        darkcolor="#3e3e3e",
        arrowcolor="#ffffff"
    )
    style.map(
        "Vertical.TScrollbar",
        background=[('pressed', '#505050'), ('active', '#4e4e4e')]
    )

    # Contenedor principal
    main_frame = tk.Frame(root, bg="#1e1e1e")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # 3. Área de Texto y Scrollbar
    # Configuración de colores planos según la descripción visual
    text_area = tk.Text(
        main_frame,
        bg="#1e1e1e",
        fg="#e3e3e3",
        insertbackground="#ffffff", # Cursor blanco
        selectbackground="#3e3e3e", # Selección gris oscura
        selectforeground="#ffffff",
        font=("Consolas", font_size),
        undo=True,
        maxundo=100,
        bd=0,
        highlightthickness=0,
        wrap="word"
    )
    
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=text_area.yview)
    text_area.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=4)

    # 4. Barra de Estado (Status Bar)
    status_bar = tk.Frame(root, bg="#202020", height=24, bd=0)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Borde superior sutil de la barra de estado
    status_border = tk.Frame(status_bar, bg="#3c3c3c", height=1)
    status_border.pack(side=tk.TOP, fill=tk.X)

    # Contenedor interno de la barra de estado para relleno y alineación
    status_content = tk.Frame(status_bar, bg="#202020")
    status_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=2)

    # Elementos de la barra de estado
    cursor_label = tk.Label(status_content, text="Ln 1, Col 1", bg="#202020", fg="#e3e3e3", font=("Segoe UI", 9))
    cursor_label.pack(side=tk.LEFT)

    encoding_label = tk.Label(status_content, text="UTF-8", bg="#202020", fg="#e3e3e3", font=("Segoe UI", 9))
    encoding_label.pack(side=tk.RIGHT)

    sep2 = tk.Label(status_content, text="  |  ", bg="#202020", fg="#3c3c3c", font=("Segoe UI", 9))
    sep2.pack(side=tk.RIGHT)

    line_ending_label = tk.Label(status_content, text="Windows (CRLF)", bg="#202020", fg="#e3e3e3", font=("Segoe UI", 9))
    line_ending_label.pack(side=tk.RIGHT)

    sep1 = tk.Label(status_content, text="  |  ", bg="#202020", fg="#3c3c3c", font=("Segoe UI", 9))
    sep1.pack(side=tk.RIGHT)

    zoom_label = tk.Label(status_content, text="100%", bg="#202020", fg="#e3e3e3", font=("Segoe UI", 9))
    zoom_label.pack(side=tk.RIGHT)

    # 5. Funciones auxiliares y eventos
    def update_cursor_pos(event=None):
        pos = text_area.index("insert")
        line, col = pos.split(".")
        cursor_label.config(text=f"Ln {line}, Col {int(col) + 1}")

    # Escuchas del cursor
    text_area.bind("<KeyRelease>", update_cursor_pos)
    text_area.bind("<ButtonRelease>", update_cursor_pos)

    # Actualizar título de la ventana
    def update_title():
        name = os.path.basename(current_file) if current_file else ("Sin título" if is_spanish else "Untitled")
        app_name = "Bloc de Notas" if is_spanish else "Notepad"
        root.title(f"{name} - {app_name}")

    # Zoom
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

    # Archivo
    def new_file(event=None):
        global current_file
        text_area.delete("1.0", tk.END)
        current_file = None
        update_title()
        update_cursor_pos()

    def open_file(event=None):
        global current_file
        title = "Abrir archivo" if is_spanish else "Open file"
        file_types = [("Archivos de texto (*.txt)", "*.txt"), ("Todos los archivos", "*.*")]
        file_path = filedialog.askopenfilename(title=title, filetypes=file_types)
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                text_area.delete("1.0", tk.END)
                text_area.insert("1.0", content)
                current_file = file_path
                update_title()
                update_cursor_pos()
            except Exception as e:
                err_title = "Error al abrir" if is_spanish else "Error opening file"
                messagebox.showerror(err_title, str(e))

    def save_file(event=None):
        global current_file
        if not current_file:
            save_file_as()
        else:
            try:
                content = text_area.get("1.0", tk.END)[:-1] # Remover newline final que agrega Tkinter
                with open(current_file, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                err_title = "Error al guardar" if is_spanish else "Error saving file"
                messagebox.showerror(err_title, str(e))

    def save_file_as(event=None):
        global current_file
        title = "Guardar como..." if is_spanish else "Save As..."
        file_types = [("Archivos de texto (*.txt)", "*.txt"), ("Todos los archivos", "*.*")]
        file_path = filedialog.asksaveasfilename(title=title, filetypes=file_types, defaultextension=".txt")
        if file_path:
            current_file = file_path
            save_file()
            update_title()

    def exit_app(event=None):
        root.destroy()

    # Formato
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

    # Ayuda
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
    menu_bar = tk.Menu(root, bg="#2b2b2b", fg="#ffffff", activebackground="#3e3e3e", activeforeground="#ffffff", bd=0)
    root.config(menu=menu_bar)

    # Variables de menú
    wrap_text = tk.BooleanVar(value=True)
    is_bold = tk.BooleanVar(value=False)
    show_status = tk.BooleanVar(value=True)
    lang_var = tk.StringVar(value="es")

    # Submenús
    file_menu = tk.Menu(menu_bar, tearoff=0, bg="#2b2b2b", fg="#ffffff", activebackground="#3e3e3e", activeforeground="#ffffff", bd=0)
    edit_menu = tk.Menu(menu_bar, tearoff=0, bg="#2b2b2b", fg="#ffffff", activebackground="#3e3e3e", activeforeground="#ffffff", bd=0)
    format_menu = tk.Menu(menu_bar, tearoff=0, bg="#2b2b2b", fg="#ffffff", activebackground="#3e3e3e", activeforeground="#ffffff", bd=0)
    view_menu = tk.Menu(menu_bar, tearoff=0, bg="#2b2b2b", fg="#ffffff", activebackground="#3e3e3e", activeforeground="#ffffff", bd=0)
    zoom_menu = tk.Menu(view_menu, tearoff=0, bg="#2b2b2b", fg="#ffffff", activebackground="#3e3e3e", activeforeground="#ffffff", bd=0)
    lang_menu = tk.Menu(menu_bar, tearoff=0, bg="#2b2b2b", fg="#ffffff", activebackground="#3e3e3e", activeforeground="#ffffff", bd=0)
    help_menu = tk.Menu(menu_bar, tearoff=0, bg="#2b2b2b", fg="#ffffff", activebackground="#3e3e3e", activeforeground="#ffffff", bd=0)

    # Construir submenú Zoom
    zoom_menu.add_command(accelerator="Ctrl+=", command=zoom_in)
    zoom_menu.add_command(accelerator="Ctrl+-", command=zoom_out)
    zoom_menu.add_command(accelerator="Ctrl+0", command=reset_zoom)

    # Idiomas
    def change_lang(lang):
        global is_spanish
        is_spanish = (lang == "es")
        update_language_ui()

    lang_menu.add_radiobutton(label="Español", variable=lang_var, value="es", command=lambda: change_lang("es"))
    lang_menu.add_radiobutton(label="English", variable=lang_var, value="en", command=lambda: change_lang("en"))

    # Configurar etiquetas dinámicas de idioma
    def update_language_ui():
        if is_spanish:
            # File
            menu_bar.entryconfig(1, label="Archivo")
            file_menu.entryconfig(0, label="Nuevo")
            file_menu.entryconfig(1, label="Abrir...")
            file_menu.entryconfig(2, label="Guardar")
            file_menu.entryconfig(3, label="Guardar como...")
            file_menu.entryconfig(5, label="Salir")
            
            # Edit
            menu_bar.entryconfig(2, label="Edición")
            edit_menu.entryconfig(0, label="Deshacer")
            edit_menu.entryconfig(1, label="Rehacer")
            edit_menu.entryconfig(3, label="Cortar")
            edit_menu.entryconfig(4, label="Copiar")
            edit_menu.entryconfig(5, label="Pegar")
            edit_menu.entryconfig(7, label="Seleccionar todo")

            # Format
            menu_bar.entryconfig(3, label="Formato")
            format_menu.entryconfig(0, label="Ajuste de línea")
            format_menu.entryconfig(1, label="Fuente en negrita")

            # View
            menu_bar.entryconfig(4, label="Ver")
            view_menu.entryconfig(0, label="Zoom")
            view_menu.entryconfig(1, label="Barra de estado")
            zoom_menu.entryconfig(0, label="Acercar")
            zoom_menu.entryconfig(1, label="Alejar")
            zoom_menu.entryconfig(2, label="Restablecer zoom")

            # Language / Help
            menu_bar.entryconfig(5, label="Idioma")
            menu_bar.entryconfig(6, label="Ayuda")
            help_menu.entryconfig(0, label="Acerca de")
        else:
            # File
            menu_bar.entryconfig(1, label="File")
            file_menu.entryconfig(0, label="New")
            file_menu.entryconfig(1, label="Open...")
            file_menu.entryconfig(2, label="Save")
            file_menu.entryconfig(3, label="Save As...")
            file_menu.entryconfig(5, label="Exit")

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

            # Language / Help
            menu_bar.entryconfig(5, label="Language")
            menu_bar.entryconfig(6, label="Help")
            help_menu.entryconfig(0, label="About Notepad")

        update_title()

    # Añadir submenús a la barra principal
    menu_bar.add_cascade(menu=file_menu)
    menu_bar.add_cascade(menu=edit_menu)
    menu_bar.add_cascade(menu=format_menu)
    menu_bar.add_cascade(menu=view_menu)
    menu_bar.add_cascade(menu=lang_menu)
    menu_bar.add_cascade(menu=help_menu)

    # Rellenar submenú Archivo
    file_menu.add_command(accelerator="Ctrl+N", command=new_file)
    file_menu.add_command(accelerator="Ctrl+O", command=open_file)
    file_menu.add_command(accelerator="Ctrl+S", command=save_file)
    file_menu.add_command(accelerator="Ctrl+Shift+S", command=save_file_as)
    file_menu.add_separator()
    file_menu.add_command(accelerator="Ctrl+Q", command=exit_app)

    # Rellenar submenú Edición
    edit_menu.add_command(accelerator="Ctrl+Z", command=lambda: text_area.event_generate("<<Undo>>"))
    edit_menu.add_command(accelerator="Ctrl+Y", command=lambda: text_area.event_generate("<<Redo>>"))
    edit_menu.add_separator()
    edit_menu.add_command(accelerator="Ctrl+X", command=lambda: text_area.event_generate("<<Cut>>"))
    edit_menu.add_command(accelerator="Ctrl+C", command=lambda: text_area.event_generate("<<Copy>>"))
    edit_menu.add_command(accelerator="Ctrl+V", command=lambda: text_area.event_generate("<<Paste>>"))
    edit_menu.add_separator()
    edit_menu.add_command(accelerator="Ctrl+A", command=lambda: (text_area.tag_add("sel", "1.0", tk.END), "break"))

    # Rellenar submenú Formato
    format_menu.add_checkbutton(variable=wrap_text, command=toggle_word_wrap)
    format_menu.add_checkbutton(variable=is_bold, command=update_font)

    # Rellenar submenú Ver
    view_menu.add_cascade(menu=zoom_menu)
    view_menu.add_checkbutton(variable=show_status, command=toggle_status_bar)

    # Rellenar submenú Ayuda
    help_menu.add_command(command=show_about)

    # Inicializar textos del menú
    update_language_ui()

    # 7. Shortcuts globales (Teclado)
    root.bind("<Control-n>", new_file)
    root.bind("<Control-o>", open_file)
    root.bind("<Control-s>", save_file)
    root.bind("<Control-S>", save_file_as) # Shift+S
    root.bind("<Control-q>", exit_app)

    root.bind("<Control-equal>", zoom_in)
    root.bind("<Control-plus>", zoom_in)
    root.bind("<Control-minus>", zoom_out)
    root.bind("<Control-0>", reset_zoom)

    # Ejecutar bucle principal
    root.mainloop()

if __name__ == "__main__":
    main()
