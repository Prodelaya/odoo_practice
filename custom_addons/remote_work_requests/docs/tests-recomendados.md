# Plan de Tests Recomendados - Remote Work Requests

## Resumen

Este documento presenta una estrategia de testing completa para el addon `remote_work_requests` de Odoo 19, cubriendo tests unitarios, de integración y de seguridad.

---

## 1. Tests del Modelo (`remote.work.request`)

### 1.1. Tests de Creación y Campos Básicos

**Test: `test_create_remote_request_basic`**
- **Objetivo**: Verificar que se puede crear una solicitud con campos mínimos
- **Datos**: employee_id, name, date_start, date_end, reason
- **Aserciones**:
  - Registro creado exitosamente
  - Estado inicial = 'draft'
  - request_date se establece automáticamente
  - user_id se establece desde employee_id.user_id

**Test: `test_employee_id_default`**
- **Objetivo**: Verificar que employee_id se establece por defecto según el usuario actual
- **Setup**: Crear usuario con empleado asociado, hacer sudo a ese usuario
- **Aserciones**: Al crear sin employee_id explícito, se usa el del usuario actual

**Test: `test_user_id_related_field`**
- **Objetivo**: Verificar que user_id se sincroniza con employee_id.user_id
- **Acciones**: Crear solicitud, verificar user_id, cambiar employee_id
- **Aserciones**: user_id cambia automáticamente con employee_id

---

### 1.2. Tests de Cálculo de Días (`_compute_days_count`)

**Test: `test_days_count_single_day`**
- **Datos**: date_start = date_end = '2025-01-15'
- **Aserción**: days_count = 1

**Test: `test_days_count_multiple_days`**
- **Datos**: date_start = '2025-01-15', date_end = '2025-01-20'
- **Aserción**: days_count = 6 (inclusivo)

**Test: `test_days_count_empty_dates`**
- **Datos**: Sin date_start o date_end
- **Aserción**: days_count = 0

**Test: `test_days_count_recompute_on_date_change`**
- **Objetivo**: Verificar recálculo al cambiar fechas
- **Acciones**: Crear con fechas, verificar días, cambiar date_end, verificar nuevo cálculo
- **Aserción**: days_count se actualiza automáticamente

---

### 1.3. Tests de Validación de Fechas (`_check_dates`)

**Test: `test_check_dates_valid`**
- **Datos**: date_start = '2025-01-15', date_end = '2025-01-20'
- **Aserción**: No se levanta ValidationError

**Test: `test_check_dates_equal`**
- **Datos**: date_start = date_end = '2025-01-15'
- **Aserción**: No se levanta ValidationError

**Test: `test_check_dates_invalid`**
- **Datos**: date_start = '2025-01-20', date_end = '2025-01-15'
- **Aserción**: Se levanta ValidationError con mensaje apropiado

---

### 1.4. Tests de Transiciones de Estado

**Test: `test_action_submit_from_draft`**
- **Estado inicial**: 'draft'
- **Acción**: action_submit()
- **Aserción**: state = 'in_review'

**Test: `test_action_submit_from_non_draft_fails`**
- **Estados a probar**: 'in_review', 'approved', 'rejected'
- **Acción**: action_submit()
- **Aserción**: Se levanta ValidationError

**Test: `test_action_approve_from_in_review`**
- **Estado inicial**: 'in_review'
- **Acción**: action_approve()
- **Aserciones**:
  - state = 'approved'
  - resolution_date se establece (fecha actual)
  - approver_id se mantiene si estaba establecido

**Test: `test_action_approve_from_non_in_review_fails`**
- **Estados a probar**: 'draft', 'approved', 'rejected'
- **Acción**: action_approve()
- **Aserción**: Se levanta ValidationError

**Test: `test_action_reject_from_in_review`**
- **Estado inicial**: 'in_review'
- **Acción**: action_reject()
- **Aserciones**:
  - state = 'rejected'
  - resolution_date se establece (fecha actual)

