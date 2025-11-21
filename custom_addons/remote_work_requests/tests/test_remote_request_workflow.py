# tests/test_remote_request_workflow.py

from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "remote_work_requests")
class TestRemoteRequestWorkflow(TransactionCase):
    """Tests para las transiciones de estado del workflow"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RemoteRequest = cls.env["remote.work.request"]
        cls.HrEmployee = cls.env["hr.employee"]
        cls.ResUsers = cls.env["res.users"]

        # Crear usuario y empleado
        cls.test_user = cls.ResUsers.create(
            {
                "name": "Test User",
                "login": "testuser_wf",
                "email": "testuser_wf@test.com",
            }
        )

        cls.employee = cls.HrEmployee.create(
            {
                "name": "Jane Smith",
                "user_id": cls.test_user.id,
            }
        )

        # Crear usuario manager
        cls.manager_user = cls.ResUsers.create(
            {
                "name": "Manager User",
                "login": "manager_wf",
                "email": "manager_wf@test.com",
            }
        )

    def _create_request(self, state="draft", approver_id=False):
        """Helper para crear solicitudes en diferentes estados"""
        return self.RemoteRequest.create(
            {
                "name": f"Request in {state}",
                "employee_id": self.employee.id,
                "date_start": date(2025, 2, 1),
                "date_end": date(2025, 2, 5),
                "reason": f"Testing {state} state",
                "state": state,
                "approver_id": approver_id if approver_id else False,
            }
        )

    def test_action_submit_from_draft(self):
        """Test: Transición draft → in_review"""
        request = self._create_request(state="draft")
        self.assertEqual(request.state, "draft")

        request.action_submit()
        self.assertEqual(request.state, "in_review")

    def test_action_submit_from_non_draft_fails(self):
        """Test: action_submit solo funciona desde draft"""
        # Probar desde in_review
        request = self._create_request(state="in_review")
        with self.assertRaises(ValidationError) as cm:
            request.action_submit()
        self.assertIn("borrador", str(cm.exception).lower())

    def test_action_approve_from_in_review(self):
        """Test: Transición in_review → approved"""
        request = self._create_request(
            state="in_review", approver_id=self.manager_user.id
        )
        self.assertEqual(request.state, "in_review")
        self.assertFalse(request.resolution_date)

        request.action_approve()
        self.assertEqual(request.state, "approved")
        self.assertTrue(request.resolution_date)
        self.assertEqual(request.resolution_date, date.today())

    def test_action_approve_from_non_in_review_fails(self):
        """Test: action_approve solo funciona desde in_review"""
        # Probar desde draft
        request = self._create_request(state="draft")
        with self.assertRaises(ValidationError) as cm:
            request.action_approve()
        self.assertIn("revisión", str(cm.exception).lower())

        # Probar desde approved
        request2 = self._create_request(state="approved")
        with self.assertRaises(ValidationError):
            request2.action_approve()

    def test_action_reject_from_in_review(self):
        """Test: Transición in_review → rejected"""
        request = self._create_request(
            state="in_review", approver_id=self.manager_user.id
        )
        self.assertEqual(request.state, "in_review")
        self.assertFalse(request.resolution_date)

        request.action_reject()
        self.assertEqual(request.state, "rejected")
        self.assertTrue(request.resolution_date)
        self.assertEqual(request.resolution_date, date.today())

    def test_action_reject_from_non_in_review_fails(self):
        """Test: action_reject solo funciona desde in_review"""
        # Probar desde draft
        request = self._create_request(state="draft")
        with self.assertRaises(ValidationError) as cm:
            request.action_reject()
        self.assertIn("revisión", str(cm.exception).lower())

        # Probar desde rejected
        request2 = self._create_request(state="rejected")
        with self.assertRaises(ValidationError):
            request2.action_reject()

    def test_resolution_date_set_on_approve(self):
        """Test: resolution_date se establece al aprobar"""
        request = self._create_request(state="in_review")
        self.assertFalse(request.resolution_date)

        request.action_approve()
        self.assertTrue(request.resolution_date)
        self.assertIsInstance(request.resolution_date, date)

    def test_resolution_date_set_on_reject(self):
        """Test: resolution_date se establece al rechazar"""
        request = self._create_request(state="in_review")
        self.assertFalse(request.resolution_date)

        request.action_reject()
        self.assertTrue(request.resolution_date)
        self.assertIsInstance(request.resolution_date, date)

    def test_complete_approval_workflow(self):
        """Test: Flujo completo draft → submit → approve"""
        request = self._create_request(state="draft")

        # Estado inicial
        self.assertEqual(request.state, "draft")
        self.assertFalse(request.resolution_date)

        # Enviar a revisión
        request.action_submit()
        self.assertEqual(request.state, "in_review")

        # Establecer aprobador
        request.write({"approver_id": self.manager_user.id})

        # Aprobar
        request.action_approve()
        self.assertEqual(request.state, "approved")
        self.assertTrue(request.resolution_date)
        self.assertEqual(request.approver_id, self.manager_user)

    def test_complete_rejection_workflow(self):
        """Test: Flujo completo draft → submit → reject"""
        request = self._create_request(state="draft")

        # Estado inicial
        self.assertEqual(request.state, "draft")

        # Enviar a revisión
        request.action_submit()
        self.assertEqual(request.state, "in_review")

        # Establecer aprobador
        request.write({"approver_id": self.manager_user.id})

        # Rechazar
        request.action_reject()
        self.assertEqual(request.state, "rejected")
        self.assertTrue(request.resolution_date)
        self.assertEqual(request.approver_id, self.manager_user)

    def test_multiple_requests_different_states(self):
        """Test: Múltiples solicitudes pueden estar en diferentes estados"""
        req1 = self._create_request(state="draft")
        req2 = self._create_request(state="draft")
        req3 = self._create_request(state="draft")

        req1.action_submit()
        req2.action_submit()
        req2.action_approve()

        self.assertEqual(req1.state, "in_review")
        self.assertEqual(req2.state, "approved")
        self.assertEqual(req3.state, "draft")
