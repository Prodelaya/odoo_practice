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
        "views/remote_request_view.xml",
    ],
    "application": True,
    "installable": True,
}