**Test: `test_action_reject_from_non_in_review_fails`**
- **Estados a probar**: 'draft', 'approved', 'rejected'
- **Acción**: action_reject()
- **Aserción**: Se levanta ValidationError

**Test: `test_resolution_date_set_on_approve`**
- **Objetivo**: Verificar que resolution_date se establece al aprobar
- **Setup**: Crear solicitud en 'in_review' sin resolution_date
- **Acción**: action_approve()
- **Aserción**: resolution_date == fecha actual

**Test: `test_resolution_date_set_on_reject`**
- **Objetivo**: Verificar que resolution_date se establece al rechazar
- **Setup**: Crear solicitud en 'in_review' sin resolution_date
- **Acción**: action_reject()
- **Aserción**: resolution_date == fecha actual

---

### 1.5. Tests de Flujo Completo

**Test: `test_complete_approval_workflow`**
- **Flujo**: draft → submit → approve
- **Aserciones en cada paso**: estado correcto, campos actualizados

**Test: `test_complete_rejection_workflow`**
- **Flujo**: draft → submit → reject
- **Aserciones en cada paso**: estado correcto, campos actualizados

---

## 2. Tests del Controlador HTTP

### 2.1. Tests del Endpoint `/remote_work/approved_requests`

**Test: `test_get_approved_requests_empty`**
- **Setup**: Sin solicitudes aprobadas
- **Acción**: GET al endpoint
- **Aserción**: JSON = []

**Test: `test_get_approved_requests_with_data`**
- **Setup**: Crear 3 solicitudes: 1 draft, 1 in_review, 1 approved
- **Acción**: GET al endpoint
- **Aserciones**:
  - JSON contiene solo 1 elemento
  - Elemento tiene campos: id, employee, approver, dates, days_count, reason, state

**Test: `test_get_approved_requests_json_structure`**
- **Setup**: Crear solicitud aprobada con todos los campos
- **Acción**: GET al endpoint
- **Aserciones**:
  - JSON válido
  - Campos presentes: id, employee, approver, request_date, date_start, date_end, resolution_date, days_count, reason, state
  - Fechas en formato ISO

**Test: `test_get_approved_requests_date_serialization`**
- **Objetivo**: Verificar que fechas se serializan correctamente a ISO format
- **Setup**: Solicitud con fechas específicas
- **Aserción**: Fechas en formato 'YYYY-MM-DD'

**Test: `test_get_approved_requests_null_fields`**
- **Setup**: Solicitud aprobada con approver_id=False y campos opcionales vacíos
- **Aserciones**: Campos nulos devuelven "" o None apropiadamente

**Test: `test_get_approved_requests_authentication_required`**
- **Objetivo**: Verificar que el endpoint requiere autenticación (auth="user")
- **Acción**: Petición sin autenticación
- **Aserción**: Retorna error 401 o redirige a login

**Test: `test_get_approved_requests_multiple_records`**
- **Setup**: Crear 5 solicitudes aprobadas con diferentes empleados
- **Acción**: GET al endpoint
- **Aserción**: JSON contiene 5 elementos, todos con state='approved'

---

## 3. Tests de Seguridad y Permisos

### 3.1. Tests de Access Rights (ir.model.access)

**Test: `test_employee_group_can_read`**
- **Usuario**: Con grupo group_remote_work_request_employee
- **Acción**: Leer solicitud propia
- **Aserción**: No se levanta AccessError

**Test: `test_employee_group_can_create`**
- **Usuario**: Con grupo group_remote_work_request_employee
- **Acción**: Crear solicitud
- **Aserción**: Registro creado exitosamente

**Test: `test_employee_group_can_write`**
- **Usuario**: Con grupo group_remote_work_request_employee
- **Acción**: Modificar solicitud propia
- **Aserción**: Cambio aplicado exitosamente

**Test: `test_manager_group_can_approve`**
- **Usuario**: Con grupo group_remote_work_request_manager
- **Acción**: Aprobar solicitud donde es aprobador
- **Aserción**: Estado cambia a 'approved'

