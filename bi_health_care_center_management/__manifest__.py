# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': "Health Care Center Management",
    'version': "18.0.0.0",
    'summary': "Manage Health Care Center Management Operations  Industry  Management Services Custom Health Care Solution ",
    'description': """Manage Health Care Center Management Operations  Industry  Management Services Custom Health Care Solution.""",
    "author": "Ibrahim Elmasry",


    
    'depends': ['base', 'mail', 'account', 'product', 'website', 'contacts', 'event', 'website_event_sale', 'stock',
                'purchase',],
    'data': [
        'security/ir.model.access.csv',
        'data/admission_data.xml',
        'demo/product_demo.xml',
        'data/admission_enroll_email.xml',
        'data/student_inquiry_mail.xml',
        'data/booking_mail_template.xml',
        'data/web_menu.xml',
        'data/student_reservation_cron.xml',
        'data/driver_reservation_cron.xml',
        'data/weekdays.xml',
        'report/center_certificate_report.xml',

        'views/templates.xml',
        'wizard/create_invoice_views.xml',
        'wizard/reservation_conflict_wizard_view.xml',
        'wizard/reservation_driver_conflict_wizard_view.xml',
        'wizard/reservation_change_wizard_view.xml',
        'wizard/driver_reservation_change_wizard_view.xml',
        'views/res_partner_views.xml',
        'views/student_admission_views.xml',
        'data/center_sport_dashboard_views.xml',
        'views/student_inquiry_views.xml',
        'views/center_booking_views.xml',
        'views/product_views.xml',
        'views/event_views.xml',
        'views/center_certificate_views.xml',
        'views/purchase_views.xml',
        'views/student_reservation_views.xml',
        'views/driver_reservation_views.xml',
        'views/level_views.xml',
        'views/package_views.xml',
        'views/city_distance_views.xml',
        'views/nurse_specialty_views.xml',

        'views/account_move_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'bi_health_care_center_management/static/src/js/sport_center_frontend.js',
            'bi_health_care_center_management/static/src/js/jquery_datetimepicker_full_min.js',
            'bi_health_care_center_management/static/src/css/jquery_datetimepicker.css',
            'bi_health_care_center_management/static/src/css/custom_styles.css',
        ],
        'web.assets_backend': [
            'bi_health_care_center_management/static/src/js/dashboard_action.js',
            'bi_health_care_center_management/static/src/xml/dashboard.xml',
        ],
    },
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    "images": ['static/description/Banner.gif'],
}
