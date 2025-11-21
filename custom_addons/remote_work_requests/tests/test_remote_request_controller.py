# tests/test_remote_request_controller.py

import json
from datetime import date

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install", "remote_work_requests")
class TestRemoteRequestController(HttpCase):
    """Tests para el controlador HTTP y endpoint JSON"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RemoteRequest = cls.env["remote.work.request"]
        cls.HrEmployee = cls.env["hr.employee"]
        cls.ResUsers = cls.env["res.users"]

        # Crear usuario de prueba
        cls.test_user = cls.ResUsers.create(
            {
                "name": "API Test User",
                "login": "apiuser",
                "email": "apiuser@test.com",
            }
        )

        # Crear empleados
        cls.employee1 = cls.HrEmployee.create(
            {
                "name": "Employee One",
                "user_id": cls.test_user.id,
            }
        )

        cls.employee2 = cls.HrEmployee.create(
            {
                "name": "Employee Two",
            }
        )

        # Crear manager
        cls.manager_user = cls.ResUsers.create(
            {
                "name": "API Manager",
                "login": "apimanager",
                "email": "apimanager@test.com",
            }
        )

    def test_get_approved_requests_empty(self):
        """Test: Endpoint retorna lista válida (puede incluir datos demo)"""
        response = self.url_open("/remote_work/approved_requests")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

        # Verificar que devuelve JSON válido y es una lista
        data = json.loads(response.content)
        self.assertIsInstance(data, list)

    def test_get_approved_requests_with_data(self):
        """Test: Endpoint retorna solo solicitudes aprobadas"""
        # Crear solicitudes en diferentes estados
        draft_req = self.RemoteRequest.create(
            {
                "name": "Draft Request",
                "employee_id": self.employee1.id,
                "date_start": date(2025, 3, 1),
                "date_end": date(2025, 3, 5),
                "reason": "Draft",
                "state": "draft",
            }
        )

        in_review_req = self.RemoteRequest.create(
            {
                "name": "In Review Request",
                "employee_id": self.employee1.id,
                "date_start": date(2025, 3, 10),
                "date_end": date(2025, 3, 15),
                "reason": "In Review",
                "state": "in_review",
            }
        )

        approved_req = self.RemoteRequest.create(
            {
                "name": "Approved Request",
                "employee_id": self.employee1.id,
                "date_start": date(2025, 3, 20),
                "date_end": date(2025, 3, 25),
                "reason": "Approved",
                "state": "approved",
                "approver_id": self.manager_user.id,
                "resolution_date": date.today(),
            }
        )

        # Llamar endpoint
        response = self.url_open("/remote_work/approved_requests")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertIsInstance(data, list)

        # Filtrar por el ID de nuestra solicitud aprobada
        our_approved = [r for r in data if r["id"] == approved_req.id]
        self.assertGreaterEqual(
            len(our_approved), 1, "Approved request should be in response"
        )

        # Verificar que draft e in_review NO están
        draft_in_response = [r for r in data if r["id"] == draft_req.id]
        in_review_in_response = [r for r in data if r["id"] == in_review_req.id]
        self.assertEqual(
            len(draft_in_response), 0, "Draft request should not be in response"
        )
        self.assertEqual(
            len(in_review_in_response), 0, "In-review request should not be in response"
        )

    def test_get_approved_requests_json_structure(self):
        """Test: Verificar estructura del JSON"""
        # Crear solicitud aprobada
        request = self.RemoteRequest.create(
            {
                "name": "Test Structure",
                "employee_id": self.employee1.id,
                "date_start": date(2025, 4, 1),
                "date_end": date(2025, 4, 10),
                "reason": "Testing JSON structure",
                "state": "approved",
                "approver_id": self.manager_user.id,
                "resolution_date": date(2025, 4, 1),
            }
        )

        # Obtener datos
        response = self.url_open("/remote_work/approved_requests")
        data = json.loads(response.content)

        # Buscar nuestro registro
        our_record = next((r for r in data if r["id"] == request.id), None)
        self.assertIsNotNone(our_record)

        # Verificar campos esperados
        expected_fields = [
            "id",
            "employee",
            "approver",
            "request_date",
            "date_start",
            "date_end",
            "resolution_date",
            "days_count",
            "reason",
            "state",
        ]
        for field in expected_fields:
            self.assertIn(field, our_record)

    def test_get_approved_requests_date_serialization(self):
        """Test: Fechas se serializan en formato ISO"""
        request = self.RemoteRequest.create(
            {
                "name": "Date Format Test",
                "employee_id": self.employee1.id,
                "date_start": date(2025, 5, 15),
                "date_end": date(2025, 5, 20),
                "reason": "Date testing",
                "state": "approved",
                "approver_id": self.manager_user.id,
                "resolution_date": date(2025, 5, 15),
            }
        )

        response = self.url_open("/remote_work/approved_requests")
        data = json.loads(response.content)

        our_record = next((r for r in data if r["id"] == request.id), None)
        self.assertIsNotNone(our_record)

        # Verificar formato ISO de fechas
        self.assertEqual(our_record["date_start"], "2025-05-15")
        self.assertEqual(our_record["date_end"], "2025-05-20")
        self.assertEqual(our_record["resolution_date"], "2025-05-15")

    def test_get_approved_requests_days_count(self):
        """Test: days_count se incluye correctamente"""
        request = self.RemoteRequest.create(
            {
                "name": "Days Count Test",
                "employee_id": self.employee1.id,
                "date_start": date(2025, 6, 1),
                "date_end": date(2025, 6, 10),
                "reason": "10 days test",
                "state": "approved",
                "approver_id": self.manager_user.id,
            }
        )

        response = self.url_open("/remote_work/approved_requests")
        data = json.loads(response.content)

        our_record = next((r for r in data if r["id"] == request.id), None)
        self.assertIsNotNone(our_record)
        self.assertEqual(our_record["days_count"], 10)

    def test_get_approved_requests_multiple_records(self):
        """Test: Múltiples solicitudes aprobadas"""
        # Crear 5 solicitudes aprobadas
        requests = []
        for i in range(5):
            req = self.RemoteRequest.create(
                {
                    "name": f"Approved Request {i}",
                    "employee_id": self.employee1.id,
                    "date_start": date(2025, 7, 1 + i),
                    "date_end": date(2025, 7, 5 + i),
                    "reason": f"Reason {i}",
                    "state": "approved",
                }
            )
            requests.append(req)

        response = self.url_open("/remote_work/approved_requests")
        data = json.loads(response.content)

        # Verificar que todos nuestros registros están
        our_ids = [r.id for r in requests]
        response_ids = [r["id"] for r in data]

        for req_id in our_ids:
            self.assertIn(req_id, response_ids)

    def test_get_approved_requests_null_fields(self):
        """Test: Campos nulos se manejan correctamente"""
        request = self.RemoteRequest.create(
            {
                "name": "Null Fields Test",
                "employee_id": self.employee2.id,  # Sin user_id
                "date_start": date(2025, 8, 1),
                "date_end": date(2025, 8, 5),
                "reason": "Testing nulls",
                "state": "approved",
                # Sin approver_id
            }
        )

        response = self.url_open("/remote_work/approved_requests")
        data = json.loads(response.content)

        our_record = next((r for r in data if r["id"] == request.id), None)
        self.assertIsNotNone(our_record)

        # approver puede ser vacío
        self.assertIn("approver", our_record)
        # El valor es "" según el controlador
        self.assertEqual(our_record["approver"], "")
