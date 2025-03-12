#Se creo el archivo
nombre_archivo = 'tareas.txt'

#Se agregaron tareas
with open(nombre_archivo, "w") as archivo:
    archivo.write("Foro \n")
    archivo.write("Examen \n")
    archivo.write("Taller en grupo \n")

#Se imprime el contenido
print("\n Tareas ")
with open(nombre_archivo, 'r') as archivo:
    contenido = archivo.read()
    print(contenido)

#Se agrega una nueva tarea
with open(nombre_archivo, "a") as archivo:
    archivo.write("Video explicativo \n")

#Se imprime con la nueva tarea
print("\n Tareas ")
with open(nombre_archivo, 'r') as archivo:
    contenido = archivo.read()
    print(contenido)

#Se elimina una tarea ya completada
with open(nombre_archivo, 'r') as archivo:
    lineas = archivo.readlines()
    lineas = [linea for linea in lineas if "Examen" not in linea]
with open(nombre_archivo, 'w') as archivo:
    archivo.writelines(lineas)
    
#Se imprime el archivo sin la tarea completada
print("\n Tareas ")
with open(nombre_archivo, 'r') as archivo:
    contenido = archivo.read()
    print(contenido)