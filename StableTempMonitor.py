import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk
import json

def seleccionar_archivo():
    """Abre un cuadro de diálogo para seleccionar un archivo y devuelve su ruta."""
    return filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])

def cambiar_nombre_columna():
    """Permite cambiar el nombre de una columna seleccionada y guarda el cambio en JSON."""
    global lista_columnas, nombres_columnas
    seleccion = lista_columnas.current()
    if seleccion == -1:
        messagebox.showwarning("Advertencia", "Selecciona una columna para cambiar su nombre.")
    else:
        nuevo_nombre = simpledialog.askstring("Cambiar nombre", f"Ingrese un nuevo nombre para {nombres_columnas[seleccion]}:")
        if nuevo_nombre:
            nombres_columnas[seleccion] = nuevo_nombre
            lista_columnas['values'] = nombres_columnas  # Actualizar la lista
            actualizar_grafica()
            guardar_nombres_json()

def cargar_datos():
    """Carga los datos desde un archivo y actualiza la gráfica."""
    global data, num_columnas, seleccion_columnas, nombres_columnas

    archivo = seleccionar_archivo()
    
    if archivo:
        try:
            data = np.loadtxt(archivo, delimiter='\t')
            
            tiempos = data[:, 0]
            datos = data[:, 1:]
            
            num_columnas = datos.shape[1]
            seleccion_columnas = list(range(num_columnas))
            nombres_columnas = [f"Serie {i}" for i in range(num_columnas)]
            
            lista_columnas['values'] = nombres_columnas
            
            data = np.column_stack((tiempos, datos))
            actualizar_grafica()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo. Error: {e}")
    else:
        messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo.")

def actualizar_grafica():
    """Actualiza la gráfica con los datos cargados y la configuración actual."""
    global canvas, fig, ax, zoom_rect, zoom_start

    if canvas:
        canvas.get_tk_widget().destroy()

    fig, ax = plt.subplots(figsize=(10, 6))

    for col in seleccion_columnas:
        ax.plot(data[:, 0], data[:, col + 1], label=nombres_columnas[col])
    
    ax.axhline(y=2, color='r', linestyle='--', label='2°C')
    ax.axhline(y=8, color='r', linestyle='--', label='8°C')

    ax.set_xlabel('Tiempo (horas)')
    ax.set_ylabel('Temperatura (°C)')
    
    tiempos = data[:, 0]
    ticks = np.arange(0, min(max(tiempos), 96) + 1, 1)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f'{tick:.0f}' for tick in ticks])
    ax.set_xlim(0, max(ticks))

    # Configurar los ticks del eje y de 2 en 2 grados
    min_temp, max_temp = np.min(data[:, 1:]), np.max(data[:, 1:])
    ticks_y = np.arange(np.floor(min_temp), np.ceil(max_temp) + 1, 2)
    ax.set_yticks(ticks_y)

    ax.legend(loc='upper right')
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Conectar eventos de mouse para zoom y movimiento
    canvas.mpl_connect('button_press_event', on_mouse_press)
    canvas.mpl_connect('button_release_event', on_mouse_release)
    canvas.mpl_connect('motion_notify_event', on_mouse_move)

def guardar_grafica():
    """Guarda la gráfica en un archivo."""
    archivo_guardar = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Imagen PNG", "*.png")])
    if archivo_guardar:
        fig.savefig(archivo_guardar)

def zoom_entrada():
    """Activa el modo de zoom con el mouse (acercamiento)."""
    global modo_zoom
    modo_zoom = 'in'
    boton_zoom_in.configure(style='success.TButton')
    boton_zoom_out.configure(style='default.TButton')

def zoom_salida():
    """Activa el modo de zoom con el mouse (alejamiento)."""
    global modo_zoom
    modo_zoom = 'out'
    boton_zoom_out.configure(style='success.TButton')
    boton_zoom_in.configure(style='default.TButton')

def restaurar_vista():
    """Restablece la vista original de la gráfica y limpia los modos."""
    global ax, canvas
    ax.set_xlim(0, max(data[:, 0]))
    ax.set_ylim(np.min(data[:, 1:]), np.max(data[:, 1:]))
    canvas.draw()
    boton_zoom_in.configure(style='default.TButton')
    boton_zoom_out.configure(style='default.TButton')
    global modo_zoom, zoom_rect, zoom_start
    modo_zoom = None
    if zoom_rect is not None:
        zoom_rect.remove()  # Elimina el rectángulo de zoom si existe
    zoom_rect = None
    zoom_start = None

def guardar_nombres_json():
    """Guarda los nombres de las columnas en un archivo JSON."""
    with open('nombres_columnas.json', 'w') as f:
        json.dump(nombres_columnas, f)

def on_mouse_press(event):
    """Maneja los eventos de presionar el mouse para zoom, movimiento y selección."""
    global zoom_start, zoom_rect, modo_zoom, modo_movimiento
    if modo_zoom and event.inaxes:
        zoom_start = (event.xdata, event.ydata)
        zoom_rect = plt.Rectangle((event.xdata, event.ydata), 0, 0, edgecolor='blue', facecolor='none')
        event.inaxes.add_patch(zoom_rect)
    elif event.inaxes and modo_movimiento:
        zoom_start = (event.xdata, event.ydata)
        canvas.get_tk_widget().focus_set()

