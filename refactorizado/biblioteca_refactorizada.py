import datetime
from abc import ABC, abstractmethod
from typing import List, Optional

# CONSTANTES
# CODE SMELL corregido: Magic Numbers

DIAS_PRESTAMO_NORMAL     = 14
DIAS_PRESTAMO_ESTUDIANTE = 7
DIAS_PRESTAMO_VIP        = 21

MULTA_DIARIA_NORMAL      = 5
MULTA_DIARIA_ESTUDIANTE  = 3
MULTA_DIARIA_VIP         = 1

# MODELOS DE DATOS
# CODE SMELL corregido: God Class

class Libro:
    """Representa un libro en el catálogo. Solo gestiona su propio estado."""
    def __init__(self, titulo: str, autor: str, isbn: str, cantidad: int):
        self.titulo     = titulo
        self.autor      = autor
        self.isbn       = isbn
        self.cantidad   = cantidad
        self.disponibles = cantidad

    def __str__(self):
        return f"[{self.isbn}] {self.titulo} - {self.autor} | Disponibles: {self.disponibles}"


class Prestamo:
    """Representa un préstamo activo o histórico. Responsabilidad única: datos del préstamo."""
    _contador = 0

    def __init__(self, usuario: "Usuario", libro: Libro, fecha_limite: datetime.date):
        Prestamo._contador += 1
        self.id             = Prestamo._contador
        self.usuario        = usuario
        self.libro          = libro
        self.fecha_prestamo = datetime.date.today()
        self.fecha_limite   = fecha_limite
        self.devuelto       = False
        self.fecha_devolucion: Optional[datetime.date] = None

    def marcar_devuelto(self):
        self.devuelto          = True
        self.fecha_devolucion  = datetime.date.today()

    def dias_de_retraso(self) -> int:
        if self.fecha_devolucion and self.fecha_devolucion > self.fecha_limite:
            return (self.fecha_devolucion - self.fecha_limite).days
        return 0

    def __str__(self):
        estado = "Devuelto" if self.devuelto else "Activo"
        return (f"Préstamo #{self.id} | Usuario: {self.usuario.nombre} "
                f"| Libro: {self.libro.titulo} | Límite: {self.fecha_limite} | {estado}")


class Multa:
    """Representa una multa generada por retraso en la devolución."""
    def __init__(self, usuario: "Usuario", monto: float, prestamo: Prestamo):
        self.usuario  = usuario
        self.monto    = monto
        self.prestamo = prestamo
        self.pagada   = False

    def __str__(self):
        estado = "Pagada" if self.pagada else "Pendiente"
        return f"Multa | Usuario: {self.usuario.nombre} | Monto: ${self.monto} | {estado}"

# PATRÓN: STRATEGY
# CODE SMELL corregido: Duplicate Code + Magic Numbers

class EstrategiaUsuario(ABC):
    """Interfaz abstracta para la estrategia de préstamo/multa por tipo de usuario.
    Principio D de SOLID: las clases de alto nivel dependen de esta abstracción."""

    @abstractmethod
    def dias_prestamo(self) -> int:
        pass

    @abstractmethod
    def multa_por_dia(self) -> float:
        pass


class EstrategiaNormal(EstrategiaUsuario):
    def dias_prestamo(self) -> int:
        return DIAS_PRESTAMO_NORMAL

    def multa_por_dia(self) -> float:
        return MULTA_DIARIA_NORMAL


class EstrategiaEstudiante(EstrategiaUsuario):
    def dias_prestamo(self) -> int:
        return DIAS_PRESTAMO_ESTUDIANTE

    def multa_por_dia(self) -> float:
        return MULTA_DIARIA_ESTUDIANTE


class EstrategiaVIP(EstrategiaUsuario):
    def dias_prestamo(self) -> int:
        return DIAS_PRESTAMO_VIP

    def multa_por_dia(self) -> float:
        return MULTA_DIARIA_VIP


def obtener_estrategia(tipo: str) -> EstrategiaUsuario:
    """Factory simple que retorna la estrategia correcta por tipo de usuario."""
    estrategias = {
        "normal":     EstrategiaNormal(),
        "estudiante": EstrategiaEstudiante(),
        "vip":        EstrategiaVIP(),
    }
    return estrategias.get(tipo, EstrategiaNormal())


class Usuario:
    """Representa un usuario del sistema. Usa su Strategy para calcular días y multas."""
    def __init__(self, nombre: str, id_usuario: str, tipo: str):
        self.nombre    = nombre
        self.id        = id_usuario
        self.tipo      = tipo
        self.activo    = True
        # Se inyecta la estrategia al momento de creación (Dependency Inversion)
        self.estrategia: EstrategiaUsuario = obtener_estrategia(tipo)

    def dias_prestamo(self) -> int:
        return self.estrategia.dias_prestamo()

    def calcular_multa(self, dias_tarde: int) -> float:
        return dias_tarde * self.estrategia.multa_por_dia()

    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"[{self.id}] {self.nombre} | Tipo: {self.tipo} | {estado}"

