import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk
import json
import pandas as pd
 
def seleccionar_archivo():
    """Abre un cuadro de diálogo para seleccionar un archivo y devuelve su ruta."""
    return filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])

def crear_seccion_ingreso_datos():
    """Crea una sección en la interfaz principal para ingresar datos manualmente en 5 columnas."""
    global frame_ingreso_datos, entradas

    # Frame para la sección de ingreso de datos
    frame_ingreso_datos = ttk.Frame(root, padding="10")
    frame_ingreso_datos.pack(side=tk.TOP, fill=tk.X, pady=10)

    entradas = []
    scrollbar_entradas = []

    # Definir los nombres personalizados para las columnas
    nombres_columnas_personalizados = [
        "columna 1",
        "columna 2",
        "columna 3",
        "columna 4",
        "columna 5"
    ]

    for i in range(5):
        columna_frame = ttk.Frame(frame_ingreso_datos)
        columna_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

        etiqueta = ttk.Label(columna_frame, text=nombres_columnas_personalizados[i])
        etiqueta.pack(side=tk.TOP, pady=5)

        entrada = tk.Text(columna_frame, height=20, width=15, wrap="none")
        entrada.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_vertical = ttk.Scrollbar(columna_frame, orient="vertical", command=entrada.yview)
        scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)
        entrada.config(yscrollcommand=scrollbar_vertical.set)

        scrollbar_horizontal = ttk.Scrollbar(frame_ingreso_datos, orient="horizontal", command=entrada.xview)
        scrollbar_horizontal.grid(row=1, column=i, sticky="ew")
        entrada.config(xscrollcommand=scrollbar_horizontal.set)

        entradas.append(entrada)
        scrollbar_entradas.append((scrollbar_vertical, scrollbar_horizontal))

    # Frame para los botones al lado de las columnas
    frame_botones = ttk.Frame(frame_ingreso_datos)
    frame_botones.grid(row=0, column=5, padx=10, pady=10, sticky="nsew")

    boton_visualizar = ttk.Button(frame_botones, text="Visualizar Gráfica", command=visualizar_datos_ingresados)
    boton_visualizar.pack(side=tk.TOP, pady=5)

    boton_guardar = ttk.Button(frame_botones, text="Guardar como CSV/TXT", command=guardar_datos_ingresados)
    boton_guardar.pack(side=tk.TOP, pady=5)

    frame_ingreso_datos.pack_forget()  # Ocultarlo inicialmente

def toggle_seccion_ingreso_datos():
    """Muestra u oculta la sección de ingreso de datos manualmente."""
    if frame_ingreso_datos.winfo_ismapped():
        frame_ingreso_datos.pack_forget()
    else:
        frame_ingreso_datos.pack(side=tk.TOP, fill=tk.X, pady=10)

def visualizar_datos_ingresados():
    """Toma los datos ingresados y los visualiza en la gráfica."""
    global canvas, fig, ax, nombres_columnas

    # Recoger los datos de las entradas
    columnas_datos = []
    for entrada in entradas:
        datos_texto = entrada.get("1.0", tk.END).strip().split('\n')
        datos_fila = [float(valor) for valor in datos_texto if valor]
        columnas_datos.append(datos_fila)

    # Validar que todas las columnas tengan la misma longitud
    max_length = max(len(col) for col in columnas_datos)
    for i in range(len(columnas_datos)):
        if len(columnas_datos[i]) < max_length:
            columnas_datos[i].extend([0] * (max_length - len(columnas_datos[i])))  # Rellenar con ceros

    # Definir los nombres personalizados para las columnas
    nombres_columnas = [
        "Inferior de la caja",
        "Superior de la caja",
        "Interior de la caja",
        "Externa de la caja 1",
        "Externa de la caja 2"
    ]

    # Graficar los datos
    if canvas:
        canvas.get_tk_widget().destroy()

    fig, ax = plt.subplots(figsize=(10, 6))
    colores = ['blue', 'orange', 'green', 'red', 'purple']

    for idx, col in enumerate(columnas_datos):
        ax.plot(range(len(col)), col, label=nombres_columnas[idx], color=colores[idx % len(colores)])

    # Añadir líneas punteadas y etiquetas de los ejes
    ax.axhline(y=2, color='r', linestyle='--', label='Límite Inferior')
    ax.axhline(y=8, color='r', linestyle='--', label='Límite Superior')
    ax.set_xlabel('Horas')
    ax.set_ylabel('Temperatura (°C)')

    ax.legend(loc='upper right')
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def guardar_datos_ingresados():
    """Guarda los datos ingresados manualmente en un archivo .txt o .csv."""
    columnas_datos = []
    for entrada in entradas:
        datos_texto = entrada.get("1.0", tk.END).strip().split('\n')
        datos_fila = [float(valor) for valor in datos_texto if valor]
        columnas_datos.append(datos_fila)

    # Validar que todas las columnas tengan la misma longitud
    max_length = max(len(col) for col in columnas_datos)
    for i in range(len(columnas_datos)):
        if len(columnas_datos[i]) < max_length:
            columnas_datos[i].extend([0] * (max_length - len(columnas_datos[i])))  # Rellenar con ceros

    # Guardar los datos en un archivo
    archivo_guardar = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivo de texto", "*.txt"), ("Archivo CSV", "*.csv")])

    if archivo_guardar.endswith(".txt"):
        np.savetxt(archivo_guardar, np.column_stack(columnas_datos), delimiter='\t', fmt='%0.1f')
    else:
        pd.DataFrame(np.column_stack(columnas_datos)).to_csv(archivo_guardar, index=False)

    messagebox.showinfo("Éxito", f"Archivo guardado exitosamente en {archivo_guardar}.")


