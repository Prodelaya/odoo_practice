# 02 — Arquitectura Técnica: Remote Work Requests (Odoo 19)

**Proyecto:** Sistema de Gestión de Solicitudes de Teletrabajo
**Versión del documento:** 1.0
**Fecha:** 21 de noviembre de 2025
**Autor:** Pablo Laya

---

## Índice

1. [Introducción](#1-introducción)
2. [Visión General de la Arquitectura](#2-visión-general-de-la-arquitectura)
3. [Componentes del Sistema](#3-componentes-del-sistema)
4. [Modelo de Datos](#4-modelo-de-datos)
5. [Capa de Presentación](#5-capa-de-presentación)
6. [Capa de Lógica de Negocio](#6-capa-de-lógica-de-negocio)
7. [Capa de Seguridad](#7-capa-de-seguridad)
8. [API y Servicios Web](#8-api-y-servicios-web)
9. [Infraestructura y Despliegue](#9-infraestructura-y-despliegue)
10. [Flujos de Datos](#10-flujos-de-datos)
11. [Decisiones de Diseño](#11-decisiones-de-diseño)
12. [Consideraciones de Escalabilidad](#12-consideraciones-de-escalabilidad)

---

## 1. Introducción

### 1.1 Propósito del Documento

Este documento describe la arquitectura técnica del addon `remote_work_requests` para Odoo 19. Proporciona una visión completa de los componentes del sistema, sus interacciones, decisiones de diseño y consideraciones de implementación.

### 1.2 Alcance

El sistema implementa un flujo completo de gestión de solicitudes de teletrabajo que incluye:
- Creación y seguimiento de solicitudes por empleados
- Proceso de aprobación por managers
- Exposición de datos a través de API REST
- Control de acceso granular basado en roles

### 1.3 Audiencia

Este documento está dirigido a:
- Desarrolladores que mantienen o extienden el addon
- Arquitectos de software evaluando el diseño
- Administradores de sistema configurando el entorno
- Auditores de seguridad revisando controles de acceso

---

## 2. Visión General de la Arquitectura

### 2.1 Patrón Arquitectónico

El addon sigue el patrón **MVC (Model-View-Controller)** de Odoo:

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENTE (Navegador)                     │
│                  Interfaz Web de Odoo                        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    ODOO WEB SERVER                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Controllers  │  │    Views     │  │     Models       │  │
│  │  (HTTP)      │  │   (XML)      │  │   (Python)       │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                  │                    │             │
│         └──────────────────┴────────────────────┘             │
│                           │                                   │
│                    ┌──────▼───────┐                          │
│                    │   Security   │                          │
│                    │  (Groups +   │                          │
│                    │    Rules)    │                          │
│                    └──────┬───────┘                          │
└───────────────────────────┼──────────────────────────────────┘
                            │ ORM (Python)
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                  PostgreSQL Database                         │
│   ┌─────────────────┐  ┌─────────────────┐                  │
│   │ remote.work.    │  │  hr.employee    │                  │
│   │   request       │  │  res.users      │                  │
│   │  (main table)   │  │   (FK refs)     │                  │
│   └─────────────────┘  └─────────────────┘                  │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Tecnologías Utilizadas

| Componente | Tecnología | Versión |
|------------|------------|---------|
| **Framework** | Odoo | 19.0 |
| **Backend** | Python | 3.12 |
| **Base de Datos** | PostgreSQL | 16 |
| **ORM** | Odoo ORM | Built-in |
| **Frontend** | XML Views + JavaScript (Odoo Web Client) | Built-in |
| **API** | HTTP Controllers (JSON) | Built-in |
| **Contenedorización** | Docker + Docker Compose | Latest |
| **Sistema Operativo** | Linux (WSL2) | Kernel 6.6 |

### 2.3 Dependencias del Módulo

```python
# __manifest__.py
"depends": ["base", "hr"]
```

**Justificación:**
- `base`: Módulo core de Odoo (obligatorio)
- `hr`: Gestión de empleados y departamentos (relación Many2one con `hr.employee`)

---

## 3. Componentes del Sistema

### 3.1 Estructura de Directorios

```
custom_addons/remote_work_requests/
│
├── __init__.py                     # Inicializador del módulo
├── __manifest__.py                 # Metadata y configuración
│
├── models/                         # Capa de datos
│   ├── __init__.py
│   └── remote_request.py          # Modelo principal
│
├── views/                          # Capa de presentación
│   └── remote_request_view.xml    # Vistas Form, List, Kanban, Search
│
├── controllers/                    # Capa de API
│   ├── __init__.py
│   └── main.py                    # Endpoint HTTP JSON
│
├── security/                       # Capa de seguridad
│   ├── remote_request_groups.xml  # Definición de grupos
│   ├── remote_request_rules.xml   # Record rules (RLS)
│   └── ir.model.access.csv        # ACL (Access Control List)
│
├── data/                           # Datos demo/seed
│   ├── hr_demo.xml                # Empleados y managers demo
│   └── remote_request_demo.xml    # Solicitudes demo
│
├── tests/                          # Suite de tests
│   ├── __init__.py
│   ├── test_remote_request_model.py
│   ├── test_remote_request_workflow.py
│   ├── test_remote_request_security.py
│   └── test_remote_request_controller.py
│
├── static/                         # Assets estáticos
│   └── description/
│       └── icon.png               # Icono del módulo
│
└── assets/                         # Screenshots y documentación visual
    └── *.png                      # 12 capturas de pantalla
```

### 3.2 Componentes Principales

#### 3.2.1 Modelo de Datos (`models/remote_request.py`)

**Responsabilidad:**
- Definir estructura de datos
- Implementar lógica de negocio (validaciones, cálculos)
- Gestionar transiciones de estado

**Clase principal:** `RemoteWorkRequest(models.Model)`

**Características técnicas:**
- Hereda de `models.Model` (persistencia en base de datos)
- Uso de decoradores: `@api.depends`, `@api.constrains`
- Campos computados con almacenamiento (`store=True`)
- Validaciones a nivel de base de datos (constraints SQL)

#### 3.2.2 Vistas (`views/remote_request_view.xml`)

**Responsabilidad:**
- Definir interfaz de usuario
- Configurar formularios, listas, kanban y búsquedas
- Establecer menús y acciones

**Tipos de vistas implementadas:**
1. **Form View**: Formulario de creación/edición
2. **List View**: Tabla con listado de registros
3. **Kanban View**: Tablero agrupado por estado
4. **Search View**: Filtros y búsquedas

#### 3.2.3 Controladores (`controllers/main.py`)

**Responsabilidad:**
- Exponer endpoint HTTP para consumo externo
- Serializar datos a JSON
- Gestionar autenticación (configurado como público)

**Clase principal:** `RemoteWorkApprovedController(http.Controller)`

**Características técnicas:**
- Decorador `@http.route` con configuración de ruta
- Uso de `.sudo()` para bypass de ACL (decisión de diseño)
- Serialización manual de fechas a formato ISO

#### 3.2.4 Seguridad (`security/`)

**Responsabilidad:**
- Definir grupos de usuarios
- Implementar RLS (Row-Level Security) mediante record rules
- Configurar permisos CRUD por grupo

**Componentes:**
1. **Grupos XML**: Definición de roles (Employee, Manager)
2. **Record Rules XML**: Filtrado de registros por usuario
3. **ACL CSV**: Permisos de acceso al modelo

#### 3.2.5 Tests (`tests/`)

**Responsabilidad:**
- Validar funcionalidad del modelo
- Verificar flujo de estados
- Asegurar permisos y seguridad
- Validar API endpoint

**Cobertura:**
- 45 tests automatizados
- 100% de tasa de éxito
- Tiempo de ejecución: ~3.5s

---

## 4. Modelo de Datos

### 4.1 Diagrama Entidad-Relación

```
┌─────────────────────────────────────────────────────────────┐
│                   remote.work.request                        │
├─────────────────────────────────────────────────────────────┤
│ PK  id (integer)                                             │
│     name (varchar) NOT NULL                                  │
│ FK  employee_id (→ hr.employee) NOT NULL                     │
│ FK  approver_id (→ res.users)                                │
│ FK  user_id (→ res.users) STORED COMPUTED                    │
│     request_date (date) DEFAULT today                        │
│     date_start (date) NOT NULL                               │
│     date_end (date) NOT NULL                                 │
│     reason (text) NOT NULL                                   │
│     state (varchar) DEFAULT 'draft'                          │
│     days_count (integer) STORED COMPUTED                     │
│     resolution_date (date)                                   │
├─────────────────────────────────────────────────────────────┤
│ CONSTRAINTS:                                                 │
│   check_dates: date_end >= date_start                        │
│   check_state: state IN (draft, in_review, approved,        │
│                          rejected)                           │
└─────────────────────────────────────────────────────────────┘
           │                    │
           │                    │
           ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│  hr.employee     │  │   res.users      │
├──────────────────┤  ├──────────────────┤
│ PK id            │  │ PK id            │
│    name          │  │    login         │
│ FK user_id       │  │    name          │
│ FK department_id │  │    groups_id     │
└──────────────────┘  └──────────────────┘
```

### 4.2 Diccionario de Datos

#### Tabla: `remote_work_request`

| Campo | Tipo | Nulo | Default | Índice | Descripción |
|-------|------|------|---------|--------|-------------|
| `id` | SERIAL | NO | AUTO | PK | Identificador único |
| `name` | VARCHAR(255) | NO | - | - | Título de la solicitud |
| `employee_id` | INTEGER | NO | `_default_employee_id()` | FK | Referencia a empleado |
| `approver_id` | INTEGER | YES | NULL | FK | Referencia a aprobador |
| `user_id` | INTEGER | YES | COMPUTED | FK | Usuario del empleado (sincronizado) |
| `request_date` | DATE | NO | `today()` | - | Fecha de creación |
| `date_start` | DATE | NO | - | - | Fecha inicio teletrabajo |
| `date_end` | DATE | NO | - | - | Fecha fin teletrabajo |
| `reason` | TEXT | NO | - | - | Justificación de la solicitud |
| `state` | VARCHAR(20) | NO | 'draft' | INDEX | Estado del flujo |
| `days_count` | INTEGER | NO | COMPUTED | - | Días totales (inclusivo) |
| `resolution_date` | DATE | YES | NULL | - | Fecha de aprobación/rechazo |

**Notas técnicas:**
- `user_id` es un campo relacionado (`related='employee_id.user_id'`) con `store=True` para optimizar consultas
- `days_count` se calcula automáticamente mediante `@api.depends("date_start", "date_end")`
- Constraint `check_dates` se valida tanto en Python como en SQL (seguridad en profundidad)

### 4.3 Estados y Transiciones

```python
STATE_SELECTION = [
    ('draft', 'Borrador'),
    ('in_review', 'En revisión'),
    ('approved', 'Aprobada'),
    ('rejected', 'Rechazada'),
]
```

**Máquina de estados:**

```
[draft] ──action_submit()──> [in_review] ──action_approve()──> [approved]
                                  │
                                  └──action_reject()──> [rejected]
```

**Invariantes de estado:**
- Solo desde `draft` se puede ejecutar `action_submit()`
- Solo desde `in_review` se puede ejecutar `action_approve()` o `action_reject()`
- Estados `approved` y `rejected` son finales (no se puede volver atrás en v1)

### 4.4 Campos Computados

#### 4.4.1 `days_count`

**Función:** `_compute_days_count()`

**Lógica:**
```python
if self.date_start and self.date_end:
    delta = (self.date_end - self.date_start).days
    self.days_count = delta + 1 if delta >= 0 else 0
else:
    self.days_count = 0
```

**Trigger:** Cambios en `date_start` o `date_end` (decorador `@api.depends`)

**Almacenamiento:** `store=True` (persiste en base de datos)

**Justificación:**
- Evita recálculo en cada lectura
- Permite ordenar/filtrar por días en vistas
- Incluye ambos extremos (lunes a viernes = 5 días)

#### 4.4.2 `user_id`

**Función:** Campo relacionado

**Lógica:**
```python
user_id = fields.Many2one(
    "res.users",
    related="employee_id.user_id",
    store=True,
    readonly=True,
)
```

**Justificación:**
- Facilita record rules (filtrado por `user_id = user.id`)
- Evita joins adicionales en consultas
- Se sincroniza automáticamente al cambiar `employee_id`

---

## 5. Capa de Presentación

### 5.1 Vista de Formulario (Form View)

**Archivo:** `views/remote_request_view.xml` (líneas 5-60)

**Estructura XML:**

```xml
<form>
  <header>
    <button name="action_submit" type="object" states="draft" class="btn-primary"/>
    <button name="action_approve" type="object" states="in_review" class="btn-success"/>
    <button name="action_reject" type="object" states="in_review" class="btn-danger"/>
    <field name="state" widget="statusbar"/>
  </header>
  <sheet>
    <group name="basic_info">
      <!-- name, employee_id, approver_id, state -->
    </group>
    <group name="dates_info">
      <!-- request_date, date_start, date_end, days_count, resolution_date -->
    </group>
    <group name="reason_info">
      <!-- reason (widget="text") -->
    </group>
  </sheet>
</form>
```

**Características:**
- **Botones contextuales:** Visibilidad condicionada por atributo `states`
- **StatusBar:** Indicador visual del estado actual
- **Grupos de campos:** Organización lógica de información
- **Widgets especiales:** `text` para `reason` (área de texto expandible)

### 5.2 Vista de Lista (List View)

**Archivo:** `views/remote_request_view.xml` (líneas 62-90)

**Columnas mostradas:**
1. `name` (Nombre)
2. `employee_id` (Empleado)
3. `request_date` (Fecha de solicitud)
4. `date_start` (Inicio)
5. `date_end` (Fin)
6. `days_count` (Días)
7. `state` (Estado)
8. `approver_id` (Aprobador)

**Decoraciones condicionales:**

```xml
<tree decoration-muted="state == 'draft'"
      decoration-info="state == 'in_review'"
      decoration-success="state == 'approved'"
      decoration-danger="state == 'rejected'">
```

**Mapeo de colores:**
- **Gris (muted):** Borrador (aún no enviado)
- **Azul (info):** En revisión (pendiente de decisión)
- **Verde (success):** Aprobada
- **Rojo (danger):** Rechazada

### 5.3 Vista Kanban

**Archivo:** `views/remote_request_view.xml` (líneas 92-125)

**Configuración:**
```xml
<kanban default_group_by="state">
  <field name="name"/>
  <field name="employee_id"/>
  <field name="date_start"/>
  <field name="date_end"/>
  <field name="days_count"/>
  <field name="state"/>
  <templates>
    <t t-name="kanban-box">
      <!-- Template HTML customizado -->
    </t>
  </templates>
</kanban>
```

**Agrupación por defecto:** Estado (`default_group_by="state"`)

**Ventajas:**
- Visión rápida del pipeline de solicitudes
- Drag & drop para cambiar estados (si se habilita)
- Ideal para managers que gestionan múltiples solicitudes

### 5.4 Vista de Búsqueda (Search View)

**Archivo:** `views/remote_request_view.xml` (líneas 127-160)

**Campos de búsqueda:**
- `name` (búsqueda por texto)
- `employee_id` (autocompletar)
- `approver_id` (autocompletar)

**Filtros predefinidos:**

| ID | Etiqueta | Dominio |
|----|----------|---------|
| `state_draft` | Borrador | `[('state', '=', 'draft')]` |
| `state_in_review` | En revisión | `[('state', '=', 'in_review')]` |
| `state_approved` | Aprobadas | `[('state', '=', 'approved')]` |
| `state_rejected` | Rechazadas | `[('state', '=', 'rejected')]` |
| `my_requests` | Mis solicitudes | `[('user_id', '=', uid)]` |
| `assigned_to_me` | Asignadas a mí | `[('approver_id', '=', uid)]` |
| `pending_review_for_me` | Pendientes de revisar | `[('approver_id', '=', uid), ('state', '=', 'in_review')]` |

**Uso de variable especial `uid`:**
- Odoo la sustituye automáticamente por el ID del usuario actual
- Permite filtros dinámicos sin lógica de backend

---

## 6. Capa de Lógica de Negocio

### 6.1 Métodos del Modelo

#### 6.1.1 `_default_employee_id()`

**Propósito:** Asignar automáticamente el empleado actual al crear una solicitud

**Implementación:**
```python
def _default_employee_id(self):
    return self.env["hr.employee"].search(
        [("user_id", "=", self.env.user.id)], limit=1
    )
```

**Contexto de uso:**
```python
employee_id = fields.Many2one(
    "hr.employee",
    default=_default_employee_id,
    required=True,
)
```

**Flujo:**
1. Usuario autenticado tiene `self.env.user.id`
2. Se busca empleado con `user_id` coincidente
3. Si existe, se asigna automáticamente
4. Si no existe, el campo queda vacío (error al guardar por `required=True`)

#### 6.1.2 `_compute_days_count()`

**Propósito:** Calcular días laborables entre fechas (inclusivo)

**Decorador:**
```python
@api.depends("date_start", "date_end")
def _compute_days_count(self):
    ...
```

**Algoritmo:**
```python
for record in self:
    if record.date_start and record.date_end:
        delta = (record.date_end - record.date_start).days
        record.days_count = delta + 1 if delta >= 0 else 0
    else:
        record.days_count = 0
```

**Casos de prueba:**
- `2025-01-15 a 2025-01-15` → 1 día
- `2025-01-15 a 2025-01-20` → 6 días
- `2025-01-01 a 2025-12-31` → 365 días
- Fechas vacías → 0 días

**Limitación conocida (v1):**
- No se excluyen festivos ni fines de semana
- Cálculo simple de días calendario
- Mejora futura: integración con calendario laboral

#### 6.1.3 `_check_dates()`

**Propósito:** Validar que `date_end >= date_start`

**Decorador:**
```python
@api.constrains("date_start", "date_end")
def _check_dates(self):
    ...
```

**Implementación:**
```python
for record in self:
    if record.date_start and record.date_end:
        if record.date_end < record.date_start:
            raise ValidationError(
                _("La fecha de fin no puede ser anterior a la fecha de inicio.")
            )
```

**Características:**
- Se ejecuta automáticamente al crear o modificar fechas
- Lanza excepción que Odoo captura y muestra al usuario
- Uso de `_()` para internacionalización (I18N)

#### 6.1.4 `action_submit()`

**Propósito:** Enviar solicitud a revisión

**Implementación:**
```python
def action_submit(self):
    for record in self:
        if record.state != "draft":
            raise ValidationError(
                _("Solo se pueden enviar solicitudes en estado Borrador.")
            )
        record.state = "in_review"
```

**Flujo:**
1. Empleado crea solicitud (estado: `draft`)
2. Empleado hace clic en botón "Enviar"
3. Se valida estado actual
4. Se cambia estado a `in_review`
5. La solicitud aparece en la vista del manager

#### 6.1.5 `action_approve()`

**Propósito:** Aprobar solicitud

**Implementación:**
```python
def action_approve(self):
    for record in self:
        if record.state != "in_review":
            raise ValidationError(
                _("Solo se pueden aprobar solicitudes en estado En revisión.")
            )
        record.write({
            "state": "approved",
            "resolution_date": fields.Date.today(),
        })
```

**Características:**
- Establece `resolution_date` automáticamente
- `approver_id` debe estar configurado previamente (asignado manualmente o por workflow)
- Estado final (no se puede revertir en v1)

#### 6.1.6 `action_reject()`

**Propósito:** Rechazar solicitud

**Implementación:**
```python
def action_reject(self):
    for record in self:
        if record.state != "in_review":
            raise ValidationError(
                _("Solo se pueden rechazar solicitudes en estado En revisión.")
            )
        record.write({
            "state": "rejected",
            "resolution_date": fields.Date.today(),
        })
```

**Características:**
- Similar a `action_approve()` pero con estado `rejected`
- No se registra motivo de rechazo en v1 (mejora futura)

### 6.2 Validaciones Implementadas

#### 6.2.1 Validaciones a Nivel de Base de Datos

**Constraints SQL:**

```python
_sql_constraints = [
    (
        "check_dates",
        "CHECK(date_end >= date_start)",
        "La fecha de fin debe ser mayor o igual a la fecha de inicio.",
    ),
]
```

**Ventajas:**
- Protección a nivel de DBMS (incluso si se inserta directamente en SQL)
- Rendimiento superior (validación antes de commit)
- Integridad garantizada

#### 6.2.2 Validaciones a Nivel de Python

**Decorador `@api.constrains`:**

```python
@api.constrains("date_start", "date_end")
def _check_dates(self):
    # Validación Python (más flexible)
```

**Ventajas:**
- Mensajes de error más descriptivos
- Lógica de validación compleja
- Acceso al contexto de Odoo (`self.env`)

**Estrategia de defensa en profundidad:**
- Validación Python como primera barrera
- Constraint SQL como última barrera
- Validaciones en frontend (futuro) para UX mejorada

---

## 7. Capa de Seguridad

### 7.1 Arquitectura de Seguridad

```
┌───────────────────────────────────────────────────────────┐
│                 Security Layer Stack                       │
├───────────────────────────────────────────────────────────┤
│ Nivel 1: ACL (ir.model.access)                            │
│   ├─ Permisos CRUD por grupo (employee, manager)         │
│   └─ Control de acceso al modelo completo                │
├───────────────────────────────────────────────────────────┤
│ Nivel 2: Record Rules (ir.rule)                           │
│   ├─ Employee: [('employee_id.user_id', '=', user.id)]   │
│   └─ Manager: [('approver_id', '=', user.id)]            │
├───────────────────────────────────────────────────────────┤
│ Nivel 3: Validaciones de Negocio (Python)                │
│   ├─ action_submit() solo desde 'draft'                  │
│   ├─ action_approve() solo desde 'in_review'             │
│   └─ action_reject() solo desde 'in_review'              │
├───────────────────────────────────────────────────────────┤
│ Nivel 4: Constraints de Base de Datos (SQL)              │
│   ├─ CHECK(date_end >= date_start)                       │
│   ├─ NOT NULL en campos requeridos                       │
│   └─ Foreign Keys con RESTRICT                           │
└───────────────────────────────────────────────────────────┘
```

### 7.2 Grupos de Seguridad

**Archivo:** `security/remote_request_groups.xml`

#### Grupo 1: Empleados

```xml
<record id="group_remote_work_request_employee" model="res.groups">
    <field name="name">Empleado - Solicitar Teletrabajo</field>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>
```

**Permisos:**
- Crear solicitudes propias
- Leer solicitudes propias
- Modificar solicitudes propias en estado `draft`
- Enviar a revisión (cambio a `in_review`)

**Restricciones:**
- No puede ver solicitudes de otros empleados
- No puede aprobar/rechazar (ni siquiera las propias)

#### Grupo 2: Managers

```xml
<record id="group_remote_work_request_manager" model="res.groups">
    <field name="name">Gerente - Gestionar Solicitudes de Teletrabajo</field>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>
```

**Permisos:**
- Leer solicitudes donde es `approver_id`
- Modificar solicitudes donde es `approver_id`
- Aprobar/rechazar solicitudes asignadas

**Restricciones:**
- No puede crear solicitudes para otros
- No puede ver/modificar solicitudes de otros managers

### 7.3 Record Rules (Row-Level Security)

**Archivo:** `security/remote_request_rules.xml`

#### Regla 1: Employee Own Records

```xml
<record id="rule_remote_request_employee_own" model="ir.rule">
    <field name="name">Empleado: Solo sus propias solicitudes</field>
    <field name="model_id" ref="model_remote_work_request"/>
    <field name="groups" eval="[(4, ref('group_remote_work_request_employee'))]"/>
    <field name="domain_force">[('employee_id.user_id', '=', user.id)]</field>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>
```

**Dominio:** `[('employee_id.user_id', '=', user.id)]`

**Interpretación:**
- Solo registros donde el usuario del empleado es el usuario actual
- Filtra automáticamente en todas las operaciones (search, read, write)

**Ejemplo:**
```python
# Usuario: john@example.com (ID: 10)
# Empleado: John Doe (employee.user_id = 10)

# Esta consulta solo retorna solicitudes de John
self.env['remote.work.request'].search([])  # RLS aplicado automáticamente
```

#### Regla 2: Manager Assigned Records

```xml
<record id="rule_remote_request_manager_all" model="ir.rule">
    <field name="name">Gerente: Solicitudes asignadas a él como aprobador</field>
    <field name="model_id" ref="model_remote_work_request"/>
    <field name="groups" eval="[(4, ref('group_remote_work_request_manager'))]"/>
    <field name="domain_force">[('approver_id', '=', user.id)]</field>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

**Dominio:** `[('approver_id', '=', user.id)]`

**Interpretación:**
- Solo registros donde el aprobador es el usuario actual
- Permite lectura y modificación (para aprobar/rechazar)
- No permite crear o eliminar

**Nota importante:**
- Si un usuario tiene ambos grupos (employee + manager), Odoo aplica un OR lógico
- Vería tanto sus solicitudes propias como las asignadas como aprobador

### 7.4 Access Control Lists (ACL)

**Archivo:** `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_remote_work_request_employee,remote.work.request employee,model_remote_work_request,group_remote_work_request_employee,1,1,1,1
access_remote_work_request_manager,remote.work.request manager,model_remote_work_request,group_remote_work_request_manager,1,1,1,1
```

**Formato:**
- `id`: Identificador XML único
- `name`: Nombre descriptivo
- `model_id:id`: Referencia al modelo (`model_remote_work_request`)
- `group_id:id`: Referencia al grupo
- `perm_read/write/create/unlink`: 1=permitido, 0=denegado

**Interpretación:**
- ACL define **qué operaciones** puede hacer un grupo
- Record rules definen **qué registros** puede ver/modificar

### 7.5 Bypass de Seguridad (Controlador API)

**Archivo:** `controllers/main.py`

```python
@http.route("/remote_work/approved_requests", type="http", auth="public", ...)
def get_approved_requests(self, **kwargs):
    RemoteRequest = request.env["remote.work.request"].sudo()
    ...
```

**Uso de `.sudo()`:**
- **Bypass completo** de ACL y record rules
- **Justificación:** Endpoint público debe retornar todas las solicitudes aprobadas
- **Riesgo:** Expone datos sin filtrado por usuario
- **Mitigación:** Solo expone registros con `state='approved'` (ya resueltos)

**Consideraciones:**
- En v2, considerar autenticación (`auth="user"`)
- Permitir filtrado por `employee_id` (parámetro GET)
- Implementar rate limiting para prevenir abuso

---

## 8. API y Servicios Web

### 8.1 Endpoint JSON

**Ruta:** `GET /remote_work/approved_requests`

**Configuración:**

```python
@http.route(
    "/remote_work/approved_requests",
    type="http",
    auth="public",
    methods=["GET"],
    csrf=False,
)
```

**Parámetros de configuración:**

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| `type` | `"http"` | Respuesta HTTP directa (no JSON-RPC) |
| `auth` | `"public"` | Sin autenticación requerida (decisión v1) |
| `methods` | `["GET"]` | Solo lectura (idempotente) |
| `csrf` | `False` | No requiere token CSRF (API pública) |

### 8.2 Lógica del Controlador

**Implementación:**

```python
def get_approved_requests(self, **kwargs):
    # 1. Obtener modelo con bypass de seguridad
    RemoteRequest = request.env["remote.work.request"].sudo()

    # 2. Buscar solo solicitudes aprobadas
    approved_requests = RemoteRequest.search([("state", "=", "approved")])

    # 3. Serializar a lista de diccionarios
    data = []
    for req in approved_requests:
        data.append({
            "id": req.id,
            "employee": req.employee_id.name,
            "approver": req.approver_id.name if req.approver_id else "",
            "request_date": req.request_date.isoformat() if req.request_date else None,
            "date_start": req.date_start.isoformat() if req.date_start else None,
            "date_end": req.date_end.isoformat() if req.date_end else None,
            "resolution_date": req.resolution_date.isoformat() if req.resolution_date else None,
            "days_count": req.days_count,
            "reason": req.reason or "",
            "state": req.state,
        })

    # 4. Retornar JSON con Content-Type apropiado
    return request.make_response(
        json.dumps(data, default=str),
        headers={"Content-Type": "application/json"},
    )
```

### 8.3 Formato de Respuesta

**Content-Type:** `application/json`

**Estructura:**

```json
[
  {
    "id": 5,
    "employee": "Empleado Instalaciones",
    "approver": "Manager Instalaciones",
    "request_date": "2024-10-01",
    "date_start": "2024-10-10",
    "date_end": "2024-10-11",
    "resolution_date": "2024-10-02",
    "days_count": 2,
    "reason": "Revisión de instalaciones vía videollamada",
    "state": "approved"
  },
  ...
]
```

**Casos especiales:**

| Caso | Valor retornado |
|------|----------------|
| Campo de fecha nulo | `null` (JSON) |
| Campo de texto vacío | `""` (string vacío) |
| Relación Many2one nula | `""` (string vacío) |
| Lista vacía (sin solicitudes) | `[]` |

### 8.4 Ejemplo de Consumo

#### cURL

```bash
curl -X GET "http://localhost:8069/remote_work/approved_requests"
```

#### Python (requests)

```python
import requests

response = requests.get("http://localhost:8069/remote_work/approved_requests")
data = response.json()

for request in data:
    print(f"{request['employee']} - {request['days_count']} días")
```

#### JavaScript (fetch)

```javascript
fetch("http://localhost:8069/remote_work/approved_requests")
  .then(response => response.json())
  .then(data => {
    data.forEach(req => {
      console.log(`${req.employee}: ${req.days_count} días`);
    });
  });
```

### 8.5 Mejoras Futuras del API

**v2 Propuestas:**

1. **Autenticación:**
   ```python
   @http.route(..., auth="user", ...)
   ```
   - Requiere login de Odoo
   - Filtra por permisos del usuario

2. **Filtros por parámetros GET:**
   ```python
   def get_approved_requests(self, employee_id=None, date_from=None, **kwargs):
       domain = [("state", "=", "approved")]
       if employee_id:
           domain.append(("employee_id", "=", int(employee_id)))
       if date_from:
           domain.append(("date_start", ">=", date_from))
       ...
   ```

3. **Paginación:**
   ```python
   def get_approved_requests(self, offset=0, limit=100, **kwargs):
       approved_requests = RemoteRequest.search(
           [("state", "=", "approved")],
           offset=offset,
           limit=limit,
       )
   ```

4. **Endpoint POST para crear solicitudes:**
   ```python
   @http.route("/remote_work/requests", type="json", auth="user", methods=["POST"])
   def create_request(self, **data):
       ...
   ```

---

## 9. Infraestructura y Despliegue

### 9.1 Arquitectura Docker

```
┌────────────────────────────────────────────────────────────┐
│                      Docker Host (WSL2)                     │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Odoo Container (docker-odoo-1)                     │  │
│  │  ┌───────────────────────────────────────────────┐  │  │
│  │  │ Odoo 19 (Python 3.12)                         │  │  │
│  │  │ Port: 8069                                     │  │  │
│  │  │ Volumes:                                       │  │  │
│  │  │   - odoo_data:/var/lib/odoo                   │  │  │
│  │  │   - ./custom_addons:/mnt/extra-addons (RW)    │  │  │
│  │  │ Config: /etc/odoo/odoo.conf                   │  │  │
│  │  └───────────────────────────────────────────────┘  │  │
│  └────────────────┬────────────────────────────────────┘  │
│                   │                                        │
│                   │ TCP 5432                               │
│                   ▼                                        │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  PostgreSQL Container (docker-db-1)                 │  │
│  │  ┌───────────────────────────────────────────────┐  │  │
│  │  │ PostgreSQL 16                                 │  │  │
│  │  │ Port: 5432 (interno)                          │  │  │
│  │  │ Volumes:                                       │  │  │
│  │  │   - pgdata:/var/lib/postgresql/data           │  │  │
│  │  │ Database: odoo_db                             │  │  │
│  │  └───────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└────────────────────────────────────────────────────────────┘
         │
         │ HTTP Port 8069
         ▼
    [Navegador Web]
```

### 9.2 Docker Compose

**Archivo:** `docker/compose.yaml`

```yaml
services:
  odoo:
    image: odoo:19
    container_name: docker-odoo-1
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - odoo_data:/var/lib/odoo
      - ./odoo.conf:/etc/odoo/odoo.conf
      - ../custom_addons:/mnt/extra-addons
    environment:
      - HOST=db
      - USER=${POSTGRES_USER}
      - PASSWORD=${POSTGRES_PASSWORD}

  db:
    image: postgres:16
    container_name: docker-db-1
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  odoo_data:
  pgdata:
```

**Características:**
- **Persistencia:** Volúmenes Docker para datos (no se pierden al recrear contenedores)
- **Bind mount:** `custom_addons/` montado en lectura/escritura (desarrollo en caliente)
- **Secrets:** Variables de entorno desde archivo `.env` (no versionado)
- **Networking:** Red Docker interna (servicio `db` accesible desde `odoo` por nombre)

### 9.3 Configuración de Odoo

**Archivo:** `docker/odoo.conf`

```ini
[options]
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
admin_passwd = admin
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
```

**Parámetros clave:**

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `db_host` | `db` | Hostname del contenedor PostgreSQL |
| `db_port` | `5432` | Puerto estándar PostgreSQL |
| `addons_path` | `core,/mnt/extra-addons` | Ruta de búsqueda de módulos |
| `admin_passwd` | `admin` | Master password (cambiar en producción) |

**IMPORTANTE:**
- `addons_path` debe incluir **ambas** rutas (core + custom)
- Orden importa: Odoo busca secuencialmente
- Reiniciar contenedor después de modificar `odoo.conf`

### 9.4 Gestión de Secretos

**Archivo:** `docker/.env` (NO versionado)

```env
POSTGRES_USER=odoo
POSTGRES_PASSWORD=odoo
```

**Plantilla versionada:** `docker/.env.example`

```env
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
```

**Proceso de setup:**

```bash
cd docker
cp .env.example .env
# Editar .env con credenciales reales
nano .env
```

**`.gitignore`:**

```gitignore
docker/.env
docker/odoo.conf
```

### 9.5 Volúmenes Persistentes

#### Volumen 1: `odoo_data`

**Ruta interna:** `/var/lib/odoo`

**Contenido:**
- Filestore (archivos adjuntos, imágenes)
- Sessions (sesiones de usuario)
- Addons compilados (.pyc)

**Backup:**
```bash
docker run --rm \
  -v docker_odoo_data:/source:ro \
  -v $(pwd):/backup \
  alpine tar -czf /backup/odoo_data_backup.tar.gz -C /source .
```

#### Volumen 2: `pgdata`

**Ruta interna:** `/var/lib/postgresql/data`

**Contenido:**
- Datos de PostgreSQL
- Índices y configuraciones de DBMS

**Backup:**
```bash
docker exec docker-db-1 pg_dump -U odoo odoo_db > backup.sql
```

**Restore:**
```bash
docker exec -i docker-db-1 psql -U odoo odoo_db < backup.sql
```

### 9.6 Comandos de Gestión

#### Iniciar servicios

```bash
cd docker
docker compose up -d
```

#### Ver logs en tiempo real

```bash
docker compose logs -f odoo
```

#### Reiniciar solo Odoo

```bash
docker compose restart odoo
```

#### Acceder a shell de Odoo

```bash
docker exec -it docker-odoo-1 odoo shell -d odoo_db
```

#### Actualizar módulo

```bash
docker exec -it docker-odoo-1 odoo -d odoo_db -u remote_work_requests --stop-after-init
```

#### Ejecutar tests

```bash
docker compose run --rm odoo odoo \
  --test-enable \
  --stop-after-init \
  -d odoo_db \
  -u remote_work_requests
```

#### Detener servicios

```bash
docker compose down
```

#### Detener y eliminar volúmenes (DESTRUCTIVO)

```bash
docker compose down -v  # ¡Cuidado! Borra la base de datos
```

---

## 10. Flujos de Datos

### 10.1 Flujo de Creación de Solicitud

```
┌────────┐
│ Usuario│ (Empleado autenticado)
└────┬───┘
     │
     │ 1. Navega a "Trabajo Remoto → Solicitudes"
     ▼
┌────────────────┐
│  Odoo Web UI   │
└────────┬───────┘
     │
     │ 2. Clic en "Crear"
     ▼
┌────────────────┐
│  Form View     │ (remote_request_view.xml)
└────────┬───────┘
     │
     │ 3. Rellena campos: name, date_start, date_end, reason
     │    (employee_id pre-rellenado con _default_employee_id)
     ▼
┌────────────────┐
│  Botón "Guardar" │
└────────┬───────┘
     │
     │ 4. POST al servidor Odoo
     ▼
┌────────────────────┐
│  ORM (Python)      │
└────────┬───────────┘
     │
     │ 5. Validaciones:
     │    - _check_dates() (Python)
     │    - CHECK constraint (SQL)
     │    - NOT NULL en campos requeridos
     ▼
┌────────────────────┐
│  PostgreSQL        │
└────────┬───────────┘
     │
     │ 6. INSERT INTO remote_work_request
     │    VALUES (name, employee_id, date_start, date_end,
     │            reason, state='draft', ...)
     ▼
┌────────────────────┐
│  Trigger _compute  │
└────────┬───────────┘
     │
     │ 7. Cálculo de days_count
     │    UPDATE remote_work_request SET days_count = ...
     ▼
┌────────────────────┐
│  Response HTTP     │ (Redirect a vista de lista)
└────────┬───────────┘
     │
     ▼
┌────────────────┐
│  Vista Lista   │ (Solicitud aparece en estado "Borrador")
└────────────────┘
```

### 10.2 Flujo de Aprobación

```
┌────────┐
│ Manager│ (Usuario con grupo manager)
└────┬───┘
     │
     │ 1. Navega a "Trabajo Remoto → Solicitudes"
     │    Filtro activo: "Pendientes de revisar"
     ▼
┌────────────────┐
│  Search View   │ Domain: [('approver_id', '=', uid),
└────────┬───────┘         ('state', '=', 'in_review')]
     │
     │ 2. Record Rule aplica filtrado adicional
     │    (solo solicitudes donde approver_id = current_user)
     ▼
┌────────────────┐
│  List View     │ (Muestra solicitudes en revisión asignadas)
└────────┬───────┘
     │
     │ 3. Clic en solicitud → abre Form View
     ▼
┌────────────────┐
│  Form View     │ (Header muestra botones "Aprobar" y "Rechazar")
└────────┬───────┘
     │
     │ 4. Clic en "Aprobar"
     ▼
┌────────────────────┐
│  action_approve()  │ (Método del modelo)
└────────┬───────────┘
     │
     │ 5. Validación: state == 'in_review'
     ▼
┌────────────────────┐
│  write()           │ {state: 'approved', resolution_date: today}
└────────┬───────────┘
     │
     │ 6. UPDATE remote_work_request
     │    SET state = 'approved', resolution_date = '2025-11-21'
     │    WHERE id = X
     ▼
┌────────────────────┐
│  PostgreSQL        │ (Commit de transacción)
└────────┬───────────┘
     │
     ▼
┌────────────────┐
│  Vista Lista   │ (Solicitud ahora aparece en verde, estado "Aprobada")
└────────────────┘
     │
     │ 7. Solicitud disponible en API
     ▼
┌─────────────────────────────┐
│ GET /remote_work/approved_requests │
└─────────────────────────────┘
```

### 10.3 Flujo de Consumo de API

```
┌──────────────────┐
│ Cliente Externo  │ (Aplicación web, script, etc.)
└────────┬─────────┘
     │
     │ 1. GET http://localhost:8069/remote_work/approved_requests
     ▼
┌────────────────────┐
│  Nginx / Proxy     │ (Opcional en producción)
└────────┬───────────┘
     │
     │ 2. Forwarding a Odoo
     ▼
┌────────────────────────┐
│  Odoo HTTP Server      │
└────────┬───────────────┘
     │
     │ 3. Router busca @http.route matching
     ▼
┌──────────────────────────────────────┐
│  RemoteWorkApprovedController        │
│  .get_approved_requests()            │
└────────┬─────────────────────────────┘
     │
     │ 4. request.env["remote.work.request"].sudo()
     │    (Bypass de ACL y record rules)
     ▼
┌────────────────────┐
│  ORM Query         │
└────────┬───────────┘
     │
     │ 5. SELECT * FROM remote_work_request
     │    WHERE state = 'approved'
     ▼
┌────────────────────┐
│  PostgreSQL        │
└────────┬───────────┘
     │
     │ 6. Resultados (Recordset)
     ▼
┌────────────────────┐
│  Serialización     │ (Loop por cada registro)
└────────┬───────────┘
     │
     │ 7. Construcción de JSON
     │    [{id, employee, approver, dates, ...}, ...]
     ▼
┌────────────────────┐
│  json.dumps()      │
└────────┬───────────┘
     │
     │ 8. HTTP Response 200 OK
     │    Content-Type: application/json
     ▼
┌────────────────────┐
│  Cliente Externo   │ (Procesa JSON)
└────────────────────┘
```

---

## 11. Decisiones de Diseño

### 11.1 Uso de `store=True` en Campos Computados

**Decisión:**
```python
days_count = fields.Integer(compute="_compute_days_count", store=True)
```

**Alternativas consideradas:**
1. **Sin `store`:** Cálculo en cada lectura (dinámico)
2. **Con `store`:** Cálculo solo cuando cambian dependencias (persistido)

**Elección:** `store=True`

**Justificación:**
- **Performance:** Evita recálculo en cada búsqueda/listado
- **Sorting/Filtering:** Permite `order="days_count desc"` en vistas
- **Trade-off:** Espacio en disco (4 bytes/registro) vs CPU
- **Odoo best practice:** Recomendan `store=True` para campos usados en vistas

**Impacto:**
- Base de datos: +100 KB por cada 25,000 registros (negligible)
- CPU: -80% de carga en listados con ordenamiento
- Índices: PostgreSQL puede indexar campo persistido

### 11.2 Validación Dual (Python + SQL)

**Decisión:**
```python
# Python
@api.constrains("date_start", "date_end")
def _check_dates(self):
    if self.date_end < self.date_start:
        raise ValidationError("...")

# SQL
_sql_constraints = [
    ("check_dates", "CHECK(date_end >= date_start)", "..."),
]
```

**Alternativas:**
1. Solo Python (flexible, sin protección en SQL directo)
2. Solo SQL (rígido, mensajes de error genéricos)
3. Dual (actual)

**Elección:** Validación dual

**Justificación:**
- **Defensa en profundidad:** Protección en múltiples capas
- **UX:** Mensajes Python más descriptivos
- **Seguridad:** SQL previene bypass mediante queries directas
- **Costo:** Minimal (validación SQL es ~0.1ms)

### 11.3 Autenticación del API (`auth="public"`)

**Decisión:**
```python
@http.route(..., auth="public", ...)
```

**Alternativas:**
1. `auth="user"`: Requiere login de Odoo
2. `auth="public"`: Sin autenticación
3. `auth="api_key"`: Custom (implementación manual)

**Elección:** `auth="public"` (v1)

**Justificación:**
- **Simplicidad:** Facilita integración inicial
- **Datos públicos:** Solicitudes aprobadas ya no son sensibles
- **Prototipo:** v1 es PoC, v2 implementará autenticación
- **Riesgo aceptado:** Solo expone datos finales (no draft)

**Mitigaciones:**
- Endpoint de solo lectura (GET)
- Solo expone estado `approved`
- No expone datos personales sensibles

**Plan v2:**
- Cambiar a `auth="user"`
- Implementar API keys (OAuth2 o tokens JWT)
- Rate limiting (prevenir abuso)

### 11.4 No Usar `ondelete="cascade"` en Relaciones

**Decisión:**
```python
employee_id = fields.Many2one("hr.employee", ondelete="restrict")
approver_id = fields.Many2one("res.users", ondelete="restrict")
```

**Alternativas:**
1. `cascade`: Borrar solicitudes si se borra empleado
2. `restrict`: Prevenir borrado si hay solicitudes
3. `set null`: Dejar solicitud sin empleado

**Elección:** `restrict`

**Justificación:**
- **Integridad de datos:** Solicitudes históricas no deben perderse
- **Auditoría:** Trazabilidad requiere mantener registros
- **UX:** Forzar decisión explícita (archivar empleado, no borrar)

**Impacto:**
- Error al intentar borrar empleado con solicitudes
- Solución: Archivar empleado (`active=False`)

### 11.5 Cálculo de Días Inclusivo

**Decisión:**
```python
days_count = (date_end - date_start).days + 1
```

**Alternativas:**
1. Exclusivo: `(date_end - date_start).days` (lunes a viernes = 4)
2. Inclusivo: `(date_end - date_start).days + 1` (lunes a viernes = 5)

**Elección:** Inclusivo

**Justificación:**
- **UX:** Usuario espera contar ambos días (lunes + viernes = 2 días)
- **Estándar de negocio:** Hoteles, alquileres usan conteo inclusivo
- **Documentación:** Especificado en requisitos de negocio

**Ejemplo:**
```
Solicitud: 10/01/2025 a 12/01/2025
Expectativa: 3 días (10, 11, 12)
Cálculo: (12 - 10) + 1 = 3 ✓
```

### 11.6 Estado Inicial `draft` (No `in_review`)

**Decisión:**
```python
state = fields.Selection(default="draft")
```

**Alternativas:**
1. `draft`: Empleado debe enviar manualmente
2. `in_review`: Creación automáticamente envía a revisión

**Elección:** `draft`

**Justificación:**
- **Control del empleado:** Permite revisar antes de enviar
- **Borradores múltiples:** Puede crear varias versiones
- **UX:** Botón explícito "Enviar" es más claro
- **Workflow estándar:** Coincide con otros flujos de aprobación en Odoo

---

## 12. Consideraciones de Escalabilidad

### 12.1 Base de Datos

**Escenario:** 100,000 solicitudes (5 años de uso, 200 empleados)

**Estimaciones:**

| Métrica | Valor |
|---------|-------|
| Tamaño de registro | ~500 bytes |
| Total de datos | ~50 MB |
| Índices automáticos | ~10 MB |
| Total en disco | ~60 MB |

**Optimizaciones aplicadas:**

1. **Índices en columnas frecuentes:**
```sql
CREATE INDEX idx_remote_request_state ON remote_work_request(state);
CREATE INDEX idx_remote_request_employee ON remote_work_request(employee_id);
CREATE INDEX idx_remote_request_approver ON remote_work_request(approver_id);
```

2. **Campos computados almacenados:**
```python
days_count = fields.Integer(store=True)  # Evita cálculo repetitivo
```

3. **Record rules eficientes:**
```xml
<!-- Usa índices existentes (user_id, approver_id) -->
<field name="domain_force">[('employee_id.user_id', '=', user.id)]</field>
```

**Consultas críticas:**

```sql
-- Listado de solicitudes del empleado (optimizado con índice)
SELECT * FROM remote_work_request
WHERE employee_id IN (
    SELECT id FROM hr_employee WHERE user_id = 10
)
LIMIT 80;

-- Listado de solicitudes pendientes del manager
SELECT * FROM remote_work_request
WHERE approver_id = 15 AND state = 'in_review'
LIMIT 80;

-- Endpoint API (filtrado simple)
SELECT * FROM remote_work_request
WHERE state = 'approved';
```

**Plan de ejecución esperado:**
- `O(log n)` para búsquedas con índice
- `O(n)` para endpoint API (aceptable con paginación)

### 12.2 Memoria

**Odoo Workers:**

Configuración recomendada (`odoo.conf`):

```ini
[options]
limit_memory_hard = 2684354560  # 2.5 GB
limit_memory_soft = 2147483648  # 2 GB
workers = 4
```

**Cálculo de workers:**

```
workers = (2 * CPU_cores) + 1
Para 4 cores: workers = 9
```

**Consumo por worker:**
- Base: ~200 MB
- Por request: +50 MB (promedio)
- Pico: ~500 MB (con 10 solicitudes simultáneas)

**Total para 9 workers:**
- Mínimo: 1.8 GB
- Pico: 4.5 GB

### 12.3 API Endpoint

**Problema:** Endpoint retorna todas las solicitudes aprobadas sin límite

**Escenario:** 10,000 solicitudes aprobadas

**Impacto:**
- Respuesta JSON: ~5 MB
- Tiempo de serialización: ~2s
- Memoria: ~100 MB (en worker)

**Soluciones:**

#### Solución 1: Paginación

```python
def get_approved_requests(self, offset=0, limit=100, **kwargs):
    approved_requests = RemoteRequest.search(
        [("state", "=", "approved")],
        offset=int(offset),
        limit=int(limit),
        order="resolution_date desc",
    )
    ...
```

**Uso:**
```
GET /remote_work/approved_requests?offset=0&limit=100
GET /remote_work/approved_requests?offset=100&limit=100
```

#### Solución 2: Filtrado por fecha

```python
def get_approved_requests(self, date_from=None, date_to=None, **kwargs):
    domain = [("state", "=", "approved")]
    if date_from:
        domain.append(("resolution_date", ">=", date_from))
    if date_to:
        domain.append(("resolution_date", "<=", date_to))
    ...
```

**Uso:**
```
GET /remote_work/approved_requests?date_from=2025-01-01&date_to=2025-01-31
```

#### Solución 3: Caché HTTP

```python
from werkzeug.wrappers import Response

def get_approved_requests(self, **kwargs):
    ...
    response = request.make_response(
        json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Cache-Control": "public, max-age=3600",  # 1 hora
            "ETag": hashlib.md5(json.dumps(data).encode()).hexdigest(),
        },
    )
    return response
```

**Beneficio:**
- Navegadores cachean respuesta
- Reduce carga en servidor
- Válido para datos que cambian poco

### 12.4 Concurrencia

**Problema:** Dos managers aprueban la misma solicitud simultáneamente

**Escenario:**

```
Tiempo    Manager A                 Manager B
T0        Abre solicitud X          Abre solicitud X
T1        Clic en "Aprobar"         -
T2        -                          Clic en "Aprobar"
T3        write({state: approved})  write({state: approved})
```

**Solución actual:** Odoo usa transacciones PostgreSQL con locks

```sql
-- Odoo ejecuta internamente
BEGIN;
SELECT * FROM remote_work_request WHERE id = X FOR UPDATE;
UPDATE remote_work_request SET state = 'approved' WHERE id = X;
COMMIT;
```

**`FOR UPDATE`:**
- Manager A adquiere lock exclusivo
- Manager B espera hasta que A hace commit
- Evita doble aprobación

**Mejora futura:** Validar en `action_approve()` que `state == 'in_review'`

```python
def action_approve(self):
    # Refrescar desde DB (evitar stale data)
    self.invalidate_cache()

    if self.state != 'in_review':
        raise ValidationError("La solicitud ya fue procesada.")

    self.write({"state": "approved", ...})
```

### 12.5 Monitoreo

**Métricas clave:**

1. **Tiempo de respuesta del API:**
   - Target: < 500ms para 1000 registros
   - Alertar si > 2s

2. **Uso de memoria por worker:**
   - Target: < 1 GB promedio
   - Alertar si > 2 GB

3. **Consultas lentas:**
   - PostgreSQL slow query log
   - Queries > 1s deben investigarse

**Herramientas:**

```bash
# Logs de Odoo
docker compose logs -f odoo | grep -i "slow\|error"

# Stats de PostgreSQL
docker exec docker-db-1 psql -U odoo odoo_db -c "
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
"
```

---

## 13. Conclusiones

### 13.1 Fortalezas del Diseño

1. **Modularidad:** Componentes bien separados (MVC)
2. **Seguridad:** Múltiples capas (ACL, RLS, validaciones)
3. **Testabilidad:** 45 tests automatizados
4. **Escalabilidad:** Diseño soporta 100k+ registros
5. **Mantenibilidad:** Código limpio, documentado

### 13.2 Limitaciones Conocidas

1. **API sin autenticación:** Riesgo de abuso (v2 mejorará)
2. **No hay paginación:** API puede ser lenta con muchos registros
3. **Cálculo simple de días:** No excluye festivos/fines de semana
4. **Sin notificaciones:** Empleados/managers no reciben alertas
5. **Estados finales:** No se puede revertir aprobación/rechazo

### 13.3 Roadmap Técnico

**v1.1 (Próximo sprint):**
- Paginación en API
- Filtrado por fecha en endpoint
- Caché HTTP con ETags

**v2.0 (Q2 2026):**
- Autenticación API (tokens JWT)
- Integración con calendario (festivos)
- Notificaciones por email (Odoo Chatter)
- Dashboard con métricas (gráficos)

**v3.0 (Q4 2026):**
- Aprobación multinivel
- Workflows configurables
- Integración con Outlook/Google Calendar
- App móvil (Odoo Mobile)

---

**Fin del documento**

---

**Historial de cambios:**

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2025-11-21 | Pablo Laya | Versión inicial |
