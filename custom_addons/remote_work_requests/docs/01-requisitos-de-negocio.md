# 01 — Requisitos de negocio: “Remote Work Requests” (Odoo 19)

## 1. Contexto y problema
La empresa trabaja en modalidad híbrida (oficina + remoto). Las **solicitudes de teletrabajo** se gestionan por email y hojas de cálculo, lo que provoca:
- Falta de trazabilidad y duplicidades.
- Aprobaciones lentas o informales.
- Dificultad para saber quién teletrabaja y cuándo.
- Imposible obtener métricas fiables (volumen, tiempos, reparto por equipos).

## 2. Objetivo
Disponibilizar en **Odoo 19** un módulo interno (**addon**) que permita:
- Registrar, revisar y aprobar/rechazar **solicitudes de teletrabajo**.
- Ofrecer **vistas amigables** (lista y formulario) para negocio.
- Publicar un **endpoint JSON** con solicitudes **aprobadas**.
- Ejecutarse en **Docker** (Odoo + PostgreSQL) con **custom_addons** montados.

**Éxito**: el usuario de negocio cubre el proceso sin Excel/email y el responsable puede aprobar con uno o dos clics. Existe visibilidad y datos exportables.

## 3. Alcance
### 3.1 Incluye (v1)
- Modelo “Solicitud de teletrabajo” con campos clave y cálculo de días.
- Flujo de estados: `Borrador → En revisión → Aprobada / Rechazada`.
- Vistas: **lista** y **formulario** (filtros por estado, responsable y “Mis solicitudes”).
- Endpoint JSON: `/api/remote-work/approved` (GET) con solicitudes aprobadas.
- Seguridad básica: dos perfiles (Usuario y Responsable).
- Despliegue **Docker** (Odoo + PostgreSQL) con `custom_addons/`.

### 3.2 Excluye (posponer)
- Notificaciones por email o chatter.
- Integración con calendario corporativo.
- Políticas avanzadas (cupos por equipo, validación de festivos).
- Cuadrantes/turnos, solapamientos complejos, informes avanzados.

## 4. Actores
- **Empleado solicitante**: crea y consulta sus solicitudes; puede enviar a revisión.
- **Responsable aprobador**: revisa, aprueba o rechaza; ve solicitudes de su ámbito.
- **Administrador** (opcional): puede ver todo, gestionar permisos y configuración.

## 5. Historias de usuario (resumen)
- **Como Empleado**, quiero crear una solicitud con fechas y motivo para pedir teletrabajo.
- **Como Empleado**, quiero ver mis solicitudes y su estado para saber si han sido aprobadas.
- **Como Responsable**, quiero una vista rápida de solicitudes “En revisión” para decidir.
- **Como Responsable**, quiero aprobar o rechazar con un clic y dejar constancia.
- **Como Administrador**, quiero un listado exportable de aprobadas para reportar.

## 6. Reglas de negocio
- No se permite **fecha fin < fecha inicio**.
- El **nº de días** se calcula automáticamente (incluye ambos extremos).
- Transiciones válidas:
  - `Borrador → En revisión` (acción del solicitante).
  - `En revisión → Aprobada` (acción del responsable).
  - `En revisión → Rechazada` (acción del responsable).
- Al **aprobar/rechazar**, se registran **responsable** y **fecha de resolución**.
- No se vuelve a `Borrador` desde `Aprobada/Rechazada` (v1).

## 7. Requisitos funcionales
- Crear/editar **Solicitudes** con: empleado, fechas inicio/fin, motivo, estado, nº días (calculado), responsable y fecha de resolución.
- Botones de acción en formulario: **Enviar a revisión**, **Aprobar**, **Rechazar**.
- **Vistas**:
  - Lista con columnas: empleado, fechas, estado, nº días, responsable.
  - Formulario con grupos de campos (solicitud / aprobación).
  - Búsqueda/filtros: por estado, responsable, “Mis solicitudes”.
- **API**:
  - `GET /api/remote-work/approved` → JSON con: empleado, rango fechas, nº días, responsable.
  - Parámetros opcionales: `employee_id` (filtrado).
  - Autenticación **opcional** en v1 (decisión técnica documentada).
