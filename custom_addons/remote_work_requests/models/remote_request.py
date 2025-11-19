from odoo import fields, models


class RemoteWorkRequest(models.Model):
    _name = "remote.work.request"
    _description = "Solicitud de trabajo en remoto"

    name = fields.Char(string="Nombre de la solicitud", required=True)
    employee_id = fields.Many2one("res.partner", string="Empleado")