def seleccionar_y_procesar_csv():
    """Permite seleccionar 5 archivos CSV, extrae los primeros 1000 datos de la columna °C y los guarda en un archivo .txt."""
    archivos_csv = filedialog.askopenfilenames(filetypes=[("Archivos CSV", "*.csv")], title="Selecciona hasta 5 archivos CSV", multiple=True)
    
    if not archivos_csv or len(archivos_csv) == 0:
        messagebox.showwarning("Advertencia", "No se seleccionaron archivos CSV.")
        return

    # Limitar a 5 archivos
    archivos_csv = archivos_csv[:5]
    
    # Para almacenar los datos extraídos
    columnas_datos = []
    nombres_archivos = []

    for archivo in archivos_csv:
        try:
            # Leer el archivo CSV
            df = pd.read_csv(archivo)
            
            # Verificar si la columna °C existe
            if '°C' not in df.columns:
                messagebox.showwarning("Advertencia", f"El archivo {archivo} no contiene una columna °C.")
                continue
            
            # Extraer los primeros 1,000 datos de la columna °C
            datos_c = df['°C'].head(1000).to_numpy()

            # Si tiene menos de 1000 datos, rellenar con ceros
            if len(datos_c) < 1000:
                datos_c = np.pad(datos_c, (0, 1000 - len(datos_c)), 'constant')

            columnas_datos.append(datos_c)
            nombres_archivos.append(archivo.split("/")[-1])
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el archivo {archivo}: {e}")
    
    if not columnas_datos:
        messagebox.showwarning("Advertencia", "No se pudo procesar ningún archivo CSV.")
        return

    # Combinar las columnas en un archivo TXT
    generar_archivo_txt(columnas_datos, nombres_archivos)

def generar_archivo_txt(columnas_datos, nombres_archivos):
    """Genera un archivo .txt con las columnas de datos procesadas."""
    archivo_guardar = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivo de texto", "*.txt")], title="Guardar archivo TXT")
    
    if  not archivo_guardar:
        messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo para guardar.")
        return
    
    # Guardar las columnas de datos en un archivo TXT
    datos_combinados = np.column_stack(columnas_datos)
    np.savetxt(archivo_guardar, datos_combinados, delimiter='\t', fmt='%0.1f')

    messagebox.showinfo("Éxito", f"El archivo {archivo_guardar} ha sido generado exitosamente.")
    
    # Mostrar los nombres de los archivos y los colores de las gráficas
    mostrar_colores_y_nombres(nombres_archivos)

def mostrar_colores_y_nombres(nombres_archivos):
    """Muestra los nombres de los archivos CSV seleccionados y sus colores asociados."""
    colores = ['blue', 'orange', 'green', 'red', 'purple']
    
    texto = "Archivos seleccionados y sus colores en la gráfica:\n"
    for idx, nombre in enumerate(nombres_archivos):
        texto += f"{nombre} -> {colores[idx % len(colores)]}\n"
    
    messagebox.showinfo("Archivos y Colores", texto)

# Función para seleccionar un archivo
def cambiar_nombre_columna():
    """Permite cambiar el nombre de una columna seleccionada y actualiza la gráfica."""
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


