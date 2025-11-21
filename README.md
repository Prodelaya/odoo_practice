# Odoo 19 – Entorno de práctica (WSL + Docker) y addon “Remote Work Requests”

Práctica con **Odoo 19** sobre **WSL + Docker**: orquestación mínima (Odoo + PostgreSQL), carpeta de `custom_addons/` y desarrollo de un addon real (**Remote Work Requests**) con modelos, vistas, permisos y un endpoint JSON.

---

## Tabla de contenidos
- [Odoo 19 – Entorno de práctica (WSL + Docker) y addon “Remote Work Requests”](#odoo-19--entorno-de-práctica-wsl--docker-y-addon-remote-work-requests)
  - [Tabla de contenidos](#tabla-de-contenidos)
  - [Objetivos](#objetivos)
  - [Requisitos previos](#requisitos-previos)
  - [Estructura del proyecto](#estructura-del-proyecto)
  - [Clonado del repositorio](#clonado-del-repositorio)
  - [Configuración](#configuración)
    - [Variables de entorno](#variables-de-entorno)
    - [Archivo de configuración de Odoo](#archivo-de-configuración-de-odoo)
  - [Arranque](#arranque)
  - [Verificación rápida](#verificación-rápida)
  - [Addon de ejemplo: Remote Work Requests](#addon-de-ejemplo-remote-work-requests)
    - [Características principales](#características-principales)
    - [Documentación completa](#documentación-completa)
    - [Inicio rápido](#inicio-rápido)
    - [Ejecutar tests](#ejecutar-tests)
    - [Capturas de pantalla](#capturas-de-pantalla)
  - [Comandos útiles](#comandos-útiles)
  - [Solución de problemas](#solución-de-problemas)
  - [Buenas prácticas](#buenas-prácticas)

---

## Objetivos
- Montar **Odoo 19 + PostgreSQL** en Docker (WSL).
- Entender la configuración real: `odoo.conf`, `addons_path`, `data_dir`.
- Desarrollar un addon con **modelos, vistas, seguridad** y un **endpoint JSON**.
- Mantener el proyecto limpio: `custom_addons/` versionado, **core fuera del repo**.

---

## Requisitos previos
- **Windows 10/11** con **WSL2** (Ubuntu recomendado).
- **Docker Desktop** (con integración WSL habilitada).
- **Git** instalado en WSL.
- Navegador web (para `http://localhost:8069`).

> Nota: ejecuta comandos siempre desde **WSL** (rutas Linux), no desde PowerShell/CMD.

---

## Estructura del proyecto
~~~text
odoo_practice/
├─ docker/
│  ├─ compose.yaml                  # orquestación (Odoo + PostgreSQL)
│  ├─ .env.example                  # plantilla de variables
│  ├─ odoo.conf.example             # plantilla de configuración de Odoo
│  └─ (odoo.conf y .env reales)     # NO se versionan
├─ custom_addons/
│  └─ remote_work_requests/         # addon de ejemplo (carpeta del módulo)
├─ odoo/                            # clon del core (IGNORADO por git)
└─ README.md
~~~

---

## Clonado del repositorio
~~~bash
# Dentro de WSL
cd ~/proyectos
git clone <URL_DE_TU_REPO> odoo_practice
cd odoo_practice
~~~

Si ya tenías el core clonado, colócalo (o clónalo) en `odoo_practice/odoo/` (está **ignorado por git**).

---

## Configuración

### Variables de entorno
1. Copia la plantilla y rellena credenciales reales:
~~~bash
cd docker
cp .env.example .env
~~~

2. Edita `.env` (no se sube a git) con valores reales:
~~~dotenv
POSTGRES_USER=odoo
POSTGRES_PASSWORD=********
POSTGRES_DB=odoo_db
ADMIN_PASSWORD=********     # “master password” que pedirá Odoo al crear la BD
~~~

> Mantén **`.env.example`** en el repo con valores de ejemplo para que otros puedan replicar el entorno.

### Archivo de configuración de Odoo
1. Copia la plantilla y ajusta valores:
~~~bash
cp odoo.conf.example odoo.conf
~~~

2. Asegúrate de que contiene (valores reales en `odoo.conf`):

Conexión a DB:
~~~ini
db_host = db
db_port = 5432
db_user = odoo
db_password = ********
~~~

Ruta de addons:
~~~ini
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
~~~

Master password:
~~~ini
admin_passwd = ********
~~~

Otros:
~~~ini
data_dir = /var/lib/odoo
log_level = info
~~~

> **Importante**: el host `db` debe coincidir con el **nombre del servicio** de PostgreSQL en `compose.yaml`.

---

## Arranque
~~~bash
# Desde la carpeta docker/
cd docker
# Arranca en segundo plano
docker compose up -d
~~~

Cuando todo esté en marcha, abre:
**http://localhost:8069**

- Crea una **base de datos** (por ejemplo `odoo_db`).
- Cuando pida **Master Password**, introduce la de `ADMIN_PASSWORD` de tu `.env`
  (y que pusiste en `odoo.conf` como `admin_passwd`).

---

## Verificación rápida
1. En Odoo, **Ajustes → Activar Modo Desarrollador**.
2. **Ajustes → Técnico → Parámetros → Rutas de addons**:
   - Debes ver **dos rutas**:
     - `/usr/lib/python3/dist-packages/odoo/addons`
     - `/mnt/extra-addons`
3. **Apps → Actualizar lista de aplicaciones**: verifica que aparece tu módulo en `custom_addons/` (aunque esté “vacío” de momento).

---

## Addon de ejemplo: Remote Work Requests

**Descripción:** Sistema completo de gestión de solicitudes de teletrabajo con flujo de aprobación.

### Características principales
- **Modelo de datos**: Solicitudes con empleado, fechas, motivo, estado y cálculo automático de días
- **Flujo de estados**: `borrador → revisión → aprobada/rechazada`
- **Vistas**: Lista, formulario, kanban y búsqueda con filtros contextuales
- **Lógica de negocio**: Validaciones de fechas, acciones de transición, campos computados
- **API REST**: Endpoint JSON para consultar solicitudes aprobadas
- **Seguridad**:
  - Grupos: Empleado (crear propias) y Manager (aprobar asignadas)
  - Record rules: RLS (Row-Level Security)
  - ACL: Permisos CRUD por grupo
- **Suite de tests**: 45 tests automatizados (100% passing)
  - Tests de modelo (validaciones, cálculos, constraints)
  - Tests de workflow (transiciones de estado)
  - Tests de seguridad (permisos, aislamiento)
  - Tests de API (endpoint HTTP JSON)

### Documentación completa

El proyecto incluye documentación profesional y exhaustiva:

| Documento | Descripción | Audiencia |
|-----------|-------------|-----------|
| **[01-requisitos-de-negocio.md](docs/01-requisitos-de-negocio.md)** | Requisitos funcionales y no funcionales del sistema | Product Owners, Stakeholders |
| **[02-arquitectura-tecnica.md](docs/02-arquitectura-tecnica.md)** | Arquitectura del sistema, componentes, modelo de datos, decisiones de diseño | Arquitectos, Desarrolladores Senior |
| **[03-diseno-funcional.md](docs/03-diseno-funcional.md)** | Casos de uso, flujos de trabajo, especificación de pantallas, reglas de negocio | Analistas Funcionales, QA |
| **[04-api-specification.md](docs/04-api-specification.md)** | Especificación OpenAPI del endpoint REST, ejemplos de consumo | Desarrolladores de integraciones |
| **[05-manual-de-usuario.md](docs/05-manual-de-usuario.md)** | Guía paso a paso para empleados y managers | Usuarios finales |
| **[tests-recomendados.md](docs/tests-recomendados.md)** | Plan de testing completo | QA Engineers, Desarrolladores |
| **[tests-realizados.md](docs/tests-realizados.md)** | Estado de implementación de testing | QA Engineers, Desarrolladores |

### Inicio rápido

1. **Instalación del módulo:**
   ```bash
   cd docker
   docker compose up -d
   ```

2. **Acceder a Odoo:**
   - URL: http://localhost:8069
   - Activar **Modo Desarrollador**
   - **Apps → Actualizar lista de aplicaciones**
   - Buscar "Remote Work Requests" e instalar

3. **Configurar permisos:**
   - **Configuración → Usuarios**
   - Asignar grupos:
     - `Empleado - Solicitar Teletrabajo` (para usuarios normales)
     - `Gerente - Gestionar Solicitudes` (para managers)

4. **Probar el sistema:**
   - **Empleado**: Trabajo Remoto → Solicitudes → Crear
   - **Manager**: Trabajo Remoto → Solicitudes → Filtro "Pendientes de revisar"

5. **Consumir el API:**
   ```bash
   curl -X GET "http://localhost:8069/remote_work/approved_requests"
   ```

### Ejecutar tests

```bash
cd docker
docker compose run --rm odoo odoo --test-enable --stop-after-init \
  -d odoo_db -u remote_work_requests
```

**Resultado esperado:**
```
41 post-tests in 3.36s, 2110 queries
0 failed, 0 error(s) of 41 tests
```

### Capturas de pantalla

El proyecto incluye 12 capturas de pantalla documentando la interfaz:

- `assets/01-screenshot-apps-gallery.jpg` - Galería de apps
- `assets/02-screenshot-app-info.jpg` - Información del módulo
- `assets/03-screenshot-app-view.jpg` - Vista general
- `assets/04-screenshot-app-form.jpg` - Formulario de solicitud
- `assets/05-screenshot-app-list.jpg` - Vista de lista
- `assets/06-screenshot-app-buttons.jpg` - Botones de acción por estado
- `assets/07-screenshot-app-filters.jpg` - Filtros de búsqueda
- `assets/08-screenshot-app-only-own-user-requests.jpg` - Vista empleado (aislamiento)
- `assets/09-screenshot-app-groups-permissions.jpg` - Configuración de permisos
- `assets/10-screenshot-app-only-to-approver-user-requests.jpg` - Vista manager
- `assets/11-screenshot-app-state-colors.jpg` - Colorización por estado
- `assets/12-screenshot-app-kanban-view.jpg` - Vista Kanban

> El desarrollo del addon se realiza en `custom_addons/remote_work_requests/`. Odoo lo "ve" porque montamos `custom_addons/` como `/mnt/extra-addons` en el contenedor.

---

## Comandos útiles
~~~bash
# Ver logs en vivo (útil para depurar arranque)
docker compose logs -f

# Reiniciar solo Odoo (aplica cambios de config/vistas sin tocar la BD)
docker compose restart odoo

# Parar contenedores
docker compose down

# Parar y borrar volúmenes (¡destruye datos! Postgres + filestore)
docker compose down -v
~~~

---

## Solución de problemas

**No veo `/mnt/extra-addons` en “Rutas de addons”**
- Verifica que `odoo.conf` tiene:
  ~~~ini
  addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
  ~~~
- Confirma que el **compose** monta tu `custom_addons/` → `/mnt/extra-addons`.
- Comprueba que **`odoo.conf` está montado** en `/etc/odoo/odoo.conf`.

**Odoo no conecta con la base**
- En `odoo.conf`: `db_host = db`, `db_user`, `db_password` y puerto `5432`.
- En `.env`: `POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB` coherentes.
- Revisa `docker compose logs -f db`.

**El módulo no aparece en Apps**
- Pulsa **“Actualizar lista de aplicaciones”**.
- Asegúrate de que el módulo tiene **`__manifest__.py`** y nombre de carpeta correcto.
- Mira logs de Odoo por errores de carga.

**Contraseñas con caracteres no ASCII**
- Si ves errores raros de autenticación/codificación, prueba temporalmente una contraseña ASCII.

---

## Buenas prácticas
- Versiona solo plantillas: **`.env.example`** y **`odoo.conf.example`**.
- Mantén **`docker/.env`** y **`docker/odoo.conf`** fuera del repo.
- Usa rutas **WSL/Linux** en volúmenes (no rutas UNC de Windows).
- Crea un **venv** local para tooling (linters/formatters) si lo necesitas:
  - `black`, `isort`, `ruff`, `pylint-odoo`, `pre-commit`.

---
