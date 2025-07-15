from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime




class AddSessionWizard(models.TransientModel):
    _name = 'add.session.wizard'
    _description = 'Add Extra Session Wizard'

    new_start = fields.Datetime("New Start Date", required=True)
    new_end = fields.Datetime("New End Date", required=True)

    def action_add_session(self):
        active_res_id = self.env.context.get('active_id')
        original = self.env['student.reservation'].browse(active_res_id)

        self.env['student.reservation'].create({
            'student_id': original.student_id.id,
            'sport_id': original.sport_id.id,
            'level_id': original.level_id.id,
            'trainer_id': original.trainer_id.id,
            'start_date': self.new_start,
            'end_date': self.new_end,
            'admission_id': original.admission_id.id,
        })