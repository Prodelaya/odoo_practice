# remote_work_requests/controllers/main.py

import json

from odoo import http
from odoo.http import request


class RemoteWorkApprovedController(http.Controller):
    """Controlador para exponer solicitudes de trabajo remoto aprobadas."""

    @http.route(
        "/remote_work/approved_requests",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def get_approved_requests(self, **kwargs):
        """Devuelve en Json todas las solicitudes aprobadas.add()

        Pensado como endopoint simple para demo / integración interna
        """
        RemoteRequest = request.env["remote.work.request"]

        # 1) Buscar solo las solicitudes en estado 'approved'
        approved_requests = RemoteRequest.search([("state", "=", "approved")])

        # Serializar los campos clave a una lista de diccionarios
        data = []
        for rec in approved_requests:
            data.append(
                {
                    "id": rec.id,
                    "employee": rec.employee_id.name or "",
                    "approver": rec.approver_id.name or "",
                    "request_date": (
                        rec.request_date.isoformat() if rec.request_date else None
                    ),
                    "date_start": (
                        rec.date_start.isoformat() if rec.date_start else None
                    ),
                    "date_end": rec.date_end.isoformat() if rec.date_end else None,
                    "resolution_date": (
                        rec.resolution_date.isoformat() if rec.resolution_date else None
                    ),
                    "days_count": rec.days_count,
                    "reason": rec.reason or "",
                    "state": rec.state,
                }
            )

        # Devolver JSON como respuesta HTTP estándar
        return http.Response(
            json.dumps(data, default=str),
            content_type="application/json",
        )
