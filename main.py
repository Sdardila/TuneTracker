import requests
import os
from datetime import timedelta


def mostrar_bienvenida():
    print(
        '''
TuneTracker es una app que analiza playlists de Spotify para ofrecerte estadísticas detalladas sobre tus canciones favoritas. Desde los géneros más escuchados hasta la energía y popularidad de cada track, TuneTracker convierte tu música en datos visuales y fáciles de entender. Ideal para curiosos musicales, investigadores, o quienes simplemente quieren conocer su perfil sonoro al detalle.

Requisitos previos:
-Instalar la ultima version de Python (Pagina oficial: https://www.python.org/).
-Instalar un editor de codigo (Editor recomendado: https://code.visualstudio.com/Download).
-En caso de no tener, crear una cuenta de Spotify.
-Ingresar a Spotify for Developers e iniciar sesion con una cuenta de Spotify (Premium o no Premium) (Pagina: https://developer.spotify.com/).
-Crear una app en spotify de tipo Web API. 
-Dentro de esta app se encuentran las credenciales client id y client secret. Ingresarlas cuando se pidan.
        '''
    )


def obtener_token():
    while True:
        try:
            CLIENT_ID = input('Ingrese el Client ID: ')
            CLIENT_SECRET = input('Ingrese el Client Secret: ')
            token = requests.post('https://accounts.spotify.com/api/token',
                                  data={'grant_type': 'client_credentials',
                                        'client_id': CLIENT_ID,
                                        'client_secret': CLIENT_SECRET}).json()['access_token']
            print('Token obtenido satisfactoriamente.\n')
            return token
        except:
            print('Hubo un error en la obtencion del token. Verifique las credenciales e ingreselas de nuevo.\n')


def obtener_playlist(token):
    while True:
        try:
            link_playlist = input("Ingrese el link del playlist: ")
            playlist_id = link_playlist.split('/')[4].split('?')[0]
            nombre_playlist = requests.get(
                f'https://api.spotify.com/v1/playlists/{playlist_id}',
                headers={'Authorization': f'Bearer {token}'}
            ).json()['name'].strip()
            print(f'Nombre de la playlist: {nombre_playlist}')
            canciones = []
            url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
            while url:
                response = requests.get(url, headers={'Authorization': f'Bearer {token}'}).json()
                canciones.extend(response['items'])
                url = response.get('next')
            print(f'Cancion(es) de la playlist <{nombre_playlist}> obtenidas satisfactoriamente')
            return nombre_playlist, canciones
        except:
            print('Hubo un error con la obtencion de los datos de la Playlist. Verifique la URL.')


def crear_archivos(nombre_playlist, canciones):
    diccionario_artistas = {}
    with open(f'Canciones {nombre_playlist}.txt', 'w', encoding='utf-8') as file, \
            open(f'Artistas {nombre_playlist}.txt', 'w', encoding='utf-8') as file2:
        for c in canciones:
            try:
                track = c['track']
                if not track:
                    continue
                id_cancion = track['id']
                nombre_cancion = track['name']
                duracion_ms_cancion = int(track['duration_ms'])
                popularidad_cancion = int(track['popularity'])
                lista_artistas = [a['name'] for a in track['artists']]
                for a in lista_artistas:
                    if a not in diccionario_artistas:
                        diccionario_artistas[a] = []
                    diccionario_artistas[a].append(f"{nombre_cancion}:{id_cancion}")
                file.write(
                    f"{id_cancion}//{nombre_cancion}//{duracion_ms_cancion}//{popularidad_cancion}//{','.join(lista_artistas)}\n")
            except:
                continue
        for artista, canciones in diccionario_artistas.items():
            file2.write(f"{artista}//{';'.join(canciones)}\n")
        print("Archivo de canciones y artistas creados satisfactoriamente.\n")
    return diccionario_artistas


def artista_mas_canciones(nombre_playlist):
    max_c = 0
    with open(f'Artistas {nombre_playlist}.txt', 'r', encoding='utf-8') as f:
        for linea in f:
            artista = linea.strip().split('//')[0]
            canciones = linea.strip().split('//')[1]
            cantidad = len(canciones.split(';'))
            if cantidad > max_c:
                max_c = cantidad
                max_a = artista
    print('Artista con mayor numero de canciones: ')
    print(f"- {max_a} ({max_c} canciones)\n")