- **Seguridad**:
  - **Usuario**: ve/crea **sus** solicitudes; puede enviarlas a revisión.
  - **Responsable**: ve solicitudes de su ámbito; aprueba/rechaza.

## 8. Requisitos no funcionales
- **Despliegue**: Docker (Odoo + PostgreSQL) sobre WSL.
- **Persistencia**: volúmenes para Postgres y filestore de Odoo.
- **Configuración**: `odoo.conf` (con `addons_path` y conexión DB) y `.env` (secretos).
- **Calidad**: estructura de addon estándar Odoo, sin modificar core.
- **Trazabilidad**: cambios de estado quedan reflejados (usuario, fecha).

## 9. Datos y modelo (v1)
**Entidad:** Solicitud de teletrabajo
**Campos mínimos:**
- Empleado (relación con empleado/usuario).
- Fecha de solicitud (auto).
- Fecha inicio, fecha fin.
- Motivo (texto).
- Estado (`draft`, `in_review`, `approved`, `rejected`).
- Días solicitados (calculado).
- Responsable (usuario).
- Fecha de resolución (fecha/hora).

**Restricciones:**
- `fecha_fin >= fecha_inicio`.
- Acciones restringidas según estado actual.

## 10. Flujo de estados (UML informal)
draft --(Enviar a revisión)--> in_review
in_review --(Aprobar)-------> approved
in_review --(Rechazar)------> rejected

## 11. Interfaz (vistas)
- **Lista**: vista de solicitudes con columnas clave y filtros.
- **Formulario**: secciones de Solicitud y Aprobación con botones de acción.
- (Opcional) **Kanban** por estado (si hay tiempo).

## 12. API (v1)
- **Ruta**: `/api/remote-work/approved` (GET).
- **Salida**: array JSON de objetos `{ empleado, fecha_inicio, fecha_fin, dias, responsable }`.
- **Filtros opcionales**: `employee_id`.
- **Autenticación**: pública en v1 u **autenticada** (según decisión técnica); documentar elección.

## 13. Seguridad y permisos
- **Grupos**:
  - `remote_work_user`: crear/leer **sus** solicitudes; enviar a revisión.
  - `remote_work_manager`: leer solicitudes del equipo/área; aprobar/rechazar.
- **Access/Record Rules**:
  - Usuarios ven **solo sus** registros (salvo managers).
  - Managers con permisos de aprobación.

## 14. Métricas básicas / Informes (v1)
- Nº de solicitudes **aprobadas/rechazadas** por período.
- Días de teletrabajo **aprobados** por empleado.
- (Exportable por listado; informes avanzados fuera de v1).

## 15. Criterios de aceptación
- Se puede **crear**, **enviar**, **aprobar** y **rechazar** una solicitud completa sin errores.
- Se impide guardar **fechas inconsistentes**.
- El **nº de días** se calcula correctamente al editar fechas.
- La **API** devuelve el JSON esperado y filtra por `employee_id` si se indica.
- **Permisos**: un usuario no ve ni cambia solicitudes ajenas; un manager sí puede aprobar.

## 16. Suposiciones y dependencias
- Odoo 19 + Postgres 16 en Docker.
- Estructura de empleados/usuarios disponible (Odoo base).
- No se gestionan conflictos complejos de calendario en v1.
- No hay aprobación multinivel en v1.

## 17. Entregables
- Código del addon en `custom_addons/remote_work_requests/`.
- Orquestación Docker + configuración (`docker/compose.yaml`, `.env.example`, `odoo.conf.example`).
- Documentación en `docs/` (requisitos, arquitectura, diseño funcional, API, pruebas).

## 18. Plan de validación (manual)
1. Arranque del entorno (Docker) y creación de BD de desarrollo.
2. Instalación del addon desde Apps.
3. Caso feliz: crear → enviar a revisión → aprobar.
4. Caso alternativo: crear → enviar a revisión → rechazar.
5. Validación de restricciones (fechas) y cálculo de días.
6. Verificación de permisos (usuario vs responsable).
7. Consumo del endpoint `/api/remote_work/approved_requests` y verificación de formato.

## 19. Futuras mejoras (backlog)
- Notificaciones por email y chatter.
- Integración con calendario y festivos.
- Dashboard con métricas y gráficos.
- Aprobación multinivel y reglas por departamento.
- Gestión de solapamientos y límites mensuales/anuales.
