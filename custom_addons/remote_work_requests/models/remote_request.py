from odoo import _, api, fields, models  # noqa: I001
from odoo.exceptions import ValidationError


class RemoteWorkRequest(models.Model):
    _name = "remote.work.request"
    _description = "Solicitud de trabajo en remoto"

    name = fields.Char(string="Nombre de la solicitud", required=True)

    # Empleado solicitante (ligado al usuario logueado)
    employee_id = fields.Many2one(
        "hr.employee",
        string="Empleado",
        required=True,
        default=lambda self: self.env["hr.employee"].search(
            [("user_id", "=", self.env.user.id)], limit=1
        ),
    )

    # Usuario aprobador (manager, RRHH, etc.)
    approver_id = fields.Many2one(
        "res.users",
        string="Aprobador",
    )

    # Usuario solicitante: siempre el user del empleado
    user_id = fields.Many2one(
        "res.users",
        string="Usuario",
        related="employee_id.user_id",
        store=True,
        readonly=True,
    )

    request_date = fields.Date(
        string="Fecha de la solicitud",
        default=fields.Date.context_today,
        readonly=True,
    )
    date_start = fields.Date(string="Fecha de inicio", required=True)
    date_end = fields.Date(string="Fecha de fin", required=True)

    reason = fields.Text(string="Motivo", required=True)

    state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("in_review", "En revisión"),
            ("approved", "Aprobado"),
            ("rejected", "Rechazado"),
        ],
        string="Estado",
        default="draft",
    )

    # Número de días solicitados (incluye inicio y fin)
    days_count = fields.Integer(
        string="Número de días",
        compute="_compute_days_count",
        store=True,
        readonly=True,
    )

    # Fecha en la que se aprueba / rechaza
    resolution_date = fields.Date(
        string="Fecha de resolución",
        readonly=True,
    )

    # ---------- LÓGICA DE NEGOCIO ----------

    @api.depends("date_start", "date_end")
    def _compute_days_count(self):
        """Calcula el número de días entre inicio y fin (ambos incluidos)."""
        for request in self:
            if request.date_start and request.date_end:
                delta = (request.date_end - request.date_start).days
                # Usamos inclusivo: del 10 al 12 = 3 días
                request.days_count = delta + 1 if delta >= 0 else 0
            else:
                request.days_count = 0

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        """Evita que la fecha de fin sea anterior a la de inicio."""
        for request in self:
            if (
                request.date_start
                and request.date_end
                and request.date_end < request.date_start
            ):
                raise ValidationError(
                    _("La fecha de fin no puede ser anterior a la fecha de inicio.")
                )

    def action_submit(self):
        """Envía la solicitud para revisión."""
        for request in self:
            if request.state != "draft":
                raise ValidationError(
                    _("Solo se pueden enviar solicitudes en estado Borrador.")
                )
            request.state = "in_review"

    def action_approve(self):
        """Aprobar la solicitud y fijar la fecha de resolución."""
        today = fields.Date.context_today(self)
        for request in self:
            if request.state != "in_review":
                raise ValidationError(
                    _("Solo se pueden aprobar solicitudes en estado En revisión.")
                )
            request.state = "approved"
            request.resolution_date = today

    def action_reject(self):
        """Rechazar la solicitud y fijar la fecha de resolución."""
        today = fields.Date.context_today(self)
        for request in self:
            if request.state != "in_review":
                raise ValidationError(
                    _("Solo se pueden rechazar solicitudes en estado En revisión.")
                )
            request.state = "rejected"
            request.resolution_date = today