def artista_mas_popular(nombre_playlist):
    popularidad = {}
    with open(f'Canciones {nombre_playlist}.txt', 'r', encoding='utf-8') as f:
        for linea in f:
            partes = linea.strip().split('//')
            pop = int(partes[3])
            artistas = partes[4].split(',')
            for a in artistas:
                if a not in popularidad:
                    popularidad[a] = []
                popularidad[a].append(pop)
    max_artista = ''
    max_prom = 0
    for a in popularidad:
        promedio = sum(popularidad[a]) / len(popularidad[a])
        if promedio > max_prom:
            max_prom = promedio
            max_artista = a
    print(f"- {max_artista} ({max_prom:.2f} promedio)\n")


def peso_archivos(nombre_playlist):
    def peso_archivo(nombre_archivo):
        print(f"- Nombre archivo: {nombre_archivo}")
        total_bytes = os.path.getsize(nombre_archivo)
        total_registros = 0
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            for linea in f:
                total_registros += 1
        print(f'- Bytes: {total_bytes}')
        print(f'- Registros {total_registros}')
        if total_registros > 0:
            promedio_registro = total_bytes / total_registros
            print(f"- Tamaño promedio de registro en <{nombre_archivo}>: {promedio_registro:.2f} bytes\n")
        else:
            print(f"- El archivo <{nombre_archivo}> está vacío.\n")

    print('Peso archivos: ')
    peso_archivo(f'Canciones {nombre_playlist}.txt')
    peso_archivo(f'Artistas {nombre_playlist}.txt')


def buscar_canciones_por_artista(nombre_playlist):
    artista_dado = (input("Ingrese el nombre del artista: ")).strip()
    lecturas = 0
    cantidad_canciones = 0
    with open(f'Canciones {nombre_playlist}.txt', 'r', encoding='utf-8') as f:
        canciones_encontradas = []
        for linea in f:
            lecturas += 1
            partes = linea.strip().split('//')
            artistas = partes[4].split(',')
            for a in artistas:
                if artista_dado.lower() == a.strip().lower():
                    cantidad_canciones += 1
                    canciones_encontradas.append(f'{partes[1]}')
    print(f"- Se encontraron {cantidad_canciones} canciones tras {lecturas} lecturas totales.\n")
    print(f"Lista de canciones encontradas de {artista_dado}: ")
    if len(canciones_encontradas) > 0:
        for cancion in canciones_encontradas:
            print(f'- {cancion}')
        print("\n")
    else:
        print(f'- No se encontraron canciones de {artista_dado}\n')


def canciones_mayor_duracion_promedio(nombre_playlist):
    duracion_total = 0
    total_canciones = 0
    with open(f'Canciones {nombre_playlist}.txt', 'r', encoding='utf-8') as f:
        for linea in f:
            partes = linea.strip().split('//')
            try:
                duracion_total += int(partes[2])
                total_canciones += 1
            except ValueError:
                continue
        duracion_promedio = (duracion_total / total_canciones)
        duracion_promedio_minutos_segundos = f"{timedelta(milliseconds=duracion_promedio).seconds // 60}:{timedelta(milliseconds=duracion_promedio).seconds % 60}"
        print(f'Canciones con duracion mayor al promedio (Duracion promedio: {duracion_promedio_minutos_segundos}): ')
    with open(f'Canciones {nombre_playlist}.txt', 'r', encoding='utf-8') as f:
        canciones_duracion_mayor_promedio = []
        for linea in f:
            try:
                partes = linea.strip().split('//')
                duracion_cancion = (int(partes[2]))
                if duracion_cancion > duracion_promedio:
                    minutos = timedelta(milliseconds=duracion_cancion).seconds // 60
                    segundos = timedelta(milliseconds=duracion_cancion).seconds % 60
                    canciones_duracion_mayor_promedio.append(f'{partes[1]} | {minutos}:{segundos}')
            except ValueError:
                continue
    for cancion in canciones_duracion_mayor_promedio:
        print(f'  - {cancion}')
    print('\n')