---

### 3.2. Tests de Record Rules

**Test: `test_employee_sees_only_own_requests`**
- **Setup**: Usuario1 con empleado1, Usuario2 con empleado2
- **Datos**: Crear solicitud para empleado1 y otra para empleado2
- **Acción**: Usuario1 busca todas las solicitudes
- **Aserción**: Usuario1 solo ve su propia solicitud

**Test: `test_manager_sees_only_assigned_requests`**
- **Setup**: Manager1 y Manager2, solicitudes con diferentes approver_id
- **Datos**: Solicitud A con approver=Manager1, Solicitud B con approver=Manager2
- **Acción**: Manager1 busca solicitudes
- **Aserción**: Manager1 solo ve Solicitud A

**Test: `test_employee_cannot_see_others_requests`**
- **Setup**: Empleado A y B, cada uno con solicitudes
- **Acción**: Empleado A intenta leer directamente solicitud de B
- **Aserción**: AccessError o registro vacío

**Test: `test_employee_cannot_write_others_requests`**
- **Setup**: Empleado A con solicitud, Empleado B intenta modificarla
- **Acción**: Empleado B intenta write()
- **Aserción**: AccessError

**Test: `test_manager_can_approve_assigned_requests_only`**
- **Setup**: Manager con solicitudes donde es/no es aprobador
- **Acción**: Intentar aprobar ambas
- **Aserción**: Solo puede aprobar donde es aprobador

---

### 3.3. Tests de Permisos en Acciones

**Test: `test_employee_cannot_approve_own_request`**
- **Setup**: Empleado con solicitud propia en 'in_review'
- **Acción**: Intentar action_approve()
- **Aserción**: AccessError o la acción no está disponible (según implementación)

**Test: `test_manager_cannot_modify_approved_request`**
- **Setup**: Solicitud en estado 'approved'
- **Acción**: Manager intenta cambiar fechas o motivo
- **Aserción**: ValidationError o la modificación es permitida (verificar regla de negocio)

---

## 4. Tests de Integración

### 4.1. Tests de Integración con HR

**Test: `test_create_request_with_hr_employee`**
- **Setup**: Crear empleado usando modelo hr.employee
- **Acción**: Crear solicitud con ese empleado
- **Aserción**: Relación employee_id funciona correctamente

**Test: `test_employee_without_user_fails`**
- **Objetivo**: Verificar comportamiento si empleado no tiene user_id
- **Setup**: Empleado sin usuario asociado
- **Acción**: Crear solicitud con ese empleado
- **Aserción**: user_id queda vacío o se maneja apropiadamente

---

### 4.2. Tests de Integración Vista-Modelo

**Test: `test_form_view_loads`**
- **Objetivo**: Verificar que la vista de formulario carga sin errores
- **Acción**: Abrir vista de formulario programáticamente
- **Aserción**: Vista cargada, campos visibles

**Test: `test_list_view_loads`**
- **Objetivo**: Verificar que la vista de lista carga sin errores
- **Acción**: Abrir vista de lista
- **Aserción**: Vista cargada, columnas correctas

---

## 5. Tests de Performance (Opcional)

**Test: `test_compute_days_performance`**
- **Objetivo**: Verificar que el cálculo no es costoso con muchos registros
- **Setup**: Crear 1000 solicitudes
- **Acción**: Cambiar fechas en todas
- **Aserción**: Tiempo de ejecución < umbral aceptable

**Test: `test_endpoint_performance_with_many_records`**
- **Setup**: Crear 10,000 solicitudes aprobadas
- **Acción**: GET al endpoint
- **Aserción**: Respuesta en tiempo razonable (< 2s)

---

## 6. Tests Edge Cases

**Test: `test_create_with_future_dates`**
- **Datos**: Fechas en el futuro
- **Aserción**: Permitido (o no, según reglas de negocio)

