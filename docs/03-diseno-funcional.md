# 03 — Diseño Funcional: Remote Work Requests (Odoo 19)

**Proyecto:** Sistema de Gestión de Solicitudes de Teletrabajo
**Versión del documento:** 1.0
**Fecha:** 21 de noviembre de 2025
**Autor:** Pablo Laya

---

## Índice

1. [Introducción](#1-introducción)
2. [Casos de Uso](#2-casos-de-uso)
3. [Flujos de Trabajo](#3-flujos-de-trabajo)
4. [Especificación de Pantallas](#4-especificación-de-pantallas)
5. [Reglas de Negocio Detalladas](#5-reglas-de-negocio-detalladas)
6. [Roles y Permisos](#6-roles-y-permisos)
7. [Escenarios de Validación](#7-escenarios-de-validación)
8. [Mensajes de Error y Feedback](#8-mensajes-de-error-y-feedback)
9. [Casos Especiales](#9-casos-especiales)
10. [Glosario de Términos](#10-glosario-de-términos)

---

## 1. Introducción

### 1.1 Propósito del Documento

Este documento describe la funcionalidad del sistema de gestión de solicitudes de teletrabajo desde la perspectiva del usuario y del negocio. Define qué hace el sistema, cómo interactúan los usuarios con él, y cuáles son las reglas que rigen su comportamiento.

### 1.2 Alcance Funcional

El sistema permite:
- A los **empleados**: crear, consultar y enviar solicitudes de teletrabajo
- A los **managers**: revisar, aprobar o rechazar solicitudes asignadas
- A **sistemas externos**: consultar solicitudes aprobadas vía API REST

### 1.3 Usuarios del Sistema

| Rol | Descripción | Grupo de Odoo |
|-----|-------------|---------------|
| **Empleado** | Persona que solicita días de teletrabajo | `group_remote_work_request_employee` |
| **Manager** | Responsable que aprueba/rechaza solicitudes | `group_remote_work_request_manager` |
| **Administrador** | Usuario con acceso completo (IT/HR Admin) | `base.group_system` |
| **Sistema Externo** | Aplicación que consume el API | N/A (acceso público) |

---

## 2. Casos de Uso

### 2.1 Diagrama de Casos de Uso

```
                    ┌─────────────────────────────────┐
                    │  Sistema Remote Work Requests   │
                    └─────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
   ┌──────────┐          ┌──────────┐          ┌──────────┐
   │ Empleado │          │ Manager  │          │ Sistema  │
   │          │          │          │          │ Externo  │
   └────┬─────┘          └────┬─────┘          └────┬─────┘
        │                     │                     │
        │                     │                     │
   UC-01: Crear Solicitud    │                     │
   UC-02: Ver Mis Solicitudes│                     │
   UC-03: Enviar a Revisión  │                     │
        │                     │                     │
        │            UC-04: Ver Solicitudes        │
        │                  Asignadas               │
        │            UC-05: Aprobar Solicitud      │
        │            UC-06: Rechazar Solicitud     │
        │                     │                     │
        │                     │         UC-07: Consultar
        │                     │              Aprobadas (API)
```

### 2.2 UC-01: Crear Solicitud de Teletrabajo

**Actor:** Empleado

**Precondiciones:**
- Usuario autenticado en Odoo
- Usuario tiene grupo `group_remote_work_request_employee`
- Usuario está asociado a un empleado en HR

**Flujo Principal:**

1. Usuario navega a **Trabajo Remoto → Solicitudes**
2. Usuario hace clic en botón **"Crear"**
3. Sistema muestra formulario vacío con:
   - Campo `employee_id` pre-rellenado con el empleado actual
   - Campos `date_start`, `date_end`, `reason` vacíos
   - Estado en `draft`
4. Usuario rellena:
   - **Nombre:** "Teletrabajo junio"
   - **Fecha inicio:** 2025-06-01
   - **Fecha fin:** 2025-06-05
   - **Motivo:** "Mudanza de domicilio"
5. Usuario hace clic en **"Guardar"**
6. Sistema valida datos (ver UC-01a)
7. Sistema calcula `days_count` = 5 días
8. Sistema guarda registro con `state = 'draft'`
9. Sistema muestra mensaje: "Solicitud creada correctamente"
10. Sistema redirige a vista de lista

**Flujo Alternativo UC-01a: Error de Validación**

4a. Sistema detecta `date_end < date_start`
4b. Sistema muestra error: "La fecha de fin no puede ser anterior a la fecha de inicio."
4c. Usuario corrige fechas
4d. Continúa en paso 5

**Postcondiciones:**
- Registro creado en base de datos con `state = 'draft'`
- Solicitud visible en "Mis solicitudes"
- Campo `days_count` calculado correctamente

**Requisitos de Negocio:** REQ-001, REQ-002, REQ-005

---

### 2.3 UC-02: Ver Mis Solicitudes

**Actor:** Empleado

**Precondiciones:**
- Usuario autenticado
- Usuario tiene al menos una solicitud creada

**Flujo Principal:**

1. Usuario navega a **Trabajo Remoto → Solicitudes**
2. Sistema aplica filtro automático por record rule: `[('employee_id.user_id', '=', user.id)]`
3. Sistema muestra lista con columnas:
   - Nombre
   - Empleado (el usuario actual)
   - Fecha de solicitud
   - Fecha inicio
   - Fecha fin
   - Días
   - Estado (con colores)
4. Usuario puede aplicar filtros adicionales:
   - "Borrador"
   - "En revisión"
   - "Aprobadas"
   - "Rechazadas"
5. Usuario hace clic en una solicitud para ver detalle

**Postcondiciones:**
- Usuario visualiza solo sus propias solicitudes
- No puede ver solicitudes de otros empleados

**Requisitos de Negocio:** REQ-007, REQ-010

---

### 2.4 UC-03: Enviar Solicitud a Revisión

**Actor:** Empleado

**Precondiciones:**
- Solicitud existe con `state = 'draft'`
- Usuario es el propietario de la solicitud

**Flujo Principal:**

1. Usuario abre solicitud en modo formulario
2. Usuario verifica datos:
   - Fechas correctas
   - Motivo completo
3. Usuario hace clic en botón **"Enviar"** (visible solo si `state = 'draft'`)
4. Sistema ejecuta método `action_submit()`
5. Sistema valida `state == 'draft'` (ver UC-03a si falla)
6. Sistema cambia `state` a `'in_review'`
7. Sistema muestra mensaje: "Solicitud enviada a revisión"
8. Botón "Enviar" desaparece
9. Botones "Aprobar" y "Rechazar" aparecen (si usuario es manager)

**Flujo Alternativo UC-03a: Estado Inválido**

5a. Sistema detecta `state != 'draft'` (ej: ya está en revisión)
5b. Sistema muestra error: "Solo se pueden enviar solicitudes en estado Borrador."
5c. Usuario reconoce error y cierra formulario

**Postcondiciones:**
- Solicitud en estado `in_review`
- Visible para el manager asignado (si `approver_id` está configurado)
- No se puede volver a estado `draft` (sin eliminar y recrear)

**Requisitos de Negocio:** REQ-003, REQ-006

---

### 2.5 UC-04: Ver Solicitudes Asignadas

**Actor:** Manager

**Precondiciones:**
- Usuario autenticado
- Usuario tiene grupo `group_remote_work_request_manager`
- Existen solicitudes donde `approver_id = usuario_actual`

**Flujo Principal:**

1. Usuario (manager) navega a **Trabajo Remoto → Solicitudes**
2. Sistema aplica record rule: `[('approver_id', '=', user.id)]`
3. Sistema muestra lista de solicitudes asignadas
4. Usuario aplica filtro **"Pendientes de revisar"**
5. Sistema filtra por: `[('approver_id', '=', uid), ('state', '=', 'in_review')]`
6. Usuario visualiza solicitudes en estado `in_review` asignadas a él

**Postcondiciones:**
- Manager solo ve solicitudes donde es aprobador
- No puede ver solicitudes de otros managers

**Requisitos de Negocio:** REQ-008, REQ-011

---

### 2.6 UC-05: Aprobar Solicitud

**Actor:** Manager

**Precondiciones:**
- Solicitud existe con `state = 'in_review'`
- Usuario es el aprobador (`approver_id = user.id`)
- Usuario tiene grupo `group_remote_work_request_manager`

**Flujo Principal:**

1. Usuario abre solicitud en modo formulario
2. Usuario revisa:
   - Empleado solicitante
   - Fechas solicitadas
   - Motivo
   - Días solicitados
3. Usuario hace clic en botón **"Aprobar"** (verde)
4. Sistema ejecuta método `action_approve()`
5. Sistema valida `state == 'in_review'` (ver UC-05a si falla)
6. Sistema actualiza:
   - `state = 'approved'`
   - `resolution_date = hoy`
7. Sistema guarda cambios en base de datos
8. Sistema muestra mensaje: "Solicitud aprobada correctamente"
9. Formulario muestra estado "Aprobada" (verde)
10. Botones "Aprobar" y "Rechazar" desaparecen

**Flujo Alternativo UC-05a: Estado Inválido**

5a. Sistema detecta `state != 'in_review'` (ej: ya aprobada)
5b. Sistema muestra error: "Solo se pueden aprobar solicitudes en estado En revisión."
5c. Usuario reconoce error y cierra formulario

**Postcondiciones:**
- Solicitud en estado `approved`
- `resolution_date` establecida
- Solicitud disponible en endpoint `/remote_work/approved_requests`
- Estado no se puede revertir

**Requisitos de Negocio:** REQ-004, REQ-006

---

### 2.7 UC-06: Rechazar Solicitud

**Actor:** Manager

**Precondiciones:**
- Solicitud existe con `state = 'in_review'`
- Usuario es el aprobador (`approver_id = user.id`)
- Usuario tiene grupo `group_remote_work_request_manager`

**Flujo Principal:**

1. Usuario abre solicitud en modo formulario
2. Usuario revisa información de la solicitud
3. Usuario decide no aprobar
4. Usuario hace clic en botón **"Rechazar"** (rojo)
5. Sistema ejecuta método `action_reject()`
6. Sistema valida `state == 'in_review'` (ver UC-06a si falla)
7. Sistema actualiza:
   - `state = 'rejected'`
   - `resolution_date = hoy`
8. Sistema guarda cambios
9. Sistema muestra mensaje: "Solicitud rechazada"
10. Formulario muestra estado "Rechazada" (rojo)
11. Botones "Aprobar" y "Rechazar" desaparecen

**Flujo Alternativo UC-06a: Estado Inválido**

6a. Sistema detecta `state != 'in_review'`
6b. Sistema muestra error: "Solo se pueden rechazar solicitudes en estado En revisión."
6c. Usuario reconoce error

**Postcondiciones:**
- Solicitud en estado `rejected`
- `resolution_date` establecida
- Solicitud NO aparece en API de aprobadas
- Estado no se puede revertir

**Requisitos de Negocio:** REQ-004, REQ-006

**Nota:** En v1 no se registra motivo de rechazo. Mejora futura: campo `rejection_reason`.

---

### 2.8 UC-07: Consultar Solicitudes Aprobadas (API)

**Actor:** Sistema Externo

**Precondiciones:**
- Endpoint accesible en red
- Al menos una solicitud con `state = 'approved'`

**Flujo Principal:**

1. Sistema externo envía: `GET http://odoo-server:8069/remote_work/approved_requests`
2. Servidor Odoo recibe petición
3. Controlador ejecuta `get_approved_requests()`
4. Sistema busca registros con `state = 'approved'` (con `.sudo()`)
5. Sistema serializa registros a JSON:
   ```json
   [
     {
       "id": 5,
       "employee": "John Doe",
       "approver": "Jane Smith",
       "request_date": "2025-01-15",
       "date_start": "2025-01-20",
       "date_end": "2025-01-25",
       "resolution_date": "2025-01-18",
       "days_count": 6,
       "reason": "Work from home",
       "state": "approved"
     }
   ]
   ```
6. Sistema retorna HTTP 200 OK con JSON
7. Sistema externo procesa datos

**Flujo Alternativo UC-07a: Sin Solicitudes Aprobadas**

4a. Sistema no encuentra registros con `state = 'approved'`
4b. Sistema retorna `[]` (array vacío)
4c. Sistema externo maneja lista vacía

**Postcondiciones:**
- Datos de solicitudes aprobadas expuestos a sistema externo
- No requiere autenticación (acceso público)

**Requisitos de Negocio:** REQ-009

---

## 3. Flujos de Trabajo

### 3.1 Flujo Completo: Solicitud Aprobada

```
┌───────────────────────────────────────────────────────────────┐
│                  FLUJO: Solicitud Aprobada                     │
└───────────────────────────────────────────────────────────────┘

Empleado                Sistema                  Manager
   │                       │                         │
   │  1. Crear Solicitud   │                         │
   ├──────────────────────>│                         │
   │                       │ (state = draft)         │
   │                       │                         │
   │  2. Rellenar Datos    │                         │
   ├──────────────────────>│                         │
   │                       │ Validar fechas          │
   │                       │ Calcular days_count     │
   │                       │                         │
   │  3. Guardar (draft)   │                         │
   ├──────────────────────>│                         │
   │<─────────────────────┤                         │
   │   OK (guardado)       │                         │
   │                       │                         │
   │  4. Enviar a Revisión │                         │
   ├──────────────────────>│                         │
   │                       │ action_submit()         │
   │                       │ (state = in_review)     │
   │<─────────────────────┤                         │
   │   OK (enviado)        │                         │
   │                       │                         │
   │                       │ Notificación (futuro)   │
   │                       ├────────────────────────>│
   │                       │                         │
   │                       │   5. Revisar Solicitud  │
   │                       │<────────────────────────┤
   │                       │ (filtro: asignadas a mí)│
   │                       │                         │
   │                       │   6. Decidir Aprobar    │
   │                       │<────────────────────────┤
   │                       │ action_approve()        │
   │                       │ state = approved        │
   │                       │ resolution_date = hoy   │
   │                       │                         │
   │  Notificación (futuro)│                         │
   │<─────────────────────┤                         │
   │  (aprobado)           │                         │
   │                       │                         │
   │  7. Consultar Estado  │                         │
   ├──────────────────────>│                         │
   │<─────────────────────┤                         │
   │   (state = approved)  │                         │
   │                       │                         │
   │                       │                         │
                          ▼
                    (Disponible en API)
```

### 3.2 Flujo Alternativo: Solicitud Rechazada

```
Empleado                Sistema                  Manager
   │                       │                         │
   │ [Steps 1-4 iguales]   │                         │
   │                       │                         │
   │                       │   5. Revisar Solicitud  │
   │                       │<────────────────────────┤
   │                       │                         │
   │                       │   6. Decidir Rechazar   │
   │                       │<────────────────────────┤
   │                       │ action_reject()         │
   │                       │ state = rejected        │
   │                       │ resolution_date = hoy   │
   │                       │                         │
   │  Notificación (futuro)│                         │
   │<─────────────────────┤                         │
   │  (rechazado)          │                         │
   │                       │                         │
   │  7. Consultar Estado  │                         │
   ├──────────────────────>│                         │
   │<─────────────────────┤                         │
   │   (state = rejected)  │                         │
   │                       │                         │
                          ▼
                  (NO aparece en API)
```

### 3.3 Diagrama de Estados

```
┌─────────────────────────────────────────────────────────────┐
│                   MÁQUINA DE ESTADOS                         │
└─────────────────────────────────────────────────────────────┘

      ┌──────────┐
      │  DRAFT   │ Estado inicial
      │ (Borrador)│
      └─────┬────┘
            │
            │ action_submit()
            │ (Empleado)
            │
      ┌─────▼─────┐
      │ IN_REVIEW │
      │(En revisión)│
      └─────┬─────┘
            │
            ├───────────────────┬───────────────────┐
            │                   │                   │
            │ action_approve()  │ action_reject()   │
            │ (Manager)         │ (Manager)         │
            │                   │                   │
      ┌─────▼─────┐       ┌─────▼─────┐            │
      │ APPROVED  │       │ REJECTED  │            │
      │ (Aprobada)│       │(Rechazada)│            │
      └───────────┘       └───────────┘            │
      [Estado Final]      [Estado Final]           │

Leyenda:
- Estados en mayúsculas: valores técnicos
- Estados en paréntesis: etiquetas de usuario
- Flechas: transiciones permitidas
```

**Invariantes de Estado:**

| Estado | Transiciones Permitidas | Transiciones Prohibidas |
|--------|------------------------|------------------------|
| `draft` | → `in_review` | → `approved`, → `rejected` |
| `in_review` | → `approved`, → `rejected` | → `draft` |
| `approved` | Ninguna (final) | → `draft`, → `in_review`, → `rejected` |
| `rejected` | Ninguna (final) | → `draft`, → `in_review`, → `approved` |

---

## 4. Especificación de Pantallas

### 4.1 Pantalla: Lista de Solicitudes

**Vista:** `view_remote_request_list`

**Ubicación:** Trabajo Remoto → Solicitudes

**Elementos UI:**

| Elemento | Tipo | Descripción |
|----------|------|-------------|
| Botón "Crear" | Button | Abre formulario para nueva solicitud |
| Columna "Nombre" | Char | Título de la solicitud |
| Columna "Empleado" | Many2one | Nombre del empleado solicitante |
| Columna "Fecha de solicitud" | Date | Fecha de creación |
| Columna "Inicio" | Date | Fecha inicio teletrabajo |
| Columna "Fin" | Date | Fecha fin teletrabajo |
| Columna "Días" | Integer | Días calculados (inclusivo) |
| Columna "Estado" | Selection | Badge con color según estado |
| Columna "Aprobador" | Many2one | Nombre del manager aprobador |
| Filtros laterales | Filter buttons | Borrador, En revisión, Aprobadas, Rechazadas |
| Buscador | Search | Búsqueda por nombre, empleado, aprobador |

**Colores de Estado:**

```
draft      → Gris (muted)
in_review  → Azul (info)
approved   → Verde (success)
rejected   → Rojo (danger)
```

**Captura de pantalla:** `assets/05-screenshot-app-list.jpg`

---

### 4.2 Pantalla: Formulario de Solicitud (Modo Creación)

**Vista:** `view_remote_request_form`

**Ubicación:** Trabajo Remoto → Solicitudes → Crear

**Secciones:**

#### Sección 1: Header (Barra Superior)

| Elemento | Condición | Acción |
|----------|-----------|--------|
| Botón "Enviar" | `state == 'draft'` | Ejecuta `action_submit()` |
| Botón "Aprobar" | `state == 'in_review'` | Ejecuta `action_approve()` |
| Botón "Rechazar" | `state == 'in_review'` | Ejecuta `action_reject()` |
| StatusBar (Estado) | Siempre visible | Muestra estado actual |

#### Sección 2: Información Básica

| Campo | Tipo | Requerido | Default | Readonly |
|-------|------|-----------|---------|----------|
| **Nombre** | Char(255) | ✓ | - | - |
| **Empleado** | Many2one(hr.employee) | ✓ | Usuario actual | - |
| **Aprobador** | Many2one(res.users) | - | - | - |
| **Estado** | Selection | ✓ | `draft` | ✓ |

#### Sección 3: Fechas y Cálculos

| Campo | Tipo | Requerido | Computed | Readonly |
|-------|------|-----------|----------|----------|
| **Fecha de solicitud** | Date | ✓ | - | ✓ |
| **Fecha inicio** | Date | ✓ | - | - |
| **Fecha fin** | Date | ✓ | - | - |
| **Días solicitados** | Integer | - | ✓ | ✓ |
| **Fecha de resolución** | Date | - | - | ✓ |

#### Sección 4: Justificación

| Campo | Tipo | Requerido | Widget |
|-------|------|-----------|--------|
| **Motivo** | Text | ✓ | `text` (área de texto) |

**Validaciones en Tiempo Real:**

1. **Fechas inconsistentes:**
   - Si `date_end < date_start`
   - Error: "La fecha de fin no puede ser anterior a la fecha de inicio."
   - Se muestra al intentar guardar

2. **Campos vacíos:**
   - Si falta `name`, `employee_id`, `date_start`, `date_end`, o `reason`
   - Error: "Campo obligatorio: [nombre del campo]"

**Captura de pantalla:** `assets/04-screenshot-app-form.jpg`

---

### 4.3 Pantalla: Formulario de Solicitud (Modo Edición - Empleado)

**Estado de la solicitud:** `draft`

**Campos editables:**
- Nombre
- Fecha inicio
- Fecha fin
- Motivo

**Campos readonly:**
- Empleado (auto-asignado)
- Fecha de solicitud
- Días solicitados (calculado)
- Estado
- Aprobador (puede asignarse manualmente si se conoce)

**Botones visibles:**
- "Enviar" (botón primario azul)

**Comportamiento:**

- Al cambiar `date_start` o `date_end`, el campo `days_count` se recalcula automáticamente
- Al hacer clic en "Guardar", se ejecutan validaciones
- Al hacer clic en "Enviar", se ejecuta `action_submit()` y estado cambia a `in_review`

---

### 4.4 Pantalla: Formulario de Solicitud (Modo Lectura - Manager)

**Estado de la solicitud:** `in_review`

**Campos editables:**
- Aprobador (si no está asignado)

**Campos readonly:**
- Todos los demás (nombre, fechas, motivo, etc.)

**Botones visibles:**
- "Aprobar" (botón verde)
- "Rechazar" (botón rojo)

**Comportamiento:**

- Al hacer clic en "Aprobar":
  - Se ejecuta `action_approve()`
  - Estado cambia a `approved`
  - `resolution_date` se establece a hoy
  - Botones desaparecen
  - Mensaje de confirmación

- Al hacer clic en "Rechazar":
  - Se ejecuta `action_reject()`
  - Estado cambia a `rejected`
  - `resolution_date` se establece a hoy
  - Botones desaparecen
  - Mensaje de confirmación

**Captura de pantalla:** `assets/06-screenshot-app-buttons.jpg`

---

### 4.5 Pantalla: Vista Kanban

**Vista:** `view_remote_request_kanban`

**Agrupación por defecto:** Estado (`state`)

**Columnas:**
1. Borrador (gris)
2. En revisión (azul)
3. Aprobada (verde)
4. Rechazada (rojo)

**Tarjeta de Solicitud:**

```
┌─────────────────────────────────────┐
│ Teletrabajo junio              [⋮] │ ← Título (name)
├─────────────────────────────────────┤
│ 👤 John Doe                         │ ← Empleado
│ 📅 2025-06-01 → 2025-06-05          │ ← Rango de fechas
│ 🕒 5 días                            │ ← Días solicitados
│ ✓ Jane Smith (aprobador)            │ ← Aprobador (si existe)
└─────────────────────────────────────┘
```

**Interacción:**
- Clic en tarjeta: abre formulario
- Drag & drop: NO habilitado en v1 (evita cambios de estado accidentales)

**Captura de pantalla:** `assets/12-screenshot-app-kanban-view.jpg`

---

### 4.6 Pantalla: Filtros de Búsqueda

**Vista:** `view_remote_work_request_search`

**Barra de búsqueda:**
- Búsqueda por texto en `name`
- Autocompletar en `employee_id` (busca por nombre de empleado)
- Autocompletar en `approver_id` (busca por nombre de usuario)

**Filtros predefinidos:**

| Filtro | Descripción | Dominio Aplicado |
|--------|-------------|-----------------|
| **Borrador** | Solicitudes no enviadas | `[('state', '=', 'draft')]` |
| **En revisión** | Pendientes de decisión | `[('state', '=', 'in_review')]` |
| **Aprobadas** | Solicitudes aprobadas | `[('state', '=', 'approved')]` |
| **Rechazadas** | Solicitudes rechazadas | `[('state', '=', 'rejected')]` |
| **Mis solicitudes** | Solicitudes del usuario actual | `[('user_id', '=', uid)]` |
| **Asignadas a mí** | Donde soy aprobador | `[('approver_id', '=', uid)]` |
| **Pendientes de revisar** | En revisión + asignadas a mí | `[('approver_id', '=', uid), ('state', '=', 'in_review')]` |

**Agrupación:**
- Por Estado
- Por Empleado
- Por Aprobador
- Por Fecha de solicitud (año/mes)

**Captura de pantalla:** `assets/07-screenshot-app-filters.jpg`

---

## 5. Reglas de Negocio Detalladas

### 5.1 RN-001: Validación de Fechas

**Descripción:** La fecha de fin no puede ser anterior a la fecha de inicio.

**Regla:**
```python
date_end >= date_start
```

**Implementación:**
- Constraint Python: `@api.constrains("date_start", "date_end")`
- Constraint SQL: `CHECK(date_end >= date_start)`

**Mensaje de Error:**
```
La fecha de fin no puede ser anterior a la fecha de inicio.
```

**Casos de prueba:**

| date_start | date_end | Resultado |
|------------|----------|-----------|
| 2025-01-10 | 2025-01-10 | ✓ Válido (mismo día) |
| 2025-01-10 | 2025-01-15 | ✓ Válido |
| 2025-01-15 | 2025-01-10 | ✗ Error (fin < inicio) |

---

### 5.2 RN-002: Cálculo de Días

**Descripción:** Los días solicitados se calculan de forma inclusiva (contando ambos extremos).

**Fórmula:**
```python
days_count = (date_end - date_start).days + 1
```

**Ejemplos:**

| date_start | date_end | Cálculo | days_count |
|------------|----------|---------|-----------|
| 2025-01-10 | 2025-01-10 | (10-10) + 1 | 1 día |
| 2025-01-10 | 2025-01-12 | (12-10) + 1 | 3 días |
| 2025-01-01 | 2025-01-05 | (5-1) + 1 | 5 días |
| 2025-01-01 | 2025-12-31 | (365-1) + 1 | 365 días |

**Limitaciones (v1):**
- No se excluyen fines de semana
- No se excluyen festivos
- Cálculo simple de días calendario

**Mejoras futuras (v2):**
- Integración con calendario laboral
- Exclusión de sábados, domingos y festivos
- Configuración por país/región

---

### 5.3 RN-003: Transiciones de Estado Permitidas

**Descripción:** Solo ciertas transiciones de estado están permitidas.

**Tabla de Transiciones:**

| Estado Actual | Acción | Estado Resultante | Permitido |
|---------------|--------|-------------------|-----------|
| `draft` | `action_submit()` | `in_review` | ✓ |
| `draft` | `action_approve()` | `approved` | ✗ |
| `draft` | `action_reject()` | `rejected` | ✗ |
| `in_review` | `action_submit()` | `in_review` | ✗ |
| `in_review` | `action_approve()` | `approved` | ✓ |
| `in_review` | `action_reject()` | `rejected` | ✓ |
| `approved` | (cualquiera) | (cualquiera) | ✗ |
| `rejected` | (cualquiera) | (cualquiera) | ✗ |

**Mensajes de Error:**

```python
# Si action_submit() desde estado != 'draft'
"Solo se pueden enviar solicitudes en estado Borrador."

# Si action_approve() desde estado != 'in_review'
"Solo se pueden aprobar solicitudes en estado En revisión."

# Si action_reject() desde estado != 'in_review'
"Solo se pueden rechazar solicitudes en estado En revisión."
```

---

### 5.4 RN-004: Asignación de Empleado

**Descripción:** Al crear una solicitud, el campo `employee_id` se pre-rellena con el empleado asociado al usuario actual.

**Implementación:**
```python
def _default_employee_id(self):
    return self.env["hr.employee"].search(
        [("user_id", "=", self.env.user.id)], limit=1
    )
```

**Comportamiento:**

| Escenario | Resultado |
|-----------|-----------|
| Usuario tiene empleado asociado | `employee_id` se rellena automáticamente |
| Usuario NO tiene empleado asociado | `employee_id` queda vacío → Error al guardar (campo requerido) |
| Usuario cambia manualmente `employee_id` | Se permite si tiene permisos (admin) |

---

### 5.5 RN-005: Establecimiento de Fecha de Resolución

**Descripción:** Al aprobar o rechazar una solicitud, el campo `resolution_date` se establece automáticamente a la fecha actual.

**Implementación:**
```python
# En action_approve()
record.write({
    "state": "approved",
    "resolution_date": fields.Date.today(),
})

# En action_reject()
record.write({
    "state": "rejected",
    "resolution_date": fields.Date.today(),
})
```

**Comportamiento:**

| Acción | resolution_date antes | resolution_date después |
|--------|----------------------|------------------------|
| `action_approve()` | `None` (vacío) | `2025-11-21` (hoy) |
| `action_reject()` | `None` (vacío) | `2025-11-21` (hoy) |
| `action_submit()` | `None` | `None` (sin cambios) |

---

### 5.6 RN-006: Visibilidad de Botones

**Descripción:** Los botones de acción se muestran u ocultan según el estado de la solicitud.

**Reglas de Visibilidad:**

| Botón | Condición de Visibilidad | Color | Posición |
|-------|-------------------------|-------|----------|
| **Enviar** | `state == 'draft'` | Azul (btn-primary) | Header |
| **Aprobar** | `state == 'in_review'` | Verde (btn-success) | Header |
| **Rechazar** | `state == 'in_review'` | Rojo (btn-danger) | Header |

**Implementación XML:**
```xml
<button name="action_submit" states="draft" class="btn-primary"/>
<button name="action_approve" states="in_review" class="btn-success"/>
<button name="action_reject" states="in_review" class="btn-danger"/>
```

**Comportamiento en cada estado:**

```
draft:      [Enviar]
in_review:  [Aprobar] [Rechazar]
approved:   (sin botones)
rejected:   (sin botones)
```

---

### 5.7 RN-007: Filtrado por Record Rules

**Descripción:** Los usuarios solo ven registros según su rol y asignaciones.

**Reglas:**

#### Empleado (`group_remote_work_request_employee`)

**Dominio:**
```python
[('employee_id.user_id', '=', user.id)]
```

**Interpretación:**
- Solo ve solicitudes donde el usuario del empleado es él mismo
- No puede ver solicitudes de otros empleados

**Ejemplo:**
```
Usuario: john@example.com (ID: 10)
Empleado: John Doe (user_id: 10)

Solicitudes visibles:
- ID 1: employee_id = John Doe ✓
- ID 2: employee_id = Jane Doe ✗ (otro empleado)
```

#### Manager (`group_remote_work_request_manager`)

**Dominio:**
```python
[('approver_id', '=', user.id)]
```

**Interpretación:**
- Solo ve solicitudes donde es el aprobador
- No puede ver solicitudes de otros managers

**Ejemplo:**
```
Usuario: manager@example.com (ID: 20)

Solicitudes visibles:
- ID 3: approver_id = 20 ✓
- ID 4: approver_id = 25 ✗ (otro manager)
```

#### Combinación de Grupos

Si un usuario tiene **ambos** grupos (employee + manager):

**Dominio efectivo (OR lógico):**
```python
[
  '|',  # OR
  ('employee_id.user_id', '=', user.id),
  ('approver_id', '=', user.id),
]
```

**Resultado:** Ve tanto sus propias solicitudes como las asignadas como aprobador.

---

## 6. Roles y Permisos

### 6.1 Matriz de Permisos

| Operación | Empleado | Manager | Admin |
|-----------|----------|---------|-------|
| **Crear solicitud propia** | ✓ | ✓ | ✓ |
| **Crear solicitud para otro** | ✗ | ✗ | ✓ |
| **Ver solicitudes propias** | ✓ | ✓ | ✓ |
| **Ver solicitudes de otros** | ✗ | Solo asignadas | ✓ |
| **Editar solicitud propia (draft)** | ✓ | ✓ | ✓ |
| **Editar solicitud propia (in_review)** | ✗ | ✗ | ✓ |
| **Editar solicitud de otro** | ✗ | ✗ | ✓ |
| **Enviar a revisión (propia)** | ✓ | ✓ | ✓ |
| **Aprobar solicitud asignada** | ✗ | ✓ | ✓ |
| **Rechazar solicitud asignada** | ✗ | ✓ | ✓ |
| **Aprobar solicitud no asignada** | ✗ | ✗ | ✓ |
| **Eliminar solicitud propia (draft)** | ✓ | ✓ | ✓ |
| **Eliminar solicitud (otros estados)** | ✗ | ✗ | ✓ |
| **Acceso al API** | N/A | N/A | N/A (público) |

### 6.2 Asignación de Grupos

**Proceso manual (v1):**

1. Administrador navega a **Configuración → Usuarios y Empresas → Usuarios**
2. Selecciona usuario
3. Edita campo "Permisos"
4. Marca checkboxes:
   - `Empleado - Solicitar Teletrabajo` → Grupo employee
   - `Gerente - Gestionar Solicitudes de Teletrabajo` → Grupo manager
5. Guarda cambios

**Proceso automático (futuro v2):**
- Auto-asignar grupo `employee` al crear usuario con empleado asociado
- Auto-asignar grupo `manager` al usuario con `is_manager=True` en departamento

**Captura de pantalla:** `assets/09-screenshot-app-groups-permissions.jpg`

---

## 7. Escenarios de Validación

### 7.1 Escenario: Solicitud Exitosa (Caso Feliz)

**Precondiciones:**
- Usuario: john@example.com (empleado)
- Manager: manager@example.com (asignado como aprobador)

**Pasos:**

1. John inicia sesión
2. Navega a "Trabajo Remoto → Solicitudes"
3. Clic en "Crear"
4. Rellena:
   - Nombre: "Teletrabajo diciembre"
   - Fecha inicio: 2025-12-01
   - Fecha fin: 2025-12-05
   - Motivo: "Visita familiar fuera de la ciudad"
5. Clic en "Guardar" → **Estado: draft, 5 días**
6. Clic en "Enviar" → **Estado: in_review**
7. Manager inicia sesión
8. Navega a "Trabajo Remoto → Solicitudes"
9. Aplica filtro "Pendientes de revisar"
10. Abre solicitud de John
11. Revisa información
12. Clic en "Aprobar" → **Estado: approved, resolution_date: hoy**
13. John recibe notificación (futuro)
14. API endpoint retorna la solicitud aprobada

**Resultado esperado:** ✓ Solicitud aprobada correctamente

---

### 7.2 Escenario: Error de Validación de Fechas

**Precondiciones:**
- Usuario autenticado como empleado

**Pasos:**

1. Usuario crea nueva solicitud
2. Rellena:
   - Nombre: "Test"
   - Fecha inicio: 2025-12-10
   - Fecha fin: 2025-12-05 ← **Error: fin < inicio**
   - Motivo: "Prueba"
3. Clic en "Guardar"

**Resultado esperado:**
```
❌ ValidationError
La fecha de fin no puede ser anterior a la fecha de inicio.
```

**Comportamiento UI:**
- Formulario no se cierra
- Mensaje de error en rojo en parte superior
- Usuario puede corregir fechas y reintentar

---

### 7.3 Escenario: Intento de Aprobar Solicitud sin Permiso

**Precondiciones:**
- Usuario: empleado sin grupo manager
- Solicitud en estado `in_review`

**Pasos:**

1. Empleado abre solicitud propia en estado `in_review`
2. Botones "Aprobar" y "Rechazar" NO son visibles (record rule)
3. Intento de ejecutar `action_approve()` directamente (vía script/API)

**Resultado esperado:**
```
❌ AccessError
No tiene permisos para realizar esta acción.
```

**Protección:**
- ACL: Grupo manager requerido para operación write en `in_review`
- Record rule: Solo aprobador puede modificar solicitudes asignadas

---

### 7.4 Escenario: Ver Solicitudes de Otros (Empleado)

**Precondiciones:**
- Usuario A: john@example.com (empleado John)
- Usuario B: jane@example.com (empleado Jane)
- Solicitud 1: employee_id = John
- Solicitud 2: employee_id = Jane

**Pasos:**

1. John inicia sesión
2. Navega a "Trabajo Remoto → Solicitudes"
3. Sistema aplica record rule: `[('employee_id.user_id', '=', john.id)]`

**Resultado esperado:**
- John ve solo Solicitud 1
- Solicitud 2 NO aparece en la lista
- Búsqueda manual por ID de Solicitud 2 retorna vacío

**Captura de pantalla:** `assets/08-screenshot-app-only-own-user-requests.jpg`

---

### 7.5 Escenario: Manager Aprueba Solo Asignadas

**Precondiciones:**
- Manager A: manager1@example.com
- Manager B: manager2@example.com
- Solicitud X: approver_id = Manager A
- Solicitud Y: approver_id = Manager B

**Pasos:**

1. Manager A inicia sesión
2. Navega a "Trabajo Remoto → Solicitudes"
3. Sistema aplica record rule: `[('approver_id', '=', manager1.id)]`

**Resultado esperado:**
- Manager A ve solo Solicitud X
- Solicitud Y NO aparece
- Intento de abrir Solicitud Y por URL directa: AccessError

**Captura de pantalla:** `assets/10-screenshot-app-only-to-approver-user-requests.jpg`

---

## 8. Mensajes de Error y Feedback

### 8.1 Mensajes de Validación

| Código | Mensaje | Contexto |
|--------|---------|----------|
| **VAL-001** | "La fecha de fin no puede ser anterior a la fecha de inicio." | Validación de fechas (`_check_dates`) |
| **VAL-002** | "Solo se pueden enviar solicitudes en estado Borrador." | `action_submit()` desde estado != draft |
| **VAL-003** | "Solo se pueden aprobar solicitudes en estado En revisión." | `action_approve()` desde estado != in_review |
| **VAL-004** | "Solo se pueden rechazar solicitudes en estado En revisión." | `action_reject()` desde estado != in_review |
| **VAL-005** | "El campo [nombre] es obligatorio." | Campos requeridos vacíos (name, employee_id, etc.) |

### 8.2 Mensajes de Éxito

| Código | Mensaje | Contexto |
|--------|---------|----------|
| **OK-001** | "Solicitud creada correctamente." | Después de guardar nueva solicitud |
| **OK-002** | "Solicitud enviada a revisión." | Después de `action_submit()` exitoso |
| **OK-003** | "Solicitud aprobada correctamente." | Después de `action_approve()` exitoso |
| **OK-004** | "Solicitud rechazada." | Después de `action_reject()` exitoso |
| **OK-005** | "Cambios guardados." | Después de editar solicitud existente |

### 8.3 Mensajes de Error de Acceso

| Código | Mensaje | Contexto |
|--------|---------|----------|
| **ACC-001** | "No tiene permisos para realizar esta acción." | ACL denegado |
| **ACC-002** | "Registro no encontrado o no tiene acceso." | Record rule filtra registro |
| **ACC-003** | "Debe pertenecer al grupo [nombre] para acceder." | Grupo requerido no asignado |

---

## 9. Casos Especiales

### 9.1 Solicitud con Fechas Futuras

**Escenario:**
- Usuario crea solicitud con `date_start` en el futuro (ej: +3 meses)

**Comportamiento:**
- ✓ Permitido (sin validación de rango de fechas en v1)
- Solicitud se crea normalmente
- Manager puede aprobar anticipadamente

**Justificación:**
- Planificación a largo plazo es válida
- No hay regla de negocio que limite antelación

**Mejora futura (v2):**
- Configuración de "ventana de solicitud" (ej: máximo 6 meses de antelación)

---

### 9.2 Solicitud con Fechas Pasadas

**Escenario:**
- Usuario crea solicitud con `date_start` en el pasado

**Comportamiento:**
- ✓ Permitido (en v1)
- Útil para regularizar teletrabajo ya realizado

**Justificación:**
- Casos de solicitudes retroactivas (ej: emergencia no planificada)

**Mejora futura (v2):**
- Configuración de "solicitudes retroactivas permitidas" (sí/no)
- Alertar si fechas son más de 7 días en el pasado

---

### 9.3 Empleado sin Usuario Asociado

**Escenario:**
- Empleado en HR sin campo `user_id` configurado

**Comportamiento:**
- Al crear solicitud, `_default_employee_id()` retorna vacío
- Usuario debe seleccionar empleado manualmente (si tiene permisos)
- Si usuario es empleado estándar: error al guardar (no puede seleccionar otro empleado)

**Solución:**
- Administrador debe asociar usuario al empleado en HR
- Configuración → Empleados → Editar → Campo "Usuario relacionado"

---

### 9.4 Usuario con Múltiples Empleados

**Escenario:**
- Usuario tiene múltiples registros de empleado (ej: diferentes empresas en entorno multi-company)

**Comportamiento:**
- `_default_employee_id()` retorna el primero encontrado (`limit=1`)
- Usuario puede cambiar manualmente si tiene permisos

**Mejora futura:**
- Diálogo de selección si se detectan múltiples empleados

---

### 9.5 Aprobador No Asignado

**Escenario:**
- Solicitud enviada a revisión (`in_review`) sin `approver_id` configurado

**Comportamiento:**
- Solicitud queda en `in_review` pero sin asignación
- Ningún manager la ve en sus filtros ("Asignadas a mí" retorna vacío)
- Solo admin puede verla y asignar aprobador

**Solución:**
- Configurar `approver_id` antes de enviar (campo visible en formulario)
- O asignar automáticamente según jerarquía (futuro v2)

**Mejora futura:**
- Validación: obligar `approver_id` antes de `action_submit()`
- Auto-asignación según jerarquía de HR (manager del departamento)

---

### 9.6 Cambio de Aprobador Durante Revisión

**Escenario:**
- Solicitud en `in_review` con `approver_id = Manager A`
- Manager A quiere reasignar a Manager B

**Comportamiento:**
- Manager A puede editar `approver_id` (campo editable en estado `in_review`)
- Al cambiar a Manager B:
  - Solicitud desaparece de la lista de Manager A
  - Aparece en la lista de Manager B
  - Manager B puede ahora aprobar/rechazar

**Justificación:**
- Flexibilidad para delegar
- Caso de uso: Manager de vacaciones reasigna a suplente

---

## 10. Glosario de Términos

### 10.1 Términos de Negocio

| Término | Definición |
|---------|-----------|
| **Teletrabajo** | Modalidad de trabajo donde el empleado realiza sus funciones fuera de la oficina (ej: desde casa) |
| **Solicitud** | Petición formal del empleado para trabajar en modalidad remota durante un período específico |
| **Aprobador** | Usuario (típicamente manager) con autoridad para aprobar o rechazar solicitudes |
| **Días solicitados** | Número de días calendario que el empleado solicita para teletrabajo (cálculo inclusivo) |
| **Revisión** | Proceso de evaluación de una solicitud por parte del aprobador |

### 10.2 Estados de Solicitud

| Estado | Código | Descripción |
|--------|--------|-------------|
| **Borrador** | `draft` | Solicitud creada pero no enviada; el empleado puede editar |
| **En revisión** | `in_review` | Solicitud enviada y pendiente de decisión del manager |
| **Aprobada** | `approved` | Solicitud autorizada por el manager; empleado puede teletrabajar |
| **Rechazada** | `rejected` | Solicitud denegada por el manager; empleado debe trabajar en oficina |

### 10.3 Campos Técnicos

| Campo | Nombre Técnico | Tipo | Descripción |
|-------|---------------|------|-------------|
| **ID** | `id` | Integer | Identificador único del registro |
| **Nombre** | `name` | Char | Título descriptivo de la solicitud |
| **Empleado** | `employee_id` | Many2one | Relación con `hr.employee` |
| **Aprobador** | `approver_id` | Many2one | Relación con `res.users` |
| **Usuario** | `user_id` | Many2one | Usuario del empleado (campo relacionado) |
| **Fecha de solicitud** | `request_date` | Date | Fecha de creación del registro |
| **Fecha inicio** | `date_start` | Date | Primer día de teletrabajo |
| **Fecha fin** | `date_end` | Date | Último día de teletrabajo |
| **Motivo** | `reason` | Text | Justificación del empleado |
| **Estado** | `state` | Selection | Estado del flujo (draft/in_review/approved/rejected) |
| **Días** | `days_count` | Integer | Número de días (computado) |
| **Fecha de resolución** | `resolution_date` | Date | Fecha de aprobación o rechazo |

### 10.4 Permisos y Seguridad

| Término | Definición |
|---------|-----------|
| **ACL** | Access Control List - Permisos CRUD a nivel de modelo |
| **Record Rule** | Filtro automático de registros según usuario (Row-Level Security) |
| **Grupo** | Conjunto de permisos asignados a usuarios (role) |
| **Domain** | Expresión de filtrado en formato Odoo (ej: `[('state', '=', 'draft')]`) |
| **sudo()** | Método que bypasea restricciones de seguridad (superuser do) |

### 10.5 Abreviaturas

| Abreviatura | Significado |
|-------------|-------------|
| **RN** | Regla de Negocio |
| **UC** | Caso de Uso (Use Case) |
| **HR** | Human Resources (Recursos Humanos) |
| **API** | Application Programming Interface |
| **JSON** | JavaScript Object Notation |
| **CRUD** | Create, Read, Update, Delete |
| **ORM** | Object-Relational Mapping |
| **FK** | Foreign Key (clave foránea) |
| **PK** | Primary Key (clave primaria) |

---

## 11. Referencias

### 11.1 Documentos Relacionados

- **01-requisitos-de-negocio.md** - Requisitos originales del proyecto
- **02-arquitectura-tecnica.md** - Diseño técnico y componentes del sistema
- **04-api-specification.md** - Especificación detallada del endpoint REST
- **tests-recomendados.md** - Plan de testing y casos de prueba

### 11.2 Enlaces Externos

- **Odoo Documentation:** https://www.odoo.com/documentation/19.0/
- **Odoo ORM API:** https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html
- **Odoo Security:** https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html

---

**Fin del documento**

---

**Historial de cambios:**

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2025-11-21 | Pablo Laya | Versión inicial |