def ordenar_canciones_por_popularidad(nombre_playlist):
    with open(f'Canciones {nombre_playlist}.txt', 'r', encoding='utf-8') as f:
        canciones_ordenadas = f.readlines()
    canciones_ordenadas.sort(key=lambda x: int(x.split('//')[3]), reverse=True)
    with open(f'Canciones {nombre_playlist}.txt', 'w', encoding='utf-8') as f:
        f.writelines(canciones_ordenadas)


def agregar_nueva_cancion(nombre_playlist, diccionario_artistas):
    print('Ingrese los datos de la nueva cancion: ')
    id = input('Id: ').strip()
    nombre = input('Nombre: ').strip()
    while True:
        try:
            duracion_ms = int(input('Duracion en ms: ').strip())
            break
        except:
            print("Ingrese un valor entero y numerico")
    while True:
        try:
            popularidad = int(input('Popularidad: ').strip())
            break
        except:
            print("Ingrese un valor entero y numerico")
    autores = input('Autor o autores (separelos por comas): ').split(',')
    autores = [a.strip() for a in autores]
    datos_cancion_nueva = f'{id}//{nombre}//{duracion_ms}//{popularidad}//{",".join(autores)}\n'
    with open(f'Canciones {nombre_playlist}.txt', 'r', encoding='utf-8') as f:
        canciones_ordenadas = f.readlines()
    canciones_ordenadas.append(datos_cancion_nueva)
    canciones_ordenadas.sort(key=lambda x: int(x.split('//')[3]), reverse=True)
    for a in autores:
        if a not in diccionario_artistas:
            diccionario_artistas[a] = []
        diccionario_artistas[a].append(f"{nombre}:{id}")
    with open(f'Canciones {nombre_playlist}.txt', 'w', encoding='utf-8') as f:
        f.writelines(canciones_ordenadas)
    with open(f'Artistas {nombre_playlist}.txt', 'w', encoding='utf-8') as f2:
        for artista, canciones in diccionario_artistas.items():
            f2.write(f"{artista}//{';'.join(canciones)}\n")
    print('Nuevos datos guardados satisfactoriamente.\n')


def buscar_por_popularidad_lineal(nombre_playlist):
    print(
        'En este inciso usted ingresara una popularidad y se devolvera la cancion o las canciones con dicha popularidad.')
    while True:
        try:
            popularidad_a_buscar = int(input('Ingrese una popularidad: '))
            break
        except:
            print("Ingrese un valor entero y numerico")
    with open(f'Canciones {nombre_playlist}.txt', 'r', encoding='utf-8') as f:
        canciones_mayor_pop = []
        for linea in f:
            partes = linea.split('//')
            if int(partes[3]) == popularidad_a_buscar:
                canciones_mayor_pop.append(partes[1])
    if len(canciones_mayor_pop) == 0:
        print(f"No se encontraron canciones con esa popularidad. ")
        print('\n')
    else:
        print(f"Las canciones con popularidad igual a {popularidad_a_buscar} son:")
        for cancion in canciones_mayor_pop:
            print(f'- {cancion}')
        print('\n')


def buscar_por_popularidad_binaria(nombre_playlist):
    print(
        'En este inciso se le pedira una popularidad. En este caso, se hara uso de la busqueda binaria para encontrar una cancion con dicha popularidad.')
    while True:
        try:
            popularidad_a_buscar = int(input('Ingrese una popularidad: '))
            break
        except:
            print("Ingrese un valor entero y numerico")
    with open(f'Canciones {nombre_playlist}.txt', 'r', encoding='utf-8') as f:
        datos = f.readlines()
    izq = 0
    der = len(datos) - 1
    encontrada = False
    while izq <= der and not encontrada:
        mid = (izq + der) // 2
        pop = int(datos[mid].split('//')[3])
        if pop == popularidad_a_buscar:
            print(f"- Encontrada: {datos[mid]}")
            encontrada = True
        elif popularidad_a_buscar > pop:
            der = mid - 1
        else:
            izq = mid + 1
    if not encontrada:
        print('No se encontro elemento con esa popularidad')


