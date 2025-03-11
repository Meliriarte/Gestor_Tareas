class GestorTareas:
    def __init__(self, nombre_archivo):
        self.nombre_archivo = nombre_archivo

    def agregar_tarea(self, tarea):
        """Agrega una nueva tarea al archivo."""
        with open(self.nombre_archivo, "a") as archivo:
            archivo.write(tarea + "\n")

    def mostrar_tareas(self):
        """Muestra todas las tareas del archivo."""
        with open(self.nombre_archivo, 'r') as archivo:
            contenido = archivo.read()
            print(contenido)

    def eliminar_tarea(self, tarea):
        """Elimina una tarea del archivo."""
        with open(self.nombre_archivo, 'r') as archivo:
            lineas = archivo.readlines()
            lineas = [linea for linea in lineas if tarea not in linea]
        
        # Sobrescribimos el archivo con las líneas filtradas
        with open(self.nombre_archivo, 'w') as archivo:
            archivo.writelines(lineas)

# Crear instancia de GestorTareas y usarla
nombre_archivo = 'tareas.txt'

# Crear una instancia de GestorTareas
gestor = GestorTareas(nombre_archivo)

# Se agregan tareas iniciales
with open(nombre_archivo, "w") as archivo:  # Esto limpia el archivo antes de agregar tareas
    archivo.write("Foro \n")
    archivo.write("Examen \n")
    archivo.write("Taller en grupo \n")

# Mostrar tareas iniciales
print("\nTareas iniciales:")
gestor.mostrar_tareas()

# Agregar una nueva tarea
gestor.agregar_tarea("Video explicativo")

# Mostrar tareas con la nueva tarea
print("\nTareas después de agregar 'Video explicativo':")
gestor.mostrar_tareas()

# Eliminar tarea completada ("Examen")
gestor.eliminar_tarea("Examen")

# Mostrar tareas después de eliminar la tarea "Examen"
print("\nTareas después de eliminar 'Examen':")
gestor.mostrar_tareas()
