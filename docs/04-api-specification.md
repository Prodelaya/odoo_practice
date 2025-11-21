# 04 — Especificación del API: Remote Work Requests

**Proyecto:** Sistema de Gestión de Solicitudes de Teletrabajo
**Versión del API:** 1.0
**Versión del documento:** 1.0
**Fecha:** 21 de noviembre de 2025
**Autor:** Pablo Rodríguez

---

## Índice

1. [Introducción](#1-introducción)
2. [Información General del API](#2-información-general-del-api)
3. [Autenticación y Seguridad](#3-autenticación-y-seguridad)
4. [Endpoints](#4-endpoints)
5. [Modelos de Datos](#5-modelos-de-datos)
6. [Códigos de Respuesta](#6-códigos-de-respuesta)
7. [Ejemplos de Uso](#7-ejemplos-de-uso)
8. [Limitaciones y Restricciones](#8-limitaciones-y-restricciones)
9. [Versionado](#9-versionado)
10. [Changelog](#10-changelog)

---

## 1. Introducción

### 1.1 Propósito

Esta especificación describe el API REST del sistema Remote Work Requests, que permite consultar solicitudes de teletrabajo aprobadas desde aplicaciones externas.

### 1.2 Audiencia

- Desarrolladores de aplicaciones que consumen el API
- Equipos de integración
- Administradores de sistemas
- Testers de API

### 1.3 Alcance

**Versión 1.0 incluye:**
- Endpoint GET para consultar solicitudes aprobadas
- Respuestas en formato JSON
- Acceso público sin autenticación

**Futuras versiones incluirán:**
- Autenticación con tokens JWT
- Endpoints POST/PUT/DELETE (CRUD completo)
- Filtrado avanzado por parámetros
- Paginación de resultados
- Rate limiting

---

## 2. Información General del API

### 2.1 URL Base

```
http://<servidor>:8069
```

**Ejemplos:**
- Desarrollo: `http://localhost:8069`
- Producción: `https://odoo.empresa.com`

### 2.2 Protocolo

- **HTTP/HTTPS:** Soportado (HTTPS recomendado en producción)
- **Método:** GET (solo lectura)

### 2.3 Formato de Datos

- **Request:** N/A (sin body)
- **Response:** `application/json; charset=utf-8`

### 2.4 Encoding

- **Character Set:** UTF-8
- **Date Format:** ISO 8601 (`YYYY-MM-DD`)

### 2.5 Límites y Cuotas

| Métrica | Valor (v1.0) | Notas |
|---------|-------------|-------|
| **Rate Limit** | Sin límite | v2.0 implementará rate limiting |
| **Paginación** | Sin paginación | Se retornan todos los registros |
| **Tamaño máximo de respuesta** | ~10 MB | Limitado por configuración de Odoo |
| **Timeout** | 30 segundos | Timeout del servidor web |

---

## 3. Autenticación y Seguridad

### 3.1 Autenticación (v1.0)

**Tipo:** Pública (sin autenticación)

**Configuración:**
```python
@http.route(..., auth="public", csrf=False, ...)
```

**Implicaciones:**
- No se requiere token, API key, ni login
- Cualquier cliente con acceso de red puede consultar
- Solo expone datos ya aprobados (considerados no sensibles)

### 3.2 HTTPS

**Recomendaciones:**
- Usar HTTPS en producción
- Configurar certificado SSL/TLS válido
- Forzar redirección HTTP → HTTPS en servidor web (Nginx/Apache)

**Ejemplo de configuración Nginx:**
```nginx
server {
    listen 80;
    server_name odoo.empresa.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name odoo.empresa.com;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8069;
    }
}
```

### 3.3 CORS (Cross-Origin Resource Sharing)

**Estado actual:** No configurado en v1.0

**Configuración futura (v2.0):**
```python
headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}
```

---

## 4. Endpoints

### 4.1 GET /remote_work/approved_requests

**Descripción:** Obtiene todas las solicitudes de teletrabajo en estado "aprobada".

#### Información General

| Atributo | Valor |
|----------|-------|
| **URL** | `/remote_work/approved_requests` |
| **Método** | `GET` |
| **Autenticación** | No requerida (público) |
| **Content-Type Response** | `application/json` |

#### Parámetros de Query

**v1.0:** Sin parámetros soportados

**v2.0 (planeado):**

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `employee_id` | Integer | No | - | Filtrar por ID de empleado |
| `approver_id` | Integer | No | - | Filtrar por ID de aprobador |
| `date_from` | Date (ISO) | No | - | Fecha mínima de `date_start` |
| `date_to` | Date (ISO) | No | - | Fecha máxima de `date_end` |
| `offset` | Integer | No | 0 | Número de registros a saltar (paginación) |
| `limit` | Integer | No | 100 | Número máximo de registros a retornar |

#### Headers de Request

**Opcionales:**

```http
Accept: application/json
User-Agent: MyApp/1.0
```

#### Headers de Response

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 1234
Server: Werkzeug/2.x Python/3.12
Date: Thu, 21 Nov 2025 10:00:00 GMT
```

#### Cuerpo de Respuesta

**Tipo:** Array de objetos JSON

**Esquema:**

```json
[
  {
    "id": Integer,
    "employee": String,
    "approver": String,
    "request_date": String (ISO Date),
    "date_start": String (ISO Date),
    "date_end": String (ISO Date),
    "resolution_date": String (ISO Date) | null,
    "days_count": Integer,
    "reason": String,
    "state": String
  }
]
```

**Ejemplo:**

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
  {
    "id": 6,
    "employee": "Empleado Instalaciones",
    "approver": "Manager Instalaciones",
    "request_date": "2024-09-20",
    "date_start": "2024-09-25",
    "date_end": "2024-09-30",
    "resolution_date": "2024-09-21",
    "days_count": 6,
    "reason": "Trabajo remoto por mudanza",
    "state": "approved"
  }
]
```

#### Códigos de Estado HTTP

| Código | Significado | Descripción |
|--------|------------|-------------|
| **200** | OK | Solicitud exitosa, retorna array (puede ser vacío) |
| **404** | Not Found | Ruta no encontrada (verificar URL) |
| **500** | Internal Server Error | Error en servidor Odoo (verificar logs) |
| **503** | Service Unavailable | Servidor Odoo no disponible |

#### Casos de Uso

##### Caso 1: Solicitudes Aprobadas Disponibles

**Request:**
```http
GET /remote_work/approved_requests HTTP/1.1
Host: localhost:8069
Accept: application/json
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "id": 5,
    "employee": "John Doe",
    "approver": "Jane Manager",
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

##### Caso 2: Sin Solicitudes Aprobadas

**Request:**
```http
GET /remote_work/approved_requests HTTP/1.1
Host: localhost:8069
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

[]
```

**Nota:** Se retorna array vacío, no error 404.

##### Caso 3: Campo Nulo (Aprobador Vacío)

**Escenario:** Solicitud aprobada sin `approver_id` configurado

**Response:**
```json
[
  {
    "id": 10,
    "employee": "John Doe",
    "approver": "",
    "request_date": "2025-01-15",
    "date_start": "2025-01-20",
    "date_end": "2025-01-25",
    "resolution_date": null,
    "days_count": 6,
    "reason": "Remote work",
    "state": "approved"
  }
]
```

**Manejo de nulos:**
- Campos `Many2one` vacíos → `""` (string vacío)
- Campos `Date` vacíos → `null`
- Campos `Text` vacíos → `""` (string vacío)

---

## 5. Modelos de Datos

### 5.1 Objeto: ApprovedRequest

#### Descripción

Representa una solicitud de teletrabajo aprobada.

#### Propiedades

| Campo | Tipo | Nullable | Descripción | Ejemplo |
|-------|------|----------|-------------|---------|
| `id` | Integer | No | Identificador único del registro | `5` |
| `employee` | String | No | Nombre completo del empleado solicitante | `"John Doe"` |
| `approver` | String | Sí | Nombre completo del manager aprobador | `"Jane Smith"` |
| `request_date` | String (Date) | Sí | Fecha de creación de la solicitud (ISO 8601) | `"2025-01-15"` |
| `date_start` | String (Date) | Sí | Fecha de inicio del teletrabajo (ISO 8601) | `"2025-01-20"` |
| `date_end` | String (Date) | Sí | Fecha de fin del teletrabajo (ISO 8601) | `"2025-01-25"` |
| `resolution_date` | String (Date) | Sí | Fecha de aprobación (ISO 8601) | `"2025-01-18"` |
| `days_count` | Integer | No | Número de días solicitados (inclusivo) | `6` |
| `reason` | String | Sí | Justificación del empleado | `"Work from home due to relocation"` |
| `state` | String | No | Estado de la solicitud (siempre "approved") | `"approved"` |

#### Esquema JSON (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ApprovedRequest",
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "description": "Unique identifier",
      "example": 5
    },
    "employee": {
      "type": "string",
      "description": "Full name of the requesting employee",
      "example": "John Doe"
    },
    "approver": {
      "type": "string",
      "description": "Full name of the approving manager (empty string if not assigned)",
      "example": "Jane Smith"
    },
    "request_date": {
      "type": ["string", "null"],
      "format": "date",
      "description": "Date when the request was created (ISO 8601)",
      "example": "2025-01-15"
    },
    "date_start": {
      "type": ["string", "null"],
      "format": "date",
      "description": "Start date of remote work period",
      "example": "2025-01-20"
    },
    "date_end": {
      "type": ["string", "null"],
      "format": "date",
      "description": "End date of remote work period",
      "example": "2025-01-25"
    },
    "resolution_date": {
      "type": ["string", "null"],
      "format": "date",
      "description": "Date when the request was approved",
      "example": "2025-01-18"
    },
    "days_count": {
      "type": "integer",
      "description": "Number of days requested (inclusive count)",
      "example": 6
    },
    "reason": {
      "type": "string",
      "description": "Employee's justification for remote work",
      "example": "Work from home due to relocation"
    },
    "state": {
      "type": "string",
      "enum": ["approved"],
      "description": "State of the request (always 'approved' in this endpoint)",
      "example": "approved"
    }
  },
  "required": ["id", "employee", "days_count", "state"]
}
```

---

## 6. Códigos de Respuesta

### 6.1 Respuestas Exitosas (2xx)

#### 200 OK

**Descripción:** Solicitud procesada correctamente.

**Casos:**
- Array con solicitudes aprobadas
- Array vacío (sin solicitudes aprobadas)

**Headers:**
```http
Content-Type: application/json
Content-Length: <size>
```

**Body:**
```json
[
  { "id": 1, "employee": "...", ... }
]
```

---

### 6.2 Errores del Cliente (4xx)

#### 404 Not Found

**Descripción:** Ruta no encontrada.

**Causa:** URL incorrecta.

**Ejemplo:**
```http
GET /remote_work/approved HTTP/1.1
```

**Response:**
```http
HTTP/1.1 404 Not Found
Content-Type: text/html

<!DOCTYPE html>
<html>
<head><title>404 Not Found</title></head>
<body>
  <h1>404 Not Found</h1>
  <p>The requested URL was not found on this server.</p>
</body>
</html>
```

**Solución:** Verificar URL correcta: `/remote_work/approved_requests`

---

### 6.3 Errores del Servidor (5xx)

#### 500 Internal Server Error

**Descripción:** Error interno en el servidor Odoo.

**Causas posibles:**
- Error en código Python del controlador
- Error de base de datos
- Configuración incorrecta de Odoo

**Ejemplo de escenario:**
- Error en serialización de fechas
- Fallo en consulta a PostgreSQL

**Response:**
```http
HTTP/1.1 500 Internal Server Error
Content-Type: text/html

<!DOCTYPE html>
<html>
<head><title>500 Internal Server Error</title></head>
<body>
  <h1>Internal Server Error</h1>
  <p>The server encountered an internal error and was unable to complete your request.</p>
</body>
</html>
```

**Diagnóstico:**
```bash
# Ver logs de Odoo
docker compose logs -f odoo | grep ERROR
```

**Solución:**
- Revisar logs del servidor
- Verificar configuración de base de datos
- Reiniciar servicio Odoo si es necesario

---

#### 503 Service Unavailable

**Descripción:** Servidor Odoo no disponible.

**Causas posibles:**
- Contenedor Docker detenido
- Odoo en proceso de reinicio
- Sobrecarga del servidor

**Response:**
```http
HTTP/1.1 503 Service Unavailable
Content-Type: text/html
Retry-After: 120

<!DOCTYPE html>
<html>
<head><title>503 Service Unavailable</title></head>
<body>
  <h1>Service Temporarily Unavailable</h1>
</body>
</html>
```

**Solución:**
```bash
# Verificar estado del contenedor
docker compose ps

# Reiniciar servicios
docker compose restart odoo
```

---

## 7. Ejemplos de Uso

### 7.1 cURL

#### Ejemplo 1: GET Básico

```bash
curl -X GET "http://localhost:8069/remote_work/approved_requests"
```

**Output:**
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
  }
]
```

#### Ejemplo 2: Con Headers

```bash
curl -X GET "http://localhost:8069/remote_work/approved_requests" \
  -H "Accept: application/json" \
  -H "User-Agent: MyApp/1.0" \
  -v
```

**Output (verbose):**
```
* Connected to localhost (127.0.0.1) port 8069
> GET /remote_work/approved_requests HTTP/1.1
> Host: localhost:8069
> Accept: application/json
> User-Agent: MyApp/1.0
>
< HTTP/1.1 200 OK
< Content-Type: application/json; charset=utf-8
< Content-Length: 234
< Date: Thu, 21 Nov 2025 10:00:00 GMT
<
[...]
```

#### Ejemplo 3: Guardar Respuesta en Archivo

```bash
curl -X GET "http://localhost:8069/remote_work/approved_requests" \
  -o approved_requests.json
```

---

### 7.2 Python (requests)

#### Instalación

```bash
pip install requests
```

#### Ejemplo Básico

```python
import requests

# GET a la API
response = requests.get("http://localhost:8069/remote_work/approved_requests")

# Verificar código de estado
if response.status_code == 200:
    data = response.json()
    print(f"Total de solicitudes aprobadas: {len(data)}")

    for request in data:
        print(f"ID: {request['id']}")
        print(f"  Empleado: {request['employee']}")
        print(f"  Período: {request['date_start']} a {request['date_end']}")
        print(f"  Días: {request['days_count']}")
        print(f"  Motivo: {request['reason']}")
        print()
else:
    print(f"Error: {response.status_code}")
```

#### Ejemplo con Manejo de Errores

```python
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

API_URL = "http://localhost:8069/remote_work/approved_requests"

try:
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()  # Lanza excepción si status != 2xx

    data = response.json()

    # Procesar datos
    for request in data:
        print(f"{request['employee']}: {request['days_count']} días")

except Timeout:
    print("Error: La solicitud tardó demasiado")
except ConnectionError:
    print("Error: No se pudo conectar al servidor")
except requests.HTTPError as e:
    print(f"Error HTTP: {e}")
except requests.RequestException as e:
    print(f"Error de solicitud: {e}")
except ValueError:
    print("Error: Respuesta no es JSON válido")
```

#### Ejemplo: Filtrar en Cliente (v1.0)

```python
import requests
from datetime import date

response = requests.get("http://localhost:8069/remote_work/approved_requests")
data = response.json()

# Filtrar por empleado (lado cliente)
employee_name = "Empleado Instalaciones"
filtered = [r for r in data if r['employee'] == employee_name]

print(f"Solicitudes de {employee_name}: {len(filtered)}")

# Filtrar por rango de fechas (lado cliente)
date_from = date(2024, 10, 1)
date_to = date(2024, 10, 31)

filtered_by_date = [
    r for r in data
    if date.fromisoformat(r['date_start']) >= date_from
    and date.fromisoformat(r['date_end']) <= date_to
]

print(f"Solicitudes en octubre 2024: {len(filtered_by_date)}")
```

---

### 7.3 JavaScript (fetch)

#### Ejemplo Básico (Browser)

```javascript
fetch("http://localhost:8069/remote_work/approved_requests")
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log(`Total de solicitudes: ${data.length}`);

    data.forEach(request => {
      console.log(`${request.employee}: ${request.days_count} días`);
    });
  })
  .catch(error => {
    console.error("Error:", error);
  });
```

#### Ejemplo con async/await

```javascript
async function fetchApprovedRequests() {
  try {
    const response = await fetch(
      "http://localhost:8069/remote_work/approved_requests"
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    // Mostrar en tabla HTML
    displayRequests(data);

  } catch (error) {
    console.error("Error fetching data:", error);
    showErrorMessage(error.message);
  }
}

function displayRequests(requests) {
  const tableBody = document.getElementById("requests-table-body");
  tableBody.innerHTML = "";

  requests.forEach(req => {
    const row = `
      <tr>
        <td>${req.employee}</td>
        <td>${req.date_start}</td>
        <td>${req.date_end}</td>
        <td>${req.days_count}</td>
        <td>${req.reason}</td>
      </tr>
    `;
    tableBody.innerHTML += row;
  });
}

// Ejecutar al cargar página
fetchApprovedRequests();
```

#### Ejemplo Node.js (con node-fetch)

```javascript
// npm install node-fetch
import fetch from "node-fetch";

const API_URL = "http://localhost:8069/remote_work/approved_requests";

async function getApprovedRequests() {
  try {
    const response = await fetch(API_URL);
    const data = await response.json();

    console.log(`Total: ${data.length} solicitudes aprobadas`);

    // Calcular total de días aprobados
    const totalDays = data.reduce((sum, req) => sum + req.days_count, 0);
    console.log(`Total de días aprobados: ${totalDays}`);

  } catch (error) {
    console.error("Error:", error.message);
  }
}

getApprovedRequests();
```

---

### 7.4 Postman

#### Configuración de Request

**Método:** GET

**URL:** `http://localhost:8069/remote_work/approved_requests`

**Headers:**
```
Accept: application/json
```

**Tests (JavaScript):**

```javascript
pm.test("Status code es 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response es un array", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.be.an('array');
});

pm.test("Cada solicitud tiene campos requeridos", function () {
    var jsonData = pm.response.json();

    jsonData.forEach(function(request) {
        pm.expect(request).to.have.property('id');
        pm.expect(request).to.have.property('employee');
        pm.expect(request).to.have.property('state', 'approved');
        pm.expect(request).to.have.property('days_count');
    });
});

pm.test("Fechas están en formato ISO", function () {
    var jsonData = pm.response.json();

    if (jsonData.length > 0) {
        var firstRequest = jsonData[0];

        if (firstRequest.date_start) {
            pm.expect(firstRequest.date_start).to.match(/^\d{4}-\d{2}-\d{2}$/);
        }
    }
});
```

---

## 8. Limitaciones y Restricciones

### 8.1 Limitaciones Actuales (v1.0)

| Limitación | Descripción | Impacto |
|------------|-------------|---------|
| **Sin filtrado** | No se pueden filtrar resultados por parámetros | Cliente debe filtrar localmente |
| **Sin paginación** | Se retornan todos los registros | Respuesta puede ser grande con muchos datos |
| **Sin ordenamiento** | Orden es por ID ascendente (default de Odoo) | No se puede ordenar por fecha o empleado |
| **Sin autenticación** | Acceso público | Cualquiera con acceso de red puede consultar |
| **Solo lectura** | No se pueden crear/modificar solicitudes vía API | Requiere usar interfaz web de Odoo |
| **Sin versionado de URL** | No hay `/v1/` en la ruta | Cambios futuros pueden romper compatibilidad |

### 8.2 Consideraciones de Performance

#### Escenario: 10,000 Solicitudes Aprobadas

**Estimaciones:**

| Métrica | Valor |
|---------|-------|
| Tamaño de respuesta JSON | ~5 MB |
| Tiempo de serialización | ~2 segundos |
| Tiempo de transferencia | ~1 segundo (red local) |
| Memoria usada en worker | ~100 MB |

**Recomendaciones:**

1. **Implementar paginación (v2.0):**
   ```
   GET /remote_work/approved_requests?limit=100&offset=0
   ```

2. **Implementar filtrado por fecha:**
   ```
   GET /remote_work/approved_requests?date_from=2025-01-01&date_to=2025-01-31
   ```

3. **Cache en cliente:**
   - Almacenar respuesta localmente
   - Refrescar cada X minutos
   - Usar ETags para validación de cache

4. **Compresión HTTP:**
   ```http
   Accept-Encoding: gzip, deflate
   ```

### 8.3 Restricciones de Datos

#### Datos No Expuestos

El endpoint **NO** expone:
- Solicitudes en estado `draft`
- Solicitudes en estado `in_review`
- Solicitudes en estado `rejected`
- Información de empleados (más allá del nombre)
- Información de departamentos
- Datos personales (email, teléfono, dirección)

#### Datos Expuestos

El endpoint **SÍ** expone:
- Solo solicitudes con `state = 'approved'`
- Nombres de empleados y aprobadores
- Fechas de solicitud y aprobación
- Motivo de la solicitud (texto libre)
- Número de días aprobados

---

## 9. Versionado

### 9.1 Esquema de Versionado

**Formato:** Semantic Versioning (MAJOR.MINOR.PATCH)

- **MAJOR:** Cambios incompatibles con versiones anteriores
- **MINOR:** Nueva funcionalidad compatible con versiones anteriores
- **PATCH:** Correcciones de bugs compatibles

### 9.2 Versiones Planificadas

#### v1.0 (Actual)

**Fecha de Release:** 21 de noviembre de 2025

**Características:**
- Endpoint GET `/remote_work/approved_requests`
- Respuestas JSON
- Sin autenticación
- Sin filtrado ni paginación

---

#### v1.1 (Q1 2026)

**Cambios planificados:**

1. **Paginación:**
   ```
   GET /remote_work/approved_requests?offset=0&limit=100
   ```

2. **Filtrado por fecha:**
   ```
   GET /remote_work/approved_requests?date_from=2025-01-01&date_to=2025-01-31
   ```

3. **Header con metadata:**
   ```http
   X-Total-Count: 500
   X-Page-Offset: 0
   X-Page-Limit: 100
   ```

**Compatibilidad:** 100% compatible con v1.0

---

#### v2.0 (Q2 2026)

**Cambios planificados (BREAKING CHANGES):**

1. **Autenticación requerida:**
   ```http
   Authorization: Bearer <token>
   ```

2. **Nuevo formato de URL:**
   ```
   GET /api/v2/remote_work/requests?status=approved
   ```

3. **Respuesta con metadata:**
   ```json
   {
     "meta": {
       "total": 500,
       "offset": 0,
       "limit": 100
     },
     "data": [...]
   }
   ```

4. **Endpoints CRUD completos:**
   - `POST /api/v2/remote_work/requests` (crear)
   - `PUT /api/v2/remote_work/requests/{id}` (editar)
   - `DELETE /api/v2/remote_work/requests/{id}` (eliminar)

**Compatibilidad:** NO compatible con v1.x (deprecación anunciada con 6 meses de anticipación)

---

## 10. Changelog

### v1.0 (2025-11-21)

**Inicial Release**

**Añadido:**
- Endpoint `GET /remote_work/approved_requests`
- Respuesta JSON con 10 campos por solicitud
- Acceso público sin autenticación
- Documentación completa del API

**Notas:**
- Primera versión funcional
- Base para futuras iteraciones

---

## Anexos

### A. Especificación OpenAPI (Swagger)

```yaml
openapi: 3.0.3
info:
  title: Remote Work Requests API
  description: API para consultar solicitudes de teletrabajo aprobadas
  version: 1.0.0
  contact:
    name: Pablo Rodríguez
    email: admin@empresa.com

servers:
  - url: http://localhost:8069
    description: Servidor de desarrollo
  - url: https://odoo.empresa.com
    description: Servidor de producción

paths:
  /remote_work/approved_requests:
    get:
      summary: Obtener solicitudes aprobadas
      description: Retorna todas las solicitudes de teletrabajo en estado 'approved'
      operationId: getApprovedRequests
      tags:
        - Remote Work Requests
      responses:
        '200':
          description: Solicitud exitosa
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/ApprovedRequest'
              examples:
                conDatos:
                  summary: Con solicitudes aprobadas
                  value:
                    - id: 5
                      employee: "John Doe"
                      approver: "Jane Smith"
                      request_date: "2025-01-15"
                      date_start: "2025-01-20"
                      date_end: "2025-01-25"
                      resolution_date: "2025-01-18"
                      days_count: 6
                      reason: "Work from home"
                      state: "approved"
                sinDatos:
                  summary: Sin solicitudes aprobadas
                  value: []
        '404':
          description: Ruta no encontrada
        '500':
          description: Error interno del servidor

components:
  schemas:
    ApprovedRequest:
      type: object
      required:
        - id
        - employee
        - days_count
        - state
      properties:
        id:
          type: integer
          description: Identificador único
          example: 5
        employee:
          type: string
          description: Nombre del empleado
          example: "John Doe"
        approver:
          type: string
          description: Nombre del aprobador
          example: "Jane Smith"
          nullable: true
        request_date:
          type: string
          format: date
          description: Fecha de creación
          example: "2025-01-15"
          nullable: true
        date_start:
          type: string
          format: date
          description: Fecha de inicio
          example: "2025-01-20"
          nullable: true
        date_end:
          type: string
          format: date
          description: Fecha de fin
          example: "2025-01-25"
          nullable: true
        resolution_date:
          type: string
          format: date
          description: Fecha de aprobación
          example: "2025-01-18"
          nullable: true
        days_count:
          type: integer
          description: Número de días (inclusivo)
          example: 6
          minimum: 0
        reason:
          type: string
          description: Justificación del empleado
          example: "Work from home due to relocation"
        state:
          type: string
          enum:
            - approved
          description: Estado de la solicitud
          example: "approved"
```

### B. Ejemplo de Colección Postman

```json
{
  "info": {
    "name": "Remote Work Requests API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Approved Requests",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Accept",
            "value": "application/json"
          }
        ],
        "url": {
          "raw": "http://localhost:8069/remote_work/approved_requests",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8069",
          "path": ["remote_work", "approved_requests"]
        }
      }
    }
  ]
}
```

---

**Fin del documento**

---

**Historial de cambios:**

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2025-11-21 | Pablo Rodríguez | Versión inicial del API v1.0 |