# PATRÓN: OBSERVER
# CODE SMELL corregido: Feature Envy

class ObservadorBiblioteca(ABC):
    """Interfaz abstracta para observadores de eventos de la biblioteca."""

    @abstractmethod
    def on_prestamo_creado(self, prestamo: Prestamo):
        pass

    @abstractmethod
    def on_devolucion_a_tiempo(self, prestamo: Prestamo):
        pass

    @abstractmethod
    def on_devolucion_con_multa(self, prestamo: Prestamo, multa: Multa):
        pass


class NotificadorConsola(ObservadorBiblioteca):
    """Observador concreto: notifica por consola. Se puede reemplazar por
    email, SMS, etc. sin tocar la lógica de negocio."""

    def on_prestamo_creado(self, prestamo: Prestamo):
        print(f"  [NOTIFICACIÓN] Hola {prestamo.usuario.nombre}, "
              f"tu préstamo de '{prestamo.libro.titulo}' vence el {prestamo.fecha_limite}.")

    def on_devolucion_a_tiempo(self, prestamo: Prestamo):
        print(f"  [NOTIFICACIÓN] Hola {prestamo.usuario.nombre}, "
              f"gracias por devolver '{prestamo.libro.titulo}' a tiempo.")

    def on_devolucion_con_multa(self, prestamo: Prestamo, multa: Multa):
        print(f"  [NOTIFICACIÓN] Hola {prestamo.usuario.nombre}, "
              f"tienes una multa de ${multa.monto} pendiente por retraso.")

# PATRÓN: SINGLETON
# CODE SMELL corregido: God Class (parcial)

class CatalogoBiblioteca:
    """
    Singleton que almacena el estado global: libros, usuarios, préstamos y multas.
    Garantiza que toda la aplicación trabaje con la misma fuente de datos.
    """
    _instancia: Optional["CatalogoBiblioteca"] = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        self.libros:    List[Libro]    = []
        self.usuarios:  List[Usuario]  = []
        self.prestamos: List[Prestamo] = []
        self.multas:    List[Multa]    = []

    # --- Acceso a libros ---
    def agregar_libro(self, libro: Libro):
        if self.buscar_libro(libro.isbn):
            print(f"  El libro con ISBN {libro.isbn} ya existe.")
            return
        self.libros.append(libro)

    def buscar_libro(self, isbn: str) -> Optional[Libro]:
        return next((l for l in self.libros if l.isbn == isbn), None)

    # --- Acceso a usuarios ---
    def agregar_usuario(self, usuario: Usuario):
        if self.buscar_usuario(usuario.id):
            print(f"  El usuario con ID {usuario.id} ya existe.")
            return
        self.usuarios.append(usuario)

    def buscar_usuario(self, id_usuario: str) -> Optional[Usuario]:
        return next((u for u in self.usuarios if u.id == id_usuario), None)

    def tiene_prestamos_vencidos(self, usuario: Usuario) -> bool:
        hoy = datetime.date.today()
        return any(
            p.usuario == usuario and not p.devuelto and hoy > p.fecha_limite
            for p in self.prestamos
        )

# SERVICIO DE BIBLIOTECA
# CODE SMELL corregido: God Class + Long Method

