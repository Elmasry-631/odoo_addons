{
    'name': "Sale Contract Auto",
    'version': '0.1',
    'category': 'Sales',
    'summary': "Automatically generate contracts from sale orders.",
    'author': "Ibrahim Elmasry",
    'website': "https://www.woledge.com",
    'license': 'LGPL-3',

    'depends': [
        'base',
        'sale',
        'account',
        'website',  # <-- Important dependency
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/ir_sequence.xml',
        'views/views.xml',
        'views/sale_contract_form.xml',
        'report/contract_report.xml',
        'report/contract_print_template.xml',
        'views/templates.xml', # For the portal
        'data/mail_templates.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}