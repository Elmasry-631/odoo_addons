from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class StudentReservation(models.Model):
    _inherit = "student.reservation"

    def action_add_session_wizard(self):
        return {
            'name': _('Add Extra Session'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'add.session.wizard',
            'target': 'new',
            'context': {'active_id': self.id},
        }