def generar_indice_artistas(nombre_playlist):
    artistas_ordenados_letra = []
    with open(f'Artistas {nombre_playlist}.txt', 'r', encoding='utf-8') as f, open(
            f'Indice {nombre_playlist}.txt', 'w', encoding='utf-8') as idx:
        for linea in f:
            artistas_ordenados_letra.append(linea)
            artistas_ordenados_letra.sort(key=lambda x: x.split('//')[0])
        contar = 1
        for i in artistas_ordenados_letra:
            nombre = i.split('//')[0]
            canciones = i.split('//')[1].split(',')
            idx.write(f'{contar}.')
            for c in canciones:
                contar += 1
                idx.write(f'{nombre}//{c.strip()}')
            idx.write('\n')
        print('Indice de artistas creado satisfactoriamente.\n')


def mostrar_menu():
    print("\nMENU PRINCIPAL")
    print("1. Obtener token de autenticación")
    print("2. Analizar playlist")
    print("3. Cambiar playlist")
    print("4. Mostrar artista con más canciones")
    print("5. Mostrar artista más popular")
    print("6. Mostrar peso de archivos")
    print("7. Buscar canciones por artista")
    print("8. Mostrar canciones con duración mayor al promedio")
    print("9. Ordenar canciones por popularidad")
    print("10. Agregar nueva canción")
    print("11. Buscar canciones por popularidad (búsqueda lineal)")
    print("12. Buscar canciones por popularidad (búsqueda binaria)")
    print("13. Generar índice de artistas")
    print("14. Salir")
    opcion = input("Seleccione una opción: ")
    return opcion


def main():
    mostrar_bienvenida()
    token = None
    nombre_playlist = None
    diccionario_artistas = None

    while True:
        opcion = mostrar_menu() 

        if opcion == "1":
            token = obtener_token()
        elif opcion == "2":
            if token is None:
                print("Primero debe obtener el token (opción 1)")
            else:
                nombre_playlist, canciones = obtener_playlist(token)
                diccionario_artistas = crear_archivos(nombre_playlist, canciones)
        elif opcion == "3":
            if token is None:
                print("Primero debe obtener el token (opción 1)")
            else:
                nombre_playlist, canciones = obtener_playlist(token)
                diccionario_artistas = crear_archivos(nombre_playlist, canciones)
                print('Playlist cambiada satisfactoriamente.')
        elif opcion == "4":
            if nombre_playlist is None:
                print("Primero debe analizar una playlist (opción 2)")
            else:
                artista_mas_canciones(nombre_playlist)
        elif opcion == "5":
            if nombre_playlist is None:
                print("Primero debe analizar una playlist (opción 2)")
            else:
                artista_mas_popular(nombre_playlist)
        elif opcion == "6":
            if nombre_playlist is None:
                print("Primero debe analizar una playlist (opción 2)")
            else:
                peso_archivos(nombre_playlist)
        elif opcion == "7":
            if nombre_playlist is None:
                print("Primero debe analizar una playlist (opción 2)")
            else:
                buscar_canciones_por_artista(nombre_playlist)
        elif opcion == "8":
            if nombre_playlist is None:
                print("Primero debe analizar una playlist (opción 2)")
            else:
                canciones_mayor_duracion_promedio(nombre_playlist)
        elif opcion == "9":
            if nombre_playlist is None:
                print("Primero debe analizar una playlist (opción 2)")
            else:
                ordenar_canciones_por_popularidad(nombre_playlist)
                print("Canciones ordenadas por popularidad.\n")
        elif opcion == "10":
            if nombre_playlist is None:
                print("Primero debe analizar una playlist (opción 2)")
            else:
                agregar_nueva_cancion(nombre_playlist, diccionario_artistas)
        elif opcion == "11":
            if nombre_playlist is None:
                print("Primero debe analizar una playlist (opción 2)")
            else:
                buscar_por_popularidad_lineal(nombre_playlist)
        elif opcion == "12":
            if nombre_playlist is None:
                print("Primero debe analizar una playlist (opción 2)")
            else:
                buscar_por_popularidad_binaria(nombre_playlist)
        elif opcion == "13":
            if nombre_playlist is None:
                print("Primero debe analizar una playlist (opción 2)")
            else:
                generar_indice_artistas(nombre_playlist)
        elif opcion == "14":
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción del 1 al 14.")

main()