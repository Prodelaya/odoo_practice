# tests/test_remote_request_model.py

from datetime import date, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "remote_work_requests")
class TestRemoteRequestModel(TransactionCase):
    """Tests para el modelo remote.work.request - campos, validaciones, cálculos"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RemoteRequest = cls.env["remote.work.request"]
        cls.HrEmployee = cls.env["hr.employee"]
        cls.ResUsers = cls.env["res.users"]

        # Crear usuario de prueba
        cls.test_user = cls.ResUsers.create(
            {
                "name": "Test User",
                "login": "testuser",
                "email": "testuser@test.com",
            }
        )

        # Crear empleado asociado al usuario
        cls.employee = cls.HrEmployee.create(
            {
                "name": "John Doe",
                "user_id": cls.test_user.id,
            }
        )

    def test_create_remote_request_basic(self):
        """Test: Crear solicitud con campos mínimos"""
        request = self.RemoteRequest.create(
            {
                "name": "Test Request",
                "employee_id": self.employee.id,
                "date_start": date(2025, 1, 15),
                "date_end": date(2025, 1, 20),
                "reason": "Need to work from home",
            }
        )

        self.assertTrue(request)
        self.assertEqual(request.state, "draft")
        self.assertTrue(request.request_date)
        self.assertEqual(request.employee_id, self.employee)
        self.assertEqual(request.user_id, self.test_user)

    def test_user_id_related_field(self):
        """Test: user_id se sincroniza con employee_id.user_id"""
        request = self.RemoteRequest.create(
            {
                "name": "Test Request",
                "employee_id": self.employee.id,
                "date_start": date(2025, 1, 15),
                "date_end": date(2025, 1, 20),
                "reason": "Test",
            }
        )

        self.assertEqual(request.user_id, self.test_user)

    def test_days_count_single_day(self):
        """Test: Cálculo de días para un solo día"""
        request = self.RemoteRequest.create(
            {
                "name": "Single Day Request",
                "employee_id": self.employee.id,
                "date_start": date(2025, 1, 15),
                "date_end": date(2025, 1, 15),
                "reason": "One day remote work",
            }
        )

        self.assertEqual(request.days_count, 1)

    def test_days_count_multiple_days(self):
        """Test: Cálculo de días para múltiples días (inclusivo)"""
        request = self.RemoteRequest.create(
            {
                "name": "Multiple Days Request",
                "employee_id": self.employee.id,
                "date_start": date(2025, 1, 15),
                "date_end": date(2025, 1, 20),
                "reason": "Week remote work",
            }
        )

        # Del 15 al 20 = 6 días (inclusivo)
        self.assertEqual(request.days_count, 6)

    def test_days_count_recompute_on_date_change(self):
        """Test: days_count se recalcula al cambiar fechas"""
        request = self.RemoteRequest.create(
            {
                "name": "Test Request",
                "employee_id": self.employee.id,
                "date_start": date(2025, 1, 15),
                "date_end": date(2025, 1, 17),
                "reason": "Initial 3 days",
            }
        )

        self.assertEqual(request.days_count, 3)

        # Cambiar fecha de fin
        request.write({"date_end": date(2025, 1, 22)})
        self.assertEqual(request.days_count, 8)

    def test_check_dates_valid(self):
        """Test: Fechas válidas (end >= start) no lanzan error"""
        request = self.RemoteRequest.create(
            {
                "name": "Valid Dates",
                "employee_id": self.employee.id,
                "date_start": date(2025, 1, 15),
                "date_end": date(2025, 1, 20),
                "reason": "Valid range",
            }
        )

        self.assertTrue(request)

    def test_check_dates_equal(self):
        """Test: Fechas iguales son válidas"""
        request = self.RemoteRequest.create(
            {
                "name": "Same Date",
                "employee_id": self.employee.id,
                "date_start": date(2025, 1, 15),
                "date_end": date(2025, 1, 15),
                "reason": "Same day",
            }
        )

        self.assertTrue(request)

    def test_check_dates_invalid(self):
        """Test: date_end < date_start lanza ValidationError"""
        with self.assertRaises(ValidationError) as cm:
            self.RemoteRequest.create(
                {
                    "name": "Invalid Dates",
                    "employee_id": self.employee.id,
                    "date_start": date(2025, 1, 20),
                    "date_end": date(2025, 1, 15),
                    "reason": "Invalid range",
                }
            )

        self.assertIn("fecha", str(cm.exception).lower())

    def test_very_long_date_range(self):
        """Test: Rango de fechas muy largo (edge case)"""
        request = self.RemoteRequest.create(
            {
                "name": "Long Range",
                "employee_id": self.employee.id,
                "date_start": date(2025, 1, 1),
                "date_end": date(2025, 12, 31),
                "reason": "Full year",
            }
        )

        self.assertEqual(request.days_count, 365)

    def test_name_required(self):
        """Test: Campo 'name' es requerido"""
        with self.assertRaises(Exception):  # ValidationError o IntegrityError
            self.RemoteRequest.create(
                {
                    "employee_id": self.employee.id,
                    "date_start": date(2025, 1, 15),
                    "date_end": date(2025, 1, 20),
                    "reason": "Test",
                }
            )

    def test_employee_required(self):
        """Test: Campo 'employee_id' es requerido"""
        with self.assertRaises(Exception):
            self.RemoteRequest.create(
                {
                    "name": "No Employee",
                    "date_start": date(2025, 1, 15),
                    "date_end": date(2025, 1, 20),
                    "reason": "Test",
                }
            )

    def test_create_with_future_dates(self):
        """Test: Fechas futuras son aceptadas"""
        future_date = date.today() + timedelta(days=30)
        request = self.RemoteRequest.create(
            {
                "name": "Future Request",
                "employee_id": self.employee.id,
                "date_start": future_date,
                "date_end": future_date + timedelta(days=5),
                "reason": "Future planning",
            }
        )

        self.assertTrue(request)
        self.assertTrue(request.date_start > date.today())

    def test_create_with_past_dates(self):
        """Test: Fechas pasadas son aceptadas"""
        past_date = date.today() - timedelta(days=30)
        request = self.RemoteRequest.create(
            {
                "name": "Past Request",
                "employee_id": self.employee.id,
                "date_start": past_date,
                "date_end": past_date + timedelta(days=5),
                "reason": "Retroactive request",
            }
        )

        self.assertTrue(request)
        self.assertTrue(request.date_start < date.today())