# Función para configurar las líneas punteadas
def configurar_lineas_punteadas():
    """Permite configurar los valores de las líneas punteadas en el gráfico."""
    global min_punteado, max_punteado
    min_punteado = simpledialog.askfloat("Configurar Línea Punteada", "Ingrese el valor para la línea punteada mínima:", initialvalue=min_punteado)
    max_punteado = simpledialog.askfloat("Configurar Línea Punteada", "Ingrese el valor para la línea punteada máxima:", initialvalue=max_punteado)
    if min_punteado is not None and max_punteado is not None:
        actualizar_grafica()

def cargar_datos():
    """Carga los datos desde un archivo .txt y actualiza la gráfica."""
    global data, num_columnas, seleccion_columnas, nombres_columnas

    archivo = seleccionar_archivo()
    
    if archivo:
        try:
            # Leer todos los datos del archivo .txt sin excluir la primera columna
            datos = np.loadtxt(archivo, delimiter='\t')
            
            # Generar una columna de tiempo en función del número de filas
            tiempos_generados = np.arange(0, len(datos) * 0.08, 0.08)  # Ajusta el rango y el incremento según sea necesario
            
            # Combinar la columna de tiempos con los datos
            data = np.column_stack((tiempos_generados, datos))
            
            # Asegurarse de que todas las columnas se seleccionen
            num_columnas = datos.shape[1]  # Cambia aquí para que se detecten todas las columnas
            seleccion_columnas = list(range(num_columnas))
            nombres_columnas = [f"Serie {i+1}" for i in range(num_columnas)]
            
            # Actualizar la lista de columnas en el combobox
            lista_columnas['values'] = nombres_columnas
            
            # Llamar a la función para actualizar la gráfica
            actualizar_grafica()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo. Error: {e}")
    else:
        messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo.")