def on_mouse_release(event):
    """Maneja los eventos de soltar el mouse para aplicar zoom o mover."""
    global zoom_start, zoom_rect, modo_zoom, modo_movimiento
    if modo_zoom and event.inaxes:
        if zoom_rect:
            x0, y0 = zoom_start
            x1, y1 = event.xdata, event.ydata
            if x1 < x0:
                x0, x1 = x1, x0
            if y1 < y0:
                y0, y1 = y1, y0
            if modo_zoom == 'in':
                ax.set_xlim(x0, x1)
                ax.set_ylim(y0, y1)
            elif modo_zoom == 'out':
                x_center, y_center = (x0 + x1) / 2, (y0 + y1) / 2
                width, height = abs(x1 - x0), abs(y1 - y0)
                ax.set_xlim(x_center - width / 2, x_center + width / 2)
                ax.set_ylim(y_center - height / 2, y_center + height / 2)
            canvas.draw()
        if zoom_rect is not None:
            zoom_rect.remove()  # Elimina el rectángulo de zoom después de aplicar el zoom
        zoom_rect = None
        modo_zoom = None
    elif modo_movimiento and event.inaxes:
        if zoom_start is not None:
            dx = event.xdata - zoom_start[0]
            dy = event.ydata - zoom_start[1]
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
            ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
            zoom_start = (event.xdata, event.ydata)
            canvas.draw()
        modo_movimiento = False

def on_mouse_move(event):
    """Maneja los eventos de mover el mouse para zoom y movimiento."""
    global zoom_start, zoom_rect, modo_movimiento
    if zoom_rect and event.inaxes and modo_zoom:
        x0, y0 = zoom_start
        x1, y1 = event.xdata, event.ydata
        if x1 < x0:
            x0, x1 = x1, x0
        if y1 < y0:
            y0, y1 = y1, y0
        zoom_rect.set_width(x1 - x0)
        zoom_rect.set_height(y1 - y0)
        zoom_rect.set_xy((x0, y0))
        canvas.draw()
    elif modo_movimiento and event.inaxes:
        if zoom_start is not None:
            dx = event.xdata - zoom_start[0]
            dy = event.ydata - zoom_start[1]
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
            ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
            zoom_start = (event.xdata, event.ydata)
            canvas.draw()

def activar_mover():
    """Activa el modo de mover la gráfica con el mouse."""
    global modo_movimiento
    modo_movimiento = True
    boton_mover.configure(style='success.TButton')

def desactivar_mover():
    """Desactiva el modo de mover la gráfica con el mouse."""
    global modo_movimiento
    modo_movimiento = None
    boton_mover.configure(style='default.TButton')

def crear_menu_opciones():
    """Crea el menú de opciones para cargar datos y cambiar nombre."""
    menu_opciones = tk.Menu(root, tearoff=0)
    menu_opciones.add_command(label="Cargar Datos", command=cargar_datos)
    menu_opciones.add_command(label="Cambiar Nombre", command=cambiar_nombre_columna)
    return menu_opciones

def main():
    global root, frame_grafica, frame_toolbar, lista_columnas, canvas
    global boton_zoom_in, boton_zoom_out, boton_reset, boton_guardar, boton_mover
    global modo_zoom, modo_movimiento

    root = ttk.Window(themename="cyborg")
    root.title("Gráfico de Datos")
    
    root.configure(bg="white")

    # Inicializar variables
    modo_zoom = None
    modo_movimiento = None
    zoom_start = None
    zoom_rect = None

    # Crear frame para la barra de herramientas
    frame_toolbar = ttk.Frame(root, padding="10")
    frame_toolbar.pack(side=tk.TOP, fill=tk.X)

    # Crear botones para la barra de herramientas
    boton_opciones = ttk.Button(frame_toolbar, text="Opciones", command=lambda: menu_opciones.post(boton_opciones.winfo_rootx(), boton_opciones.winfo_rooty() + boton_opciones.winfo_height()))
    boton_opciones.pack(side=tk.LEFT, padx=5)

    boton_zoom_in = ttk.Button(frame_toolbar, text="Zoom In", command=zoom_entrada, style='default.TButton')
    boton_zoom_in.pack(side=tk.LEFT, padx=5)

    boton_zoom_out = ttk.Button(frame_toolbar, text="Zoom Out", command=zoom_salida, style='default.TButton')
    boton_zoom_out.pack(side=tk.LEFT, padx=5)

    boton_reset = ttk.Button(frame_toolbar, text="Restablecer Vista", command=restaurar_vista, style='default.TButton')
    boton_reset.pack(side=tk.LEFT, padx=5)

    boton_guardar = ttk.Button(frame_toolbar, text="Guardar Gráfica", command=guardar_grafica, style='default.TButton')
    boton_guardar.pack(side=tk.LEFT, padx=5)

    boton_mover = ttk.Button(frame_toolbar, text="Mover Gráfica", command=lambda: activar_mover() if modo_movimiento is None else desactivar_mover(), style='default.TButton')
    boton_mover.pack(side=tk.LEFT, padx=5)

    menu_opciones = crear_menu_opciones()

    # Crear frame para la gráfica
    frame_grafica = ttk.Frame(root, padding="10")
    frame_grafica.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Alternativa para CTkListbox usando ttk.Combobox
    lista_columnas = ttk.Combobox(frame_toolbar, state='readonly')
    lista_columnas.pack(side=tk.LEFT, padx=5)

    canvas = None

    root.mainloop()

if __name__ == "__main__":
    main()