class ServicioBiblioteca:
    """
    Orquesta las operaciones del sistema usando el Catálogo (Singleton),
    las Estrategias y notificando a los Observadores (Observer).
    """

    def __init__(self):
        # Usa el Singleton como fuente de datos
        self.catalogo   = CatalogoBiblioteca()
        # Lista de observadores — se puede agregar/quitar sin modificar este servicio
        self._observadores: List[ObservadorBiblioteca] = []

    def suscribir_observador(self, observador: ObservadorBiblioteca):
        self._observadores.append(observador)

    # Métodos privados para notificar a todos los observadores (patrón Observer)
    def _notificar_prestamo(self, prestamo: Prestamo):
        for obs in self._observadores:
            obs.on_prestamo_creado(prestamo)

    def _notificar_devolucion_ok(self, prestamo: Prestamo):
        for obs in self._observadores:
            obs.on_devolucion_a_tiempo(prestamo)

    def _notificar_devolucion_multa(self, prestamo: Prestamo, multa: Multa):
        for obs in self._observadores:
            obs.on_devolucion_con_multa(prestamo, multa)

    # CODE SMELL corregido: Duplicate Code

    def _validar_usuario(self, id_usuario: str) -> Optional[Usuario]:
        usuario = self.catalogo.buscar_usuario(id_usuario)
        if not usuario:
            print("  Error: Usuario no encontrado.")
            return None
        if not usuario.activo:
            print("  Error: El usuario está inactivo.")
            return None
        return usuario

    def _validar_libro(self, isbn: str) -> Optional[Libro]:
        libro = self.catalogo.buscar_libro(isbn)
        if not libro:
            print("  Error: Libro no encontrado.")
            return None
        return libro

    # --- Operaciones principales ---

    def prestar_libro(self, id_usuario: str, isbn: str):
        usuario = self._validar_usuario(id_usuario)
        if not usuario:
            return

        libro = self._validar_libro(isbn)
        if not libro:
            return

        if libro.disponibles <= 0:
            print("  Error: No hay ejemplares disponibles.")
            return

        if self.catalogo.tiene_prestamos_vencidos(usuario):
            print("  Error: El usuario tiene préstamos vencidos. Debe pagar sus multas primero.")
            return

        # Los días de préstamo los calcula la Strategy del usuario (patrón Strategy)
        fecha_limite = datetime.date.today() + datetime.timedelta(days=usuario.dias_prestamo())
        prestamo     = Prestamo(usuario, libro, fecha_limite)

        self.catalogo.prestamos.append(prestamo)
        libro.disponibles -= 1

        print(f"  Préstamo registrado. Fecha límite: {fecha_limite}")
        # Delegar notificación al Observer — lógica de negocio no sabe CÓMO se notifica
        self._notificar_prestamo(prestamo)

    def devolver_libro(self, id_usuario: str, isbn: str):
        usuario = self._validar_usuario(id_usuario)
        if not usuario:
            return

        libro = self._validar_libro(isbn)
        if not libro:
            return

        prestamo = next(
            (p for p in self.catalogo.prestamos
             if p.usuario == usuario and p.libro == libro and not p.devuelto),
            None
        )
        if not prestamo:
            print("  Error: No se encontró un préstamo activo para este usuario y libro.")
            return

        prestamo.marcar_devuelto()
        libro.disponibles += 1

        dias_tarde = prestamo.dias_de_retraso()
        if dias_tarde > 0:
            # La multa la calcula la Strategy del usuario (patrón Strategy)
            monto = usuario.calcular_multa(dias_tarde)
            multa = Multa(usuario, monto, prestamo)
            self.catalogo.multas.append(multa)
            print(f"  Libro devuelto con {dias_tarde} días de retraso. Multa: ${monto}")
            self._notificar_devolucion_multa(prestamo, multa)
        else:
            print("  Libro devuelto a tiempo. ¡Gracias!")
            self._notificar_devolucion_ok(prestamo)

    # --- Reportes ---

    def mostrar_libros(self):
        if not self.catalogo.libros:
            print("  No hay libros registrados.")
            return
        for libro in self.catalogo.libros:
            print(f"  {libro}")

    def mostrar_usuarios(self):
        if not self.catalogo.usuarios:
            print("  No hay usuarios registrados.")
            return
        for u in self.catalogo.usuarios:
            print(f"  {u}")

    def mostrar_prestamos(self):
        if not self.catalogo.prestamos:
            print("  No hay préstamos registrados.")
            return
        for p in self.catalogo.prestamos:
            print(f"  {p}")

    def mostrar_multas(self):
        if not self.catalogo.multas:
            print("  No hay multas registradas.")
            return
        for m in self.catalogo.multas:
            print(f"  {m}")


if __name__ == "__main__":

    # Inicializar servicio y registrar observador de notificaciones (patrón Observer)
    servicio = ServicioBiblioteca()
    servicio.suscribir_observador(NotificadorConsola())

    # Poblar catálogo a través del Singleton
    catalogo = CatalogoBiblioteca()

    catalogo.agregar_libro(Libro("Cien años de soledad", "Gabriel García Márquez", "978-0-06-088328-7", 3))
    catalogo.agregar_libro(Libro("El principito",        "Antoine de Saint-Exupéry","978-0-15-601219-5", 2))
    catalogo.agregar_libro(Libro("1984",                 "George Orwell",           "978-0-45-152493-5", 1))

    catalogo.agregar_usuario(Usuario("Ana López",     "U001", "normal"))
    catalogo.agregar_usuario(Usuario("Carlos Ruiz",   "U002", "estudiante"))
    catalogo.agregar_usuario(Usuario("María Torres",  "U003", "vip"))

    print("\n--- CATÁLOGO ---")
    servicio.mostrar_libros()

    print("\n--- PRÉSTAMOS ---")
    servicio.prestar_libro("U001", "978-0-06-088328-7")
    servicio.prestar_libro("U002", "978-0-15-601219-5")
    servicio.prestar_libro("U003", "978-0-45-152493-5")

    print("\n--- DEVOLUCIONES ---")
    servicio.devolver_libro("U001", "978-0-06-088328-7")

    print("\n--- ESTADO FINAL ---")
    servicio.mostrar_libros()
    servicio.mostrar_prestamos()
    servicio.mostrar_multas()
