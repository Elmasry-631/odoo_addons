{
    "name": "CRM Project Linker",
    "version": "1.0",
    "author": "Ibrahim Elmasry",
    "website": "www.woledge.com",  # 👈 دي اللي بتظهر كلينك في واجهة Odoo
    "category": "CRM",
    "summary": "Create and link projects from CRM opportunities.",
    "description": """
        This module links CRM Opportunities to Projects seamlessly.

        Features:
        - Create Project from CRM
        - Link existing Project to Opportunity
        - Access Opportunity from Project
        - Shared Quotations between CRM and Project
    """,
    "depends": ["base", "project", "crm", "sale_management"],
    "data": [
        "views/crm_lead_view.xml"
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3"
}
