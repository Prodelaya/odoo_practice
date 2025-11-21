# 05 — Manual de Usuario: Remote Work Requests

**Proyecto:** Sistema de Gestión de Solicitudes de Teletrabajo
**Versión del sistema:** 1.0
**Versión del documento:** 1.0
**Fecha:** 21 de noviembre de 2025
**Autor:** Pablo Rodríguez

---

## Índice

1. [Introducción](#1-introducción)
2. [Acceso al Sistema](#2-acceso-al-sistema)
3. [Guía para Empleados](#3-guía-para-empleados)
4. [Guía para Managers](#4-guía-para-managers)
5. [Preguntas Frecuentes](#5-preguntas-frecuentes)
6. [Solución de Problemas](#6-solución-de-problemas)
7. [Glosario](#7-glosario)

---

## 1. Introducción

### 1.1 ¿Qué es Remote Work Requests?

Remote Work Requests es un sistema integrado en Odoo que permite gestionar las solicitudes de teletrabajo de forma centralizada, ordenada y transparente.

**Beneficios:**
- ✓ Proceso digital: sin emails ni Excel
- ✓ Trazabilidad completa de solicitudes
- ✓ Aprobaciones rápidas (un clic)
- ✓ Visibilidad del estado en tiempo real
- ✓ Historial de solicitudes aprobadas/rechazadas

### 1.2 Roles de Usuario

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **Empleado** | Persona que solicita días de teletrabajo | Crear y ver sus propias solicitudes |
| **Manager** | Responsable que aprueba/rechaza solicitudes | Revisar y decidir sobre solicitudes asignadas |
| **Administrador** | Personal de IT o RRHH con acceso completo | Ver y modificar todas las solicitudes |

---

## 2. Acceso al Sistema

### 2.1 Inicio de Sesión

1. Abre tu navegador web (Chrome, Firefox, Edge o Safari)
2. Navega a la URL de Odoo:
   ```
   http://localhost:8069 (desarrollo)
   https://odoo.empresa.com (producción)
   ```
3. Ingresa tus credenciales:
   - **Email:** tu correo corporativo
   - **Contraseña:** tu contraseña de Odoo

![Pantalla de login](../assets/01-screenshot-apps-gallery.jpg)

### 2.2 Acceder al Módulo

Una vez dentro de Odoo:

1. En el menú superior, busca el icono de "Aplicaciones"
2. En la galería de aplicaciones, busca **"Remote Work Requests"** o **"Trabajo Remoto"**
3. Haz clic en el icono para abrir el módulo

![Galería de aplicaciones](../assets/02-screenshot-app-info.jpg)

**Tip:** Puedes marcar la aplicación como favorita para acceso rápido.

---

## 3. Guía para Empleados

### 3.1 Crear una Nueva Solicitud

#### Paso 1: Navegar al Módulo

1. Abre el módulo **"Trabajo Remoto"** desde el menú principal
2. Haz clic en **"Solicitudes"** en el submenú

![Vista de navegación](../assets/03-screenshot-app-view.jpg)

#### Paso 2: Iniciar Creación

1. En la vista de lista, haz clic en el botón **"Crear"** (esquina superior izquierda)
2. Se abrirá un formulario en blanco

![Vista de lista](../assets/05-screenshot-app-list.jpg)

#### Paso 3: Rellenar el Formulario

**Campos obligatorios (marcados con *):**

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Nombre*** | Título descriptivo de tu solicitud | "Teletrabajo junio 2025" |
| **Empleado*** | Tu nombre (pre-rellenado automáticamente) | John Doe |
| **Fecha inicio*** | Primer día de teletrabajo | 2025-06-01 |
| **Fecha fin*** | Último día de teletrabajo | 2025-06-05 |
| **Motivo*** | Justificación de la solicitud | "Mudanza de domicilio" |

**Campos opcionales:**

| Campo | Descripción |
|-------|-------------|
| **Aprobador** | Manager que revisará (si lo sabes) |

![Formulario de solicitud](../assets/04-screenshot-app-form.jpg)

**Importante:**
- La **Fecha fin** no puede ser anterior a la **Fecha inicio**
- El campo **Días** se calcula automáticamente (incluye ambos extremos)
- El **Estado** inicial es "Borrador"

#### Paso 4: Guardar

1. Haz clic en **"Guardar"** (esquina superior izquierda)
2. Si hay errores, aparecerá un mensaje en rojo. Corrígelos y guarda de nuevo.
3. Si todo está correcto, verás un mensaje de confirmación

**Resultado:**
- Solicitud creada en estado **"Borrador"**
- Aún puedes editar todos los campos
- No es visible para el manager hasta que la envíes

---

### 3.2 Enviar Solicitud a Revisión

Una vez creada la solicitud y verificados los datos:

#### Paso 1: Abrir Solicitud en Borrador

1. En la lista de solicitudes, haz clic en la que quieres enviar
2. Verifica que el estado sea "Borrador"

#### Paso 2: Enviar

1. Haz clic en el botón **"Enviar"** (azul, en la parte superior del formulario)
2. El sistema cambiará el estado a **"En revisión"**
3. Recibirás un mensaje de confirmación

![Botones de acción](../assets/06-screenshot-app-buttons.jpg)

**¿Qué ocurre al enviar?**
- ✓ Estado cambia a "En revisión"
- ✓ La solicitud aparece en la bandeja del manager
- ✓ Ya NO puedes editar la solicitud
- ✓ Solo queda esperar la decisión del manager

**Nota:** En v1 no hay notificaciones por email. El manager debe revisar manualmente su bandeja.

---

### 3.3 Consultar el Estado de tus Solicitudes

#### Usar Filtros

1. En la vista de lista, haz clic en **"Filtros"** (barra superior)
2. Selecciona **"Mis solicitudes"** para ver solo las tuyas
3. Puedes agregar filtros adicionales:
   - **Borrador:** Solicitudes que aún no has enviado
   - **En revisión:** Esperando decisión del manager
   - **Aprobadas:** Solicitudes autorizadas
   - **Rechazadas:** Solicitudes denegadas

![Filtros de búsqueda](../assets/07-screenshot-app-filters.jpg)

#### Interpretar Colores

La lista usa colores para identificar rápidamente el estado:

| Color | Estado | Significado |
|-------|--------|-------------|
| **Gris** | Borrador | Aún no enviada |
| **Azul** | En revisión | Pendiente de decisión |
| **Verde** | Aprobada | Autorizada por el manager |
| **Rojo** | Rechazada | Denegada por el manager |

![Colores de estado](../assets/11-screenshot-app-state-colors.jpg)

---

### 3.4 Ver Solo tus Solicitudes

**Por seguridad, solo puedes ver tus propias solicitudes.**

El sistema aplica un filtro automático:
```
Mostrar solo solicitudes donde: Empleado = Yo
```

No verás solicitudes de otros compañeros.

![Vista de empleado](../assets/08-screenshot-app-only-own-user-requests.jpg)

---

### 3.5 Editar una Solicitud en Borrador

Si necesitas modificar una solicitud **antes de enviarla**:

1. Abre la solicitud en estado "Borrador"
2. Modifica los campos necesarios (fechas, motivo, etc.)
3. Haz clic en **"Guardar"**

**Importante:**
- Solo puedes editar solicitudes en estado **"Borrador"**
- Una vez enviadas (estado "En revisión"), ya no se pueden editar
- Si necesitas cambiar algo después de enviar, debes crear una nueva solicitud

---

### 3.6 ¿Qué Pasa Después de Enviar?

#### Escenario 1: Solicitud Aprobada ✓

1. El manager revisa tu solicitud
2. El manager hace clic en **"Aprobar"**
3. El estado cambia a **"Aprobada"** (verde)
4. Se registra la fecha de aprobación
5. Puedes teletrabajar en las fechas solicitadas

**En el futuro (v2):** Recibirás un email de notificación.

#### Escenario 2: Solicitud Rechazada ✗

1. El manager revisa tu solicitud
2. El manager hace clic en **"Rechazar"**
3. El estado cambia a **"Rechazada"** (rojo)
4. Se registra la fecha de rechazo
5. Debes trabajar desde la oficina

**En el futuro (v2):** El manager podrá dejar un comentario con el motivo del rechazo.

---

## 4. Guía para Managers

### 4.1 Ver Solicitudes Asignadas

Como manager, solo ves solicitudes donde eres el **aprobador asignado**.

#### Acceso Rápido

1. Navega a **Trabajo Remoto → Solicitudes**
2. El sistema aplica automáticamente el filtro:
   ```
   Mostrar solo solicitudes donde: Aprobador = Yo
   ```

![Vista de manager](../assets/10-screenshot-app-only-to-approver-user-requests.jpg)

#### Filtro "Pendientes de Revisar"

Para ver solo las que requieren tu decisión:

1. Haz clic en **"Filtros"**
2. Selecciona **"Pendientes de revisar"**
3. Verás solo solicitudes en estado **"En revisión"** asignadas a ti

**Tip:** Usa este filtro como tu "bandeja de entrada" de tareas pendientes.

---

### 4.2 Revisar una Solicitud

#### Paso 1: Abrir Solicitud

1. En la lista, haz clic en la solicitud que quieres revisar
2. Se abrirá el formulario con toda la información

#### Paso 2: Verificar Datos

Revisa los siguientes campos:

| Campo | Verificar |
|-------|-----------|
| **Empleado** | ¿Quién solicita? |
| **Fechas** | ¿Cuándo quiere teletrabajar? |
| **Días** | ¿Cuántos días son? |
| **Motivo** | ¿La justificación es válida? |
| **Estado** | Debe ser "En revisión" |

**Consideraciones de negocio:**
- ¿Hay otros empleados del equipo fuera esos días?
- ¿Hay eventos importantes en la oficina?
- ¿El motivo es razonable?
- ¿El empleado tiene días de teletrabajo disponibles? (si aplica)

---

### 4.3 Aprobar una Solicitud

Si decides **autorizar** la solicitud:

#### Paso 1: Verificar Estado

- Asegúrate de que el estado sea **"En revisión"**
- Si está en otro estado, no podrás aprobar

#### Paso 2: Aprobar

1. Haz clic en el botón **"Aprobar"** (verde, parte superior)
2. El sistema cambiará automáticamente:
   - Estado → **"Aprobada"**
   - Fecha de resolución → Hoy
3. Verás un mensaje de confirmación

![Botones de manager](../assets/06-screenshot-app-buttons.jpg)

**Resultado:**
- ✓ Solicitud marcada como aprobada
- ✓ Empleado puede teletrabajar en esas fechas
- ✓ Registro queda en el historial
- ✓ Solicitud aparece en el API de aprobadas

**Nota:** La decisión es **irreversible**. Si te equivocas, contacta al administrador.

---

### 4.4 Rechazar una Solicitud

Si decides **denegar** la solicitud:

#### Paso 1: Verificar Estado

- Asegúrate de que el estado sea **"En revisión"**

#### Paso 2: Rechazar

1. Haz clic en el botón **"Rechazar"** (rojo, parte superior)
2. El sistema cambiará automáticamente:
   - Estado → **"Rechazada"**
   - Fecha de resolución → Hoy
3. Verás un mensaje de confirmación

**Resultado:**
- ✗ Solicitud marcada como rechazada
- ✗ Empleado NO puede teletrabajar (debe ir a la oficina)
- ✓ Registro queda en el historial

**Limitación v1:** No se puede dejar un comentario con el motivo del rechazo. Considera comunicarte con el empleado por email o en persona.

**Mejora futura (v2):** Campo de texto para justificar el rechazo.

---

### 4.5 Reasignar una Solicitud

Si necesitas **delegar** la decisión a otro manager:

#### Escenario de Uso

- Estarás de vacaciones
- La solicitud corresponde a otro departamento
- Quieres escalar a un superior

#### Pasos

1. Abre la solicitud en estado "En revisión"
2. Haz clic en el campo **"Aprobador"**
3. Selecciona el nuevo manager de la lista
4. Haz clic en **"Guardar"**

**Efecto:**
- La solicitud desaparece de tu lista
- Aparece en la lista del nuevo aprobador
- El nuevo manager puede aprobar o rechazar

---

### 4.6 Usar la Vista Kanban

Para una visión más visual del pipeline de solicitudes:

#### Activar Vista Kanban

1. En la vista de solicitudes, haz clic en el icono **"Kanban"** (cuadrados) en la esquina superior derecha
2. Verás columnas por estado:
   - Borrador
   - En revisión
   - Aprobada
   - Rechazada

![Vista Kanban](../assets/12-screenshot-app-kanban-view.jpg)

#### Ventajas

- Visión rápida de la distribución de solicitudes
- Identificar cuellos de botella (muchas en "En revisión")
- Ver nombres y días en formato de tarjeta
- Puede arrastrar tarjetas entre columnas para pasar las solicitudes a los distintos estados.

---

## 5. Preguntas Frecuentes

### 5.1 Preguntas de Empleados

#### P: ¿Puedo crear una solicitud para fechas pasadas?

**R:** Sí. El sistema permite fechas en el pasado. Esto es útil para regularizar teletrabajo realizado en casos de emergencia.

**Recomendación:** Solicita con antelación siempre que sea posible.

---

#### P: ¿Puedo solicitar un solo día de teletrabajo?

**R:** Sí. Configura **Fecha inicio** = **Fecha fin**. El campo "Días" mostrará 1.

**Ejemplo:**
- Fecha inicio: 2025-06-15
- Fecha fin: 2025-06-15
- Días: 1

---

#### P: ¿Cómo se cuentan los días? ¿Incluye fines de semana?

**R:** El sistema cuenta **días calendario** de forma inclusiva (incluye ambos extremos).

**Ejemplo:**
- Lunes 10 a viernes 14 = 5 días
- Lunes 10 a domingo 16 = 7 días (incluye sábado y domingo)

**Limitación v1:** No se excluyen fines de semana ni festivos automáticamente.

---

#### P: ¿Puedo editar una solicitud después de enviarla?

**R:** No. Una vez en estado "En revisión", la solicitud está bloqueada.

**Alternativa:**
1. Pide al manager que rechace la solicitud
2. Crea una nueva solicitud con los datos correctos

---

#### P: ¿Recibiré un email cuando se apruebe mi solicitud?

**R:** No en v1. Debes revisar manualmente el estado en Odoo.

**Mejora futura (v2):** Notificaciones por email automáticas.

---

#### P: ¿Puedo ver las solicitudes de mis compañeros?

**R:** No. Por seguridad, solo puedes ver tus propias solicitudes.

**Excepción:** Los administradores y managers pueden ver solicitudes de su ámbito.

---

### 5.2 Preguntas de Managers

#### P: ¿Cómo sé cuándo hay nuevas solicitudes pendientes?

**R:** Debes revisar manualmente el filtro "Pendientes de revisar" en Odoo.

**Mejora futura (v2):** Notificaciones por email cuando llegue una nueva solicitud.

---

#### P: ¿Puedo deshacer una aprobación?

**R:** No directamente. Los estados aprobados/rechazados son finales.

**Solución:** Contacta al administrador del sistema para que haga el cambio manualmente.

---

#### P: ¿Puedo aprobar una solicitud de alguien que no está en mi equipo?

**R:** Solo si eres el **aprobador asignado** en esa solicitud.

**Cómo funciona:**
- Si `Aprobador = Tú` → Puedes aprobar/rechazar
- Si `Aprobador = Otro` → No verás esa solicitud

---

#### P: ¿Puedo ver un historial de todas las solicitudes que he aprobado?

**R:** Sí. Usa el filtro **"Asignadas a mí"** + **"Aprobadas"**.

**Pasos:**
1. Filtros → Asignadas a mí
2. Filtros → Aprobadas
3. Verás todas las que has aprobado históricamente

---

#### P: ¿Cuántas solicitudes puedo aprobar al mes por empleado?

**R:** No hay límite configurado en v1.

**Mejora futura (v2):** Configuración de cupos por empleado/departamento.

---

## 6. Solución de Problemas

### 6.1 Problemas Comunes de Empleados

#### Problema: "Campo obligatorio: Empleado"

**Causa:** Tu usuario no está asociado a un empleado en el módulo HR.

**Solución:**
1. Contacta al administrador de RRHH o IT
2. Deben crear un registro de empleado y vincularlo a tu usuario

---

#### Problema: "La fecha de fin no puede ser anterior a la fecha de inicio"

**Causa:** Configuraste **Fecha fin** < **Fecha inicio**.

**Solución:**
- Verifica las fechas
- Asegúrate de que Fecha fin ≥ Fecha inicio

**Ejemplo correcto:**
- Fecha inicio: 2025-06-01
- Fecha fin: 2025-06-05 ✓

**Ejemplo incorrecto:**
- Fecha inicio: 2025-06-10
- Fecha fin: 2025-06-05 ✗

---

#### Problema: No veo el botón "Enviar"

**Causa:** La solicitud no está en estado "Borrador".

**Verificación:**
- Revisa el campo "Estado" en el formulario
- Si dice "En revisión", "Aprobada" o "Rechazada", el botón no aparecerá

**Solución:**
- Si ya enviaste la solicitud, no puedes volver a enviarla
- Si necesitas hacer cambios, crea una nueva solicitud

---

#### Problema: No aparece mi solicitud en la lista

**Causa posible 1:** Hay un filtro activo.

**Solución:**
1. Revisa la barra de filtros (arriba de la lista)
2. Haz clic en la "X" de cada filtro para quitarlos
3. Tu solicitud debería aparecer

**Causa posible 2:** La creaste en otro usuario/sesión.

**Solución:**
- Verifica que estás logueado con el usuario correcto
- Las solicitudes solo son visibles para quien las creó

---

### 6.2 Problemas Comunes de Managers

#### Problema: No veo ninguna solicitud

**Causa posible 1:** No hay solicitudes asignadas a ti.

**Verificación:**
- Revisa si el campo "Aprobador" de las solicitudes tiene tu nombre
- Solo ves solicitudes donde `Aprobador = Tú`

**Solución:**
- Los empleados deben asignar un aprobador al crear la solicitud
- Pide a los empleados que te asignen como aprobador

---

**Causa posible 2:** No tienes el grupo "Manager" asignado.

**Verificación:**
1. Contacta al administrador
2. Deben verificar en: Configuración → Usuarios → Tu usuario → Permisos
3. Debe estar marcado **"Gerente - Gestionar Solicitudes de Teletrabajo"**

---

#### Problema: No veo los botones "Aprobar" y "Rechazar"

**Causa:** La solicitud no está en estado "En revisión".

**Verificación:**
- Revisa el campo "Estado"
- Los botones solo aparecen si Estado = "En revisión"

**Posibles estados:**
- "Borrador" → Solo botón "Enviar" (visible para el empleado)
- "En revisión" → Botones "Aprobar" y "Rechazar" (visible para el manager)
- "Aprobada" / "Rechazada" → Sin botones (estado final)

---

#### Problema: "Solo se pueden aprobar solicitudes en estado En revisión"

**Causa:** Intentaste aprobar una solicitud en estado diferente a "En revisión".

**Solución:**
- Verifica el estado de la solicitud
- Solo puedes aprobar solicitudes que están esperando tu decisión

---

### 6.3 Errores Técnicos

#### Error: "Acceso denegado"

**Causa:** No tienes permisos para realizar la acción.

**Escenarios:**
- Empleado intentando aprobar su propia solicitud
- Empleado intentando ver solicitudes de otros
- Manager intentando modificar solicitud de otro manager

**Solución:**
- Verifica que tienes el rol correcto (Empleado o Manager)
- Contacta al administrador si crees que deberías tener acceso

---

#### Error: "Registro no encontrado"

**Causa:** Intentaste acceder a una solicitud que no existe o no tienes permisos.

**Solución:**
- Verifica que la URL es correcta
- Usa la navegación del módulo en lugar de URLs directas
- Contacta al administrador si el problema persiste

---

#### Error: "Tiempo de espera agotado"

**Causa:** El servidor tardó demasiado en responder.

**Posibles causas:**
- Servidor sobrecargado
- Conexión de red lenta
- Problema en la base de datos

**Solución:**
1. Refresca la página (F5)
2. Espera unos minutos y reintenta
3. Si persiste, contacta al área de IT

---

## 7. Glosario

### Términos del Sistema

| Término | Definición |
|---------|-----------|
| **Solicitud** | Petición formal para trabajar en modo remoto durante un período |
| **Teletrabajo** | Modalidad de trabajo fuera de la oficina (ej: desde casa) |
| **Empleado** | Persona que solicita días de teletrabajo |
| **Manager** | Responsable que aprueba o rechaza solicitudes |
| **Aprobador** | Usuario asignado para tomar la decisión sobre una solicitud |
| **Estado** | Etapa del flujo en la que se encuentra una solicitud |

---

### Estados de Solicitud

| Estado | Descripción | Color |
|--------|-------------|-------|
| **Borrador** | Solicitud creada pero no enviada; el empleado puede editar | Gris |
| **En revisión** | Solicitud enviada y esperando decisión del manager | Azul |
| **Aprobada** | Solicitud autorizada; empleado puede teletrabajar | Verde |
| **Rechazada** | Solicitud denegada; empleado debe trabajar en oficina | Rojo |

---

### Campos del Formulario

| Campo | Descripción |
|-------|-------------|
| **Nombre** | Título descriptivo de la solicitud (ej: "Teletrabajo junio") |
| **Empleado** | Persona que solicita (auto-rellenado) |
| **Aprobador** | Manager responsable de aprobar/rechazar |
| **Fecha de solicitud** | Fecha en que se creó el registro |
| **Fecha inicio** | Primer día de teletrabajo solicitado |
| **Fecha fin** | Último día de teletrabajo solicitado |
| **Días** | Número de días calculado automáticamente (inclusivo) |
| **Motivo** | Justificación del empleado (texto libre) |
| **Estado** | Borrador, En revisión, Aprobada o Rechazada |
| **Fecha de resolución** | Fecha en que se aprobó o rechazó (auto-rellenado) |

---

## 8. Contacto y Soporte

### 8.1 Ayuda Técnica

**Para problemas técnicos:**
- Email: soporte@empresa.com
- Teléfono: +34 XXX XXX XXX
- Horario: Lunes a viernes, 9:00 - 18:00

**Antes de contactar, ten a mano:**
- Tu nombre de usuario
- Captura de pantalla del error
- Descripción detallada del problema
- Pasos para reproducir el error

---

### 8.2 Sugerencias y Feedback

**Para proponer mejoras:**
- Email: feedback-odoo@empresa.com
- Portal de ideas: https://ideas.empresa.com

**Ejemplos de sugerencias:**
- Nuevas funcionalidades
- Mejoras en la interfaz
- Notificaciones por email
- Reportes personalizados

---

## 9. Buenas Prácticas

### 9.1 Para Empleados

✓ **Solicita con antelación**
- Envía tu solicitud al menos 3-5 días antes
- Da tiempo al manager para revisar y planificar

✓ **Sé claro en el motivo**
- Explica brevemente por qué necesitas teletrabajar
- Un motivo claro facilita la aprobación

✓ **Verifica tus fechas**
- Revisa que no haya errores en las fechas
- Asegúrate de que no haya eventos importantes en la oficina

✓ **Mantén comunicación**
- Si surge un imprevisto, contacta a tu manager por email
- No dependas solo del sistema

---

### 9.2 Para Managers

✓ **Revisa regularmente**
- Consulta "Pendientes de revisar" al menos 1 vez al día
- No dejes solicitudes sin atender por más de 2 días laborables

✓ **Sé consistente**
- Aplica los mismos criterios para todos los empleados
- Documenta políticas de teletrabajo del equipo

✓ **Comunica decisiones**
- Si rechazas, explica al empleado el motivo (por email)
- Sugiere alternativas si es posible

✓ **Planifica la cobertura**
- Asegúrate de que haya presencia mínima en oficina
- Evita aprobar todo el equipo el mismo día

---

## 10. Próximas Funcionalidades (Roadmap)

### v1.1 (Q1 2026)

- ✉ Notificaciones por email (empleado y manager)
- 📊 Dashboard con métricas (solicitudes por mes, días aprobados)
- 🔍 Búsqueda avanzada por rango de fechas

### v2.0 (Q2 2026)

- 💬 Comentarios en solicitudes (feedback del manager)
- 📅 Integración con calendario de Odoo
- 🚫 Exclusión de festivos y fines de semana
- 👥 Aprobación multinivel (manager + RRHH)
- 📱 App móvil (Odoo Mobile)

---

**Fin del manual**

---

**Historial de cambios:**

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2025-11-21 | Pablo Rodríguez | Versión inicial |

---

**¿Tienes preguntas o sugerencias sobre este manual?**

Envíanos un email a: documentacion@empresa.com
