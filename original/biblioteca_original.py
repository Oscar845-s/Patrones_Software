import datetime

class Biblioteca:
    """
    Clase principal. Maneja TODO el sistema:
    libros, usuarios, préstamos, multas y notificaciones.
    """

    def __init__(self):
        self.libros = []
        self.usuarios = []
        self.prestamos = []
        self.multas = []

    # ---- LIBROS ----

    def agregar_libro(self, titulo, autor, isbn, cantidad):
        for libro in self.libros:
            if libro["isbn"] == isbn:
                print("El libro ya existe.")
                return
        self.libros.append({
            "titulo": titulo,
            "autor": autor,
            "isbn": isbn,
            "cantidad": cantidad,
            "disponibles": cantidad
        })
        print(f"Libro '{titulo}' agregado.")

    def buscar_libro(self, isbn):
        for libro in self.libros:
            if libro["isbn"] == isbn:
                return libro
        return None

    def mostrar_libros(self):
        if not self.libros:
            print("No hay libros registrados.")
            return
        for libro in self.libros:
            print(f"[{libro['isbn']}] {libro['titulo']} - {libro['autor']} | Disponibles: {libro['disponibles']}")

    # ---- USUARIOS ----

    def agregar_usuario(self, nombre, id_usuario, tipo):
        for usuario in self.usuarios:
            if usuario["id"] == id_usuario:
                print("El usuario ya existe.")
                return
        self.usuarios.append({
            "nombre": nombre,
            "id": id_usuario,
            "tipo": tipo,   # "normal", "estudiante", "vip"
            "activo": True
        })
        print(f"Usuario '{nombre}' registrado.")

    def buscar_usuario(self, id_usuario):
        for usuario in self.usuarios:
            if usuario["id"] == id_usuario:
                return usuario
        return None

    def mostrar_usuarios(self):
        if not self.usuarios:
            print("No hay usuarios registrados.")
            return
        for u in self.usuarios:
            estado = "Activo" if u["activo"] else "Inactivo"
            print(f"[{u['id']}] {u['nombre']} | Tipo: {u['tipo']} | Estado: {estado}")

    # ---- PRÉSTAMOS ----
    # CODE SMELL: Long Method — este método hace demasiadas cosas
    # CODE SMELL: Magic Numbers — 14, 7, 21 sin nombres explicativos
    # CODE SMELL: Duplicate Code — validaciones repetidas en devolver_libro

    def prestar_libro(self, id_usuario, isbn):
        # Validar usuario
        usuario = None
        for u in self.usuarios:
            if u["id"] == id_usuario:
                usuario = u
                break
        if usuario is None:
            print("Error: Usuario no encontrado.")
            return
        if not usuario["activo"]:
            print("Error: El usuario está inactivo.")
            return

        # Validar libro
        libro = None
        for l in self.libros:
            if l["isbn"] == isbn:
                libro = l
                break
        if libro is None:
            print("Error: Libro no encontrado.")
            return
        if libro["disponibles"] <= 0:
            print("Error: No hay ejemplares disponibles.")
            return

        # Verificar que no tenga préstamos vencidos
        hoy = datetime.date.today()
        for p in self.prestamos:
            if p["id_usuario"] == id_usuario and p["devuelto"] == False:
                if hoy > p["fecha_limite"]:
                    print("Error: El usuario tiene préstamos vencidos. Debe pagar sus multas primero.")
                    return

        # Calcular fecha límite según tipo de usuario
        # CODE SMELL: Magic Numbers — 14, 7, 21 deberían ser constantes
        if usuario["tipo"] == "normal":
            dias = 14
        elif usuario["tipo"] == "estudiante":
            dias = 7
        elif usuario["tipo"] == "vip":
            dias = 21
        else:
            dias = 14

        fecha_limite = hoy + datetime.timedelta(days=dias)

        prestamo = {
            "id": len(self.prestamos) + 1,
            "id_usuario": id_usuario,
            "isbn": isbn,
            "fecha_prestamo": hoy,
            "fecha_limite": fecha_limite,
            "devuelto": False
        }
        self.prestamos.append(prestamo)
        libro["disponibles"] -= 1

        print(f"Préstamo registrado. Fecha límite: {fecha_limite}")

        # Notificar al usuario (código de notificación mezclado con lógica de negocio)
        # CODE SMELL: Feature Envy — esta lógica de notificación no pertenece aquí
        print(f"[NOTIFICACIÓN] Hola {usuario['nombre']}, tu préstamo de '{libro['titulo']}' vence el {fecha_limite}.")

    # CODE SMELL: Duplicate Code — repite validaciones de usuario y libro igual que prestar_libro
    def devolver_libro(self, id_usuario, isbn):
        # Validar usuario (DUPLICADO de prestar_libro)
        usuario = None
        for u in self.usuarios:
            if u["id"] == id_usuario:
                usuario = u
                break
        if usuario is None:
            print("Error: Usuario no encontrado.")
            return

        # Validar libro (DUPLICADO de prestar_libro)
        libro = None
        for l in self.libros:
            if l["isbn"] == isbn:
                libro = l
                break
        if libro is None:
            print("Error: Libro no encontrado.")
            return

        # Buscar préstamo activo
        prestamo = None
        for p in self.prestamos:
            if p["id_usuario"] == id_usuario and p["isbn"] == isbn and not p["devuelto"]:
                prestamo = p
                break
        if prestamo is None:
            print("Error: No se encontró un préstamo activo para este usuario y libro.")
            return

        hoy = datetime.date.today()
        prestamo["devuelto"] = True
        prestamo["fecha_devolucion"] = hoy
        libro["disponibles"] += 1

        # Calcular multa
        # CODE SMELL: Magic Numbers — 5, 3, 1 sin nombres explicativos
        # CODE SMELL: Duplicate Code — lógica de tipo de usuario repetida
        if hoy > prestamo["fecha_limite"]:
            dias_tarde = (hoy - prestamo["fecha_limite"]).days
            if usuario["tipo"] == "normal":
                multa = dias_tarde * 5
            elif usuario["tipo"] == "estudiante":
                multa = dias_tarde * 3
            elif usuario["tipo"] == "vip":
                multa = dias_tarde * 1
            else:
                multa = dias_tarde * 5

            self.multas.append({
                "id_usuario": id_usuario,
                "monto": multa,
                "pagada": False
            })
            print(f"Libro devuelto con {dias_tarde} días de retraso. Multa: ${multa}")
            # Notificación mezclada con lógica de negocio (Feature Envy)
            print(f"[NOTIFICACIÓN] Hola {usuario['nombre']}, tienes una multa de ${multa} pendiente.")
        else:
            print("Libro devuelto a tiempo. ¡Gracias!")
            print(f"[NOTIFICACIÓN] Hola {usuario['nombre']}, gracias por devolver '{libro['titulo']}' a tiempo.")

    def mostrar_prestamos(self):
        if not self.prestamos:
            print("No hay préstamos registrados.")
            return
        for p in self.prestamos:
            estado = "Devuelto" if p["devuelto"] else "Activo"
            print(f"Préstamo #{p['id']} | Usuario: {p['id_usuario']} | ISBN: {p['isbn']} | Límite: {p['fecha_limite']} | Estado: {estado}")

    def mostrar_multas(self):
        if not self.multas:
            print("No hay multas registradas.")
            return
        for m in self.multas:
            estado = "Pagada" if m["pagada"] else "Pendiente"
            print(f"Usuario: {m['id_usuario']} | Multa: ${m['monto']} | Estado: {estado}")



if __name__ == "__main__":
    bib = Biblioteca()

    bib.agregar_libro("Cien años de soledad", "Gabriel García Márquez", "978-0-06-088328-7", 3)
    bib.agregar_libro("El principito", "Antoine de Saint-Exupéry", "978-0-15-601219-5", 2)
    bib.agregar_libro("1984", "George Orwell", "978-0-45-152493-5", 1)

    bib.agregar_usuario("Ana López", "U001", "normal")
    bib.agregar_usuario("Carlos Ruiz", "U002", "estudiante")
    bib.agregar_usuario("María Torres", "U003", "vip")

    print("\n--- CATÁLOGO ---")
    bib.mostrar_libros()

    print("\n--- PRÉSTAMOS ---")
    bib.prestar_libro("U001", "978-0-06-088328-7")
    bib.prestar_libro("U002", "978-0-15-601219-5")
    bib.prestar_libro("U003", "978-0-45-152493-5")

    print("\n--- DEVOLUCIONES ---")
    bib.devolver_libro("U001", "978-0-06-088328-7")

    print("\n--- ESTADO FINAL ---")
    bib.mostrar_libros()
    bib.mostrar_prestamos()
    bib.mostrar_multas()