**Test: `test_create_with_past_dates`**
- **Datos**: Fechas en el pasado
- **Aserción**: Permitido (o no, según reglas de negocio)

**Test: `test_very_long_date_range`**
- **Datos**: date_start = '2025-01-01', date_end = '2025-12-31'
- **Aserción**: days_count calculado correctamente (365 días)

**Test: `test_reason_max_length`**
- **Objetivo**: Si hay límite de caracteres en 'reason'
- **Datos**: Texto muy largo
- **Aserción**: Se acepta o se trunca según diseño

**Test: `test_name_required`**
- **Datos**: Crear sin 'name'
- **Aserción**: ValidationError

**Test: `test_employee_required`**
- **Datos**: Crear sin employee_id
- **Aserción**: ValidationError

---

## 7. Estructura de Tests Sugerida

```
custom_addons/remote_work_requests/
├── tests/
│   ├── __init__.py
│   ├── test_remote_request_model.py       # Tests 1.x
│   ├── test_remote_request_workflow.py    # Tests de flujo de estado
│   ├── test_remote_request_controller.py  # Tests 2.x
│   ├── test_remote_request_security.py    # Tests 3.x
│   └── test_remote_request_integration.py # Tests 4.x
```

---

## 8. Configuración de Testing en Odoo

### 8.1. Añadir carpeta de tests al módulo

En `__manifest__.py`, asegurarse de tener:
```python
{
    'name': 'Remote Work Requests',
    'test': True,  # Habilitar modo test
    ...
}
```

### 8.2. Estructura básica de un test en Odoo

```python
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError

@tagged('post_install', '-at_install')
class TestRemoteRequest(TransactionCase):

    def setUp(self):
        super().setUp()
        # Setup común para todos los tests
        self.RemoteRequest = self.env['remote.work.request']
        self.employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
            'user_id': self.env.user.id,
        })

    def test_example(self):
        # Arrange
        data = {...}

        # Act
        record = self.RemoteRequest.create(data)

        # Assert
        self.assertEqual(record.state, 'draft')
```

### 8.3. Ejecutar tests

```bash
# Ejecutar todos los tests del módulo
docker exec -it docker-odoo-1 odoo -c /etc/odoo/odoo.conf \
  -d odoo_db --test-enable --stop-after-init \
  -u remote_work_requests

# Ejecutar tests específicos con tags
docker exec -it docker-odoo-1 odoo -c /etc/odoo/odoo.conf \
  -d odoo_db --test-enable --test-tags=remote_work_requests \
  --stop-after-init
```

---

## 9. Priorización de Tests

### Alta Prioridad (Implementar primero)
1. Tests de validación de fechas (1.3)
2. Tests de transiciones de estado (1.4)
3. Tests de permisos básicos (3.1, 3.2)
4. Tests del endpoint HTTP (2.1) - al menos los básicos

### Media Prioridad
5. Tests de cálculo de días (1.2)
6. Tests de creación y campos (1.1)
7. Tests de flujo completo (1.5)

### Baja Prioridad (Nice to have)
8. Tests de performance (5)
9. Tests de edge cases específicos (6)
10. Tests de integración con vistas (4.2)

---

## 10. Métricas de Cobertura Esperadas

- **Modelo**: > 90% de cobertura
- **Controlador**: > 80% de cobertura
- **Métodos críticos** (`_check_dates`, `action_*`): 100% de cobertura
- **Reglas de seguridad**: 100% de validación

---

## 11. Tests Específicos Adicionales Recomendados

### 11.1. Tests de Concurrencia

**Test: `test_concurrent_approval`**
- **Objetivo**: Verificar que dos managers no puedan aprobar la misma solicitud simultáneamente
- **Setup**: Solicitud en 'in_review', dos sesiones de usuario
- **Acción**: Ambos intentan aprobar al mismo tiempo
- **Aserción**: Solo una aprobación exitosa

### 11.2. Tests de Datos Demo