def actualizar_grafica():
    """Actualiza la gráfica con los datos cargados y la configuración actual."""
    global canvas, fig, ax

    if canvas:
        canvas.get_tk_widget().destroy()

    fig, ax = plt.subplots(figsize=(10, 6))

    # Definir colores fijos
    colores = ['blue', 'orange', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']

    # Graficar los datos
    for idx, col in enumerate(seleccion_columnas):
        serie = data[:, col + 1]
        tiempo = data[:, 0]
        
        # Filtrar los datos para considerar el rango de horas de 2 a 48
        serie_hasta_hora_45 = serie[(tiempo >= 2) & (tiempo <= 48)]

        # Calcular el porcentaje de valores dentro del rango de 2 a 8°C en ese intervalo de tiempo
        porcentaje_en_rango = np.sum((serie_hasta_hora_45 >= 2) & (serie_hasta_hora_45 <= 8)) / len(serie_hasta_hora_45)

        # Asignar color verde si el porcentaje es mayor o igual al 95%
        color = 'green' if porcentaje_en_rango >= 0.95 else colores[idx % len(colores)]
        
        # Graficar la serie con el color asignado
        ax.plot(tiempo, serie, label=nombres_columnas[col], color=color)


    if min_punteado is not None:
        ax.axhline(y=min_punteado, color='r', linestyle='--', label='Mínimo')
    if max_punteado is not None:
        ax.axhline(y=max_punteado, color='r', linestyle='--', label='Máximo')
        
    ax.set_xlabel('Tiempo (horas)')
    ax.set_ylabel('Temperatura (°C)')
    
    # Configurar los ticks del eje x de 1 en 1
    max_tiempo = max(data[:, 0])
    ticks_x = np.arange(0, max_tiempo + 1, 1)
    ax.set_xticks(ticks_x)
    ax.set_xticklabels([f'{tick:.0f}' if tick % 5 == 0 else '' for tick in ticks_x])
    
    # Añadir marcas en los ticks que no tienen etiqueta (los múltiplos de 5 tienen etiqueta)
    for tick in ticks_x:
        if tick % 5 != 0:
            ax.axvline(x=tick, color='gray', linestyle='--', linewidth=0.5)
    
    # Configurar los ticks del eje y de 1 en 1
    min_temp, max_temp = np.min(data[:, 1:]), np.max(data[:, 1:])
    ticks_y = np.arange(np.floor(min_temp), np.ceil(max_temp) + 1, 1)
    ax.set_yticks(ticks_y)
    ax.set_yticklabels([f'{tick:.0f}' if tick % 2 == 0 else '' for tick in ticks_y])
    
    # Añadir marcas en los ticks que no tienen etiqueta (los múltiplos de 2 tienen etiqueta)
    for tick in ticks_y:
        if tick % 2 != 0:
            ax.axhline(y=tick, color='gray', linestyle='--', linewidth=0.5)
    
    ax.legend(loc='upper right')
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Conectar eventos de mouse para zoom y movimiento
    canvas.mpl_connect('button_press_event', on_mouse_press)
    canvas.mpl_connect('button_release_event', on_mouse_release)
    canvas.mpl_connect('motion_notify_event', on_mouse_move)
    canvas.mpl_connect('scroll_event', on_mouse_scroll)  # Conectar el evento de scroll

# Función para guardar la gráfica en un archivo
def guardar_grafica():
    """Guarda la gráfica en un archivo."""
    archivo_guardar = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Imagen PNG", "*.png")])
    if archivo_guardar:
        fig.savefig(archivo_guardar)

# Funciones para zoom
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

# Función para guardar nombres en un archivo JSON
def guardar_nombres_json():
    """Guarda los nombres de las columnas en un archivo JSON."""
    with open('nombres_columnas.json', 'w') as f:
        json.dump(nombres_columnas, f)

# Funciones para manejo de eventos del mouse
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
            ax.set_xlim(x0, x1)
            ax.set_ylim(y0, y1)
            zoom_rect.remove()
            zoom_rect = None
            canvas.draw()
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

def on_mouse_scroll(event):
    """Maneja el evento de desplazamiento del mouse para zoom con la tecla Ctrl."""
    global ax, canvas
    if event.inaxes:
        zoom_factor = 1.1
        if event.button == 'up':
            # Zoom in
            scale = zoom_factor
        elif event.button == 'down':
            # Zoom out
            scale = 1 / zoom_factor
        else:
            scale = 1
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_center = (xlim[1] + xlim[0]) / 2
        y_center = (ylim[1] + ylim[0]) / 2
        width = (xlim[1] - xlim[0]) * scale
        height = (ylim[1] - ylim[0]) * scale
        ax.set_xlim(x_center - width / 2, x_center + width / 2)
        ax.set_ylim(y_center - height / 2, y_center + height / 2)
        canvas.draw()

# Funciones para activar y desactivar el movimiento de la gráfica
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

# Función para crear el menú de opciones
def crear_menu_opciones():
    """Crea el menú de opciones para cargar datos, cambiar nombre y configurar líneas punteadas."""
    menu_opciones = tk.Menu(root, tearoff=0)
    menu_opciones.add_command(label="Cargar Datos TXT", command=cargar_datos)
    menu_opciones.add_command(label="Seleccionar y Procesar CSV", command=seleccionar_y_procesar_csv)
    menu_opciones.add_command(label="Cambiar Nombre", command=cambiar_nombre_columna)
    menu_opciones.add_command(label="Configurar Líneas Punteadas", command=configurar_lineas_punteadas)
    return menu_opciones

# Función principal para iniciar la aplicación
def main():
    global root, frame_grafica, frame_toolbar, lista_columnas, canvas
    global boton_zoom_in, boton_zoom_out, boton_reset, boton_guardar, boton_mover
    global modo_zoom, modo_movimiento, min_punteado, max_punteado

    root = ttk.Window(themename="cyborg")
    root.title("Gráfico de Datos")

    root.configure(bg="white")

    # Inicializar variables
    modo_zoom = None
    modo_movimiento = None
    zoom_start = None
    zoom_rect = None
    min_punteado = 2  # Valor inicial para la línea punteada mínima
    max_punteado = 8  # Valor inicial para la línea punteada máxima

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

    # Nuevo botón para mostrar/ocultar la sección de ingreso de datos
    boton_ingresar_datos = ttk.Button(frame_toolbar, text="Ingresar Datos", command=toggle_seccion_ingreso_datos, style='default.TButton')
    boton_ingresar_datos.pack(side=tk.LEFT, padx=5)

    menu_opciones = crear_menu_opciones()

    # Crear frame para la gráfica
    frame_grafica = ttk.Frame(root, padding="10")
    frame_grafica.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Alternativa para CTkListbox usando ttk.Combobox
    lista_columnas = ttk.Combobox(frame_toolbar, state='readonly')
    lista_columnas.pack(side=tk.LEFT, padx=5)

    canvas = None

    crear_seccion_ingreso_datos()  # Crear la sección de ingreso de datos manual

    root.mainloop()

if __name__ == "__main__":
    main()
