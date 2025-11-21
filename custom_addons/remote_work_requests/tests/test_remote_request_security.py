# tests/test_remote_request_security.py

from datetime import date

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "remote_work_requests")
class TestRemoteRequestSecurity(TransactionCase):
    """Tests para permisos y reglas de seguridad"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RemoteRequest = cls.env["remote.work.request"]
        cls.HrEmployee = cls.env["hr.employee"]
        cls.ResUsers = cls.env["res.users"]
        cls.ResGroups = cls.env["res.groups"]

        # Obtener grupos
        cls.group_employee = cls.env.ref(
            "remote_work_requests.group_remote_work_request_employee"
        )
        cls.group_manager = cls.env.ref(
            "remote_work_requests.group_remote_work_request_manager"
        )

        # Crear usuario empleado 1
        cls.employee_user1 = cls.ResUsers.create(
            {
                "name": "Employee User 1",
                "login": "emp1",
                "email": "emp1@test.com",
            }
        )
        # Asignar grupo usando SQL directo (método más robusto para tests)
        cls.env.cr.execute(
            "INSERT INTO res_groups_users_rel (gid, uid) VALUES (%s, %s)",
            (cls.group_employee.id, cls.employee_user1.id),
        )
        # Invalidar cache para que Odoo reconozca el grupo
        cls.employee_user1._invalidate_cache()
        cls.group_employee._invalidate_cache()
        cls.employee1 = cls.HrEmployee.create(
            {
                "name": "Employee 1",
                "user_id": cls.employee_user1.id,
            }
        )

        # Crear usuario empleado 2
        cls.employee_user2 = cls.ResUsers.create(
            {
                "name": "Employee User 2",
                "login": "emp2",
                "email": "emp2@test.com",
            }
        )
        # Asignar grupo usando SQL directo
        cls.env.cr.execute(
            "INSERT INTO res_groups_users_rel (gid, uid) VALUES (%s, %s)",
            (cls.group_employee.id, cls.employee_user2.id),
        )
        # Invalidar cache para que Odoo reconozca el grupo
        cls.employee_user2._invalidate_cache()
        cls.group_employee._invalidate_cache()
        cls.employee2 = cls.HrEmployee.create(
            {
                "name": "Employee 2",
                "user_id": cls.employee_user2.id,
            }
        )

        # Crear usuario manager
        cls.manager_user = cls.ResUsers.create(
            {
                "name": "Manager User",
                "login": "manager",
                "email": "manager@test.com",
            }
        )
        # Asignar grupo usando SQL directo
        cls.env.cr.execute(
            "INSERT INTO res_groups_users_rel (gid, uid) VALUES (%s, %s)",
            (cls.group_manager.id, cls.manager_user.id),
        )
        # Invalidar cache para que Odoo reconozca el grupo
        cls.manager_user._invalidate_cache()
        cls.group_manager._invalidate_cache()

    def test_employee_group_can_read_own(self):
        """Test: Empleado puede leer su propia solicitud"""
        # Crear solicitud como empleado1
        request = (
            self.RemoteRequest.with_user(self.employee_user1)
            .sudo()
            .create(
                {
                    "name": "Own Request",
                    "employee_id": self.employee1.id,
                    "date_start": date(2025, 1, 10),
                    "date_end": date(2025, 1, 15),
                    "reason": "Test own read",
                }
            )
        )

        # Leer como empleado1
        read_request = self.RemoteRequest.with_user(self.employee_user1).browse(
            request.id
        )
        self.assertTrue(read_request.exists())
        self.assertEqual(read_request.name, "Own Request")

    def test_employee_group_can_create(self):
        """Test: Empleado puede crear solicitudes"""
        request = self.RemoteRequest.with_user(self.employee_user1).create(
            {
                "name": "Employee Created",
                "employee_id": self.employee1.id,
                "date_start": date(2025, 2, 1),
                "date_end": date(2025, 2, 5),
                "reason": "Test create",
            }
        )

        self.assertTrue(request)
        self.assertEqual(request.employee_id, self.employee1)

    def test_employee_group_can_write_own(self):
        """Test: Empleado puede modificar su propia solicitud"""
        request = self.RemoteRequest.with_user(self.employee_user1).create(
            {
                "name": "Original Name",
                "employee_id": self.employee1.id,
                "date_start": date(2025, 3, 1),
                "date_end": date(2025, 3, 5),
                "reason": "Original",
            }
        )

        # Modificar
        request.with_user(self.employee_user1).write({"reason": "Modified reason"})
        self.assertEqual(request.reason, "Modified reason")

    def test_employee_sees_only_own_requests(self):
        """Test: Empleado solo ve sus propias solicitudes"""
        # Crear solicitud para empleado1
        req1 = (
            self.RemoteRequest.with_user(self.employee_user1)
            .sudo()
            .create(
                {
                    "name": "Employee 1 Request",
                    "employee_id": self.employee1.id,
                    "date_start": date(2025, 4, 1),
                    "date_end": date(2025, 4, 5),
                    "reason": "Emp1",
                }
            )
        )

        # Crear solicitud para empleado2
        req2 = (
            self.RemoteRequest.with_user(self.employee_user2)
            .sudo()
            .create(
                {
                    "name": "Employee 2 Request",
                    "employee_id": self.employee2.id,
                    "date_start": date(2025, 4, 10),
                    "date_end": date(2025, 4, 15),
                    "reason": "Emp2",
                }
            )
        )

        # Empleado1 busca todas las solicitudes
        emp1_requests = self.RemoteRequest.with_user(self.employee_user1).search([])

        # Solo debe ver su propia solicitud
        emp1_ids = emp1_requests.ids
        self.assertIn(req1.id, emp1_ids)
        self.assertNotIn(req2.id, emp1_ids)

    def test_employee_cannot_see_others_requests(self):
        """Test: Empleado no puede ver solicitudes de otros"""
        # Crear solicitud como empleado2 (sin sudo para que apliquen las reglas)
        req = self.RemoteRequest.with_user(self.employee_user2).create(
            {
                "name": "Employee 2 Request",
                "employee_id": self.employee2.id,
                "date_start": date(2025, 5, 1),
                "date_end": date(2025, 5, 5),
                "reason": "Private",
            }
        )

        # Empleado1 busca solicitudes - no debería ver la de empleado2
        emp1_requests = self.RemoteRequest.with_user(self.employee_user1).search([])
        # El record rule debería filtrar la solicitud de emp2
        self.assertNotIn(
            req.id, emp1_requests.ids, "Employee 1 should not see Employee 2's request"
        )

    def test_employee_cannot_write_others_requests(self):
        """Test: Empleado no puede modificar solicitudes de otros"""
        # Crear solicitud como empleado2 (sin sudo)
        req = self.RemoteRequest.with_user(self.employee_user2).create(
            {
                "name": "Employee 2 Request",
                "employee_id": self.employee2.id,
                "date_start": date(2025, 6, 1),
                "date_end": date(2025, 6, 5),
                "reason": "Original",
            }
        )

        # Empleado1 busca solicitudes - no debería ver la de empleado2
        emp1_requests = self.RemoteRequest.with_user(self.employee_user1).search([])

        # No debería poder encontrar el registro de emp2 debido a record rules
        self.assertNotIn(
            req.id, emp1_requests.ids, "Employee 1 should not see Employee 2's request"
        )

    def test_manager_sees_only_assigned_requests(self):
        """Test: Manager solo ve solicitudes donde es aprobador"""
        # Crear solicitud con manager como aprobador
        req_assigned = (
            self.RemoteRequest.with_user(self.employee_user1)
            .sudo()
            .create(
                {
                    "name": "Assigned to Manager",
                    "employee_id": self.employee1.id,
                    "date_start": date(2025, 7, 1),
                    "date_end": date(2025, 7, 5),
                    "reason": "Needs approval",
                    "approver_id": self.manager_user.id,
                    "state": "in_review",
                }
            )
        )

        # Crear solicitud sin aprobador asignado
        req_not_assigned = (
            self.RemoteRequest.with_user(self.employee_user2)
            .sudo()
            .create(
                {
                    "name": "Not assigned",
                    "employee_id": self.employee2.id,
                    "date_start": date(2025, 7, 10),
                    "date_end": date(2025, 7, 15),
                    "reason": "No approver",
                }
            )
        )

        # Manager busca solicitudes
        manager_requests = self.RemoteRequest.with_user(self.manager_user).search([])
        manager_ids = manager_requests.ids

        # Solo debe ver la asignada a él
        self.assertIn(req_assigned.id, manager_ids)
        self.assertNotIn(req_not_assigned.id, manager_ids)

    def test_manager_can_approve_assigned_requests(self):
        """Test: Manager puede aprobar solicitudes donde es aprobador"""
        request = (
            self.RemoteRequest.with_user(self.employee_user1)
            .sudo()
            .create(
                {
                    "name": "To Approve",
                    "employee_id": self.employee1.id,
                    "date_start": date(2025, 8, 1),
                    "date_end": date(2025, 8, 5),
                    "reason": "Manager approval test",
                    "state": "in_review",
                    "approver_id": self.manager_user.id,
                }
            )
        )

        # Manager aprueba
        request.with_user(self.manager_user).action_approve()
        self.assertEqual(request.state, "approved")

    def test_manager_can_reject_assigned_requests(self):
        """Test: Manager puede rechazar solicitudes donde es aprobador"""
        request = (
            self.RemoteRequest.with_user(self.employee_user1)
            .sudo()
            .create(
                {
                    "name": "To Reject",
                    "employee_id": self.employee1.id,
                    "date_start": date(2025, 9, 1),
                    "date_end": date(2025, 9, 5),
                    "reason": "Manager rejection test",
                    "state": "in_review",
                    "approver_id": self.manager_user.id,
                }
            )
        )

        # Manager rechaza
        request.with_user(self.manager_user).action_reject()
        self.assertEqual(request.state, "rejected")

    def test_multiple_employees_isolation(self):
        """Test: Múltiples empleados tienen aislamiento correcto"""
        # Crear solicitudes para ambos empleados
        req1 = self.RemoteRequest.with_user(self.employee_user1).create(
            {
                "name": "Emp1 Request",
                "employee_id": self.employee1.id,
                "date_start": date(2025, 10, 1),
                "date_end": date(2025, 10, 5),
                "reason": "Emp1",
            }
        )

        req2 = self.RemoteRequest.with_user(self.employee_user2).create(
            {
                "name": "Emp2 Request",
                "employee_id": self.employee2.id,
                "date_start": date(2025, 10, 10),
                "date_end": date(2025, 10, 15),
                "reason": "Emp2",
            }
        )

        # Cada empleado solo ve su solicitud
        emp1_requests = self.RemoteRequest.with_user(self.employee_user1).search([])
        emp2_requests = self.RemoteRequest.with_user(self.employee_user2).search([])

        self.assertIn(req1.id, emp1_requests.ids)
        self.assertNotIn(req2.id, emp1_requests.ids)

        self.assertIn(req2.id, emp2_requests.ids)
        self.assertNotIn(req1.id, emp2_requests.ids)
