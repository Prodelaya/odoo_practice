# ~/proyectos/odoo_practice/custom_addons/remote_work_requests/__manifest__.py
{
    "name": "Remote Work Requests",
    "version": "1.0",
    "author": "Pablo",
    "category": "Human Resources",
    "summary": "Gestión de solicitudes de trabajo en remoto",
    "icon": "remote_work_requests/static/description/icon.png",
    "depends": ["base", "hr"],
    "data": [
        "security/remote_request_groups.xml",
        "security/remote_request_rules.xml",
        "security/ir.model.access.csv",
        "data/hr_demo.xml",
        "data/remote_request_demo.xml",
        "views/remote_request_view.xml",
    ],
    "application": True,
    "installable": True,
}
