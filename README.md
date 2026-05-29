# Patrones_Software
## Sistema de Gestión de Biblioteca
## Proyecto Final — Patrones de Software

---

## Estructura del repositorio

```
biblioteca/
├── original/
│   └── biblioteca_original.py       # Código funcional con code smells
└── refactorizado/
    └── biblioteca_refactorizada.py  # Código refactorizado con patrones
```

---

## Cómo ejecutar

```bash
# Código original
python original/biblioteca_original.py

# Código refactorizado
python refactorizado/biblioteca_refactorizada.py
```

Ambos producen la misma salida funcional ✅

---

## Code Smells detectados y cómo se corrigieron

| Code Smell | Ubicación original | Solución aplicada |
|---|---|---|
| **God Class** | `Biblioteca` manejaba libros, usuarios, préstamos, multas y notificaciones | Se separó en `Libro`, `Usuario`, `Prestamo`, `Multa`, `CatalogoBiblioteca` y `ServicioBiblioteca` |
| **Long Method** | `prestar_libro()` y `devolver_libro()` con 40-50 líneas cada uno | Se extrajeron métodos `_validar_usuario()`, `_validar_libro()`, notificadores delegados al Observer |
| **Magic Numbers** | `14`, `7`, `21`, `5`, `3`, `1` hardcodeados en los métodos | Constantes nombradas: `DIAS_PRESTAMO_NORMAL`, `MULTA_DIARIA_VIP`, etc. |
| **Duplicate Code** | Búsqueda y validación de usuario/libro repetida en `prestar` y `devolver` | Métodos privados `_validar_usuario()` y `_validar_libro()` reutilizados |
| **Feature Envy** | Notificaciones `print()` mezcladas dentro de la lógica de negocio | Patrón Observer: `NotificadorConsola` separado completamente |

---

## Patrones de software aplicados

### 1. Singleton — `CatalogoBiblioteca`
**Por qué:** El sistema necesita una única fuente de verdad para libros, usuarios, préstamos y multas. Sin Singleton, podrían existir múltiples instancias con datos inconsistentes.

**Cómo:** `__new__` revisa si `_instancia` ya existe; si no, la crea. Cualquier parte del programa que llame a `CatalogoBiblioteca()` obtiene siempre el mismo objeto.

---

### 2. Strategy — `EstrategiaUsuario`
**Por qué:** El cálculo de días de préstamo y multa dependía del tipo de usuario, causando `if/elif` duplicados en dos métodos distintos. Agregar un nuevo tipo requería modificar código existente.

**Cómo:** Interfaz abstracta `EstrategiaUsuario` con implementaciones `EstrategiaNormal`, `EstrategiaEstudiante`, `EstrategiaVIP`. El `Usuario` delega el cálculo a su estrategia. Agregar un tipo "Senior" = nueva clase, sin tocar nada más.

---

### 3. Observer — `ObservadorBiblioteca`
**Por qué:** Las notificaciones estaban acopladas a la lógica de negocio (Feature Envy). Si se quisiera cambiar a email o SMS, habría que modificar `prestar_libro()` y `devolver_libro()`.

**Cómo:** Interfaz abstracta `ObservadorBiblioteca` con métodos de eventos. `ServicioBiblioteca` mantiene una lista de observadores y los notifica. `NotificadorConsola` es una implementación concreta intercambiable.

---

## Principios SOLID aplicados

| Principio | Aplicación |
|---|---|
| **S** — Single Responsibility | Cada clase tiene una sola razón para cambiar: `Libro` solo gestiona datos de libro, `Prestamo` solo datos de préstamo, `ServicioBiblioteca` solo orquesta operaciones |
| **O** — Open/Closed | Agregar un nuevo tipo de usuario = nueva clase Strategy, sin modificar `ServicioBiblioteca` ni `Usuario` |
| **D** — Dependency Inversion | `ServicioBiblioteca` depende de `ObservadorBiblioteca` (abstracción), no de `NotificadorConsola` (implementación concreta) |

---

## Verificación de funcionalidad

Ambas versiones proveen exactamente la misma funcionalidad:
- ✅ Agregar libros y usuarios
- ✅ Registrar préstamos con fecha límite según tipo de usuario
- ✅ Registrar devoluciones y calcular multas por retraso
- ✅ Bloquear préstamos a usuarios con préstamos vencidos
- ✅ Mostrar catálogo, préstamos y multas
- ✅ Notificaciones al usuario en cada operación