**Test: `test_demo_data_loads`**
- **Objetivo**: Verificar que datos demo se cargan sin errores
- **Acción**: Instalar módulo con demo=True
- **Aserción**: Registros demo existen y son válidos

---

## 12. Herramientas Recomendadas

- **Coverage.py**: Para medir cobertura de código Python
- **pytest-odoo**: Plugin de pytest para tests de Odoo (alternativa a unittest)
- **Faker**: Para generar datos de prueba realistas
- **freezegun**: Para mockear fechas en tests de resolution_date

---

## 13. Checklist de Implementación

- [ ] Crear carpeta `tests/` con `__init__.py`
- [ ] Implementar tests de alta prioridad (1.3, 1.4, 3.1, 3.2, 2.1)
- [ ] Configurar ejecución de tests en CI/CD (si aplica)
- [ ] Documentar cómo ejecutar tests en README
- [ ] Alcanzar > 80% de cobertura global
- [ ] Validar todos los tests pasan antes de cada commit (pre-commit hook)
- [ ] Revisar y actualizar tests con cada cambio en el modelo

---

## 14. Ejemplo de Test Completo

```python
# tests/test_remote_request_model.py

from datetime import date
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError

@tagged('post_install', '-at_install', 'remote_work_requests')
class TestRemoteRequestModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RemoteRequest = cls.env['remote.work.request']
        cls.employee = cls.env['hr.employee'].create({
            'name': 'John Doe',
            'user_id': cls.env.ref('base.user_admin').id,
        })

    def test_check_dates_invalid(self):
        """Test que valida que date_end no puede ser anterior a date_start"""
        with self.assertRaises(ValidationError) as cm:
            self.RemoteRequest.create({
                'name': 'Test Request',
                'employee_id': self.employee.id,
                'date_start': date(2025, 1, 20),
                'date_end': date(2025, 1, 15),
                'reason': 'Test',
            })
        self.assertIn('fecha de fin', str(cm.exception).lower())

    def test_days_count_calculation(self):
        """Test que verifica el cálculo correcto de días"""
        request = self.RemoteRequest.create({
            'name': 'Test Request',
            'employee_id': self.employee.id,
            'date_start': date(2025, 1, 15),
            'date_end': date(2025, 1, 20),
            'reason': 'Test',
        })
        self.assertEqual(request.days_count, 6)

    def test_action_submit_from_draft(self):
        """Test transición de draft a in_review"""
        request = self.RemoteRequest.create({
            'name': 'Test Request',
            'employee_id': self.employee.id,
            'date_start': date(2025, 1, 15),
            'date_end': date(2025, 1, 20),
            'reason': 'Test',
        })
        self.assertEqual(request.state, 'draft')

        request.action_submit()
        self.assertEqual(request.state, 'in_review')

    def test_action_approve_sets_resolution_date(self):
        """Test que aprobar establece resolution_date"""
        request = self.RemoteRequest.create({
            'name': 'Test Request',
            'employee_id': self.employee.id,
            'date_start': date(2025, 1, 15),
            'date_end': date(2025, 1, 20),
            'reason': 'Test',
            'state': 'in_review',  # Estado inicial para el test
        })
        self.assertFalse(request.resolution_date)

        request.action_approve()
        self.assertEqual(request.state, 'approved')
        self.assertTrue(request.resolution_date)
        self.assertEqual(request.resolution_date, date.today())
```

---

## Resumen Final

Este plan de tests cubre:
- ✅ **40+ tests** recomendados
- ✅ Validación de lógica de negocio (fechas, estados, cálculos)
- ✅ Seguridad (permisos, record rules)
- ✅ API HTTP (endpoint JSON)
- ✅ Integración con módulo HR
- ✅ Edge cases y performance

**Próximos pasos:**
1. Crear estructura de carpeta `tests/`
2. Implementar tests de alta prioridad
3. Configurar ejecución de tests en desarrollo
4. Iterar y añadir tests según bugs encontrados

---
