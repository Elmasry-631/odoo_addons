from odoo import models, fields, api
from datetime import datetime, timedelta, date


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    student_admission_id = fields.Many2one('student.admission',string='Trainee Admission')
    admission_n_of_reservations = fields.Integer(related='student_admission_id.n_of_reservations',store=1)
    admission_weekday_ids = fields.Many2many(related='student_admission_id.weekday_ids',)

    admission_start_date = fields.Float(related='student_admission_id.start_date',store=1)
    admission_end_date = fields.Float(related='student_admission_id.end_date',store=1)

    admission_start_duration = fields.Date(related='student_admission_id.start_duration',store=1)
    admission_end_duration = fields.Date(related='student_admission_id.end_duration',store=1)

