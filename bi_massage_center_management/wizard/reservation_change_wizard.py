from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from pytz import timezone, UTC
from odoo.exceptions import ValidationError


class ReservationChangeWizard(models.TransientModel):
    _name = 'reservation.change.wizard'
    _description = 'Reservation Change Wizard'

    reservation_id = fields.Many2one('student.reservation', string='Reservation', required=True,
                                     default=lambda self: self.env.context.get('active_id'))
    new_start_date = fields.Datetime(string='New Start Date', required=True, )
    new_end_date = fields.Datetime(string='New End Date', required=True, )
    new_trainer_id = fields.Many2one('res.partner', domain=[('is_coach', '=', True)], string='New Therapist',
                                     required=True, )

    def action_confirm(self):
        reservation = self.env['student.reservation'].browse(self.reservation_id.id)
        # Convert start_date and end_date from float to datetime
        for record in self:
            if record.new_trainer_id:
                # Get user's timezone
                user_tz = self.env.user.tz or 'UTC'
                user_timezone = timezone(user_tz)
                
                # Convert UTC dates to user's timezone for display
                start_date_local = record.new_start_date.replace(tzinfo=timezone('UTC')).astimezone(user_timezone)
                end_date_local = record.new_end_date.replace(tzinfo=timezone('UTC')).astimezone(user_timezone)

                overlapping_reservations = self.env['student.reservation'].search([
                    ('trainer_id', '=', record.new_trainer_id.id),
                    ('id', '!=', record.reservation_id.id),  # Exclude current reservation
                    ('start_date', '<', record.new_end_date),
                    ('end_date', '>', record.new_start_date),
                    ('state', '!=', 'finished')  # Only check non-finished reservations
                ])

                if overlapping_reservations:
                    # Get details of the first overlapping reservation
                    conflict = overlapping_reservations[0]
                    conflict_start = conflict.start_date.replace(tzinfo=timezone('UTC')).astimezone(user_timezone)
                    conflict_end = conflict.end_date.replace(tzinfo=timezone('UTC')).astimezone(user_timezone)
                    
                    raise ValidationError(
                        _("Therapist %s already has a reservation with %s during this time period (%s - %s).\nConflicting reservation: %s (%s - %s)") % 
                        (record.new_trainer_id.name,
                         conflict.student_id.name,
                         start_date_local.strftime('%Y-%m-%d %H:%M:%S'),
                         end_date_local.strftime('%Y-%m-%d %H:%M:%S'),
                         conflict.student_id.name,
                         conflict_start.strftime('%Y-%m-%d %H:%M:%S'),
                         conflict_end.strftime('%Y-%m-%d %H:%M:%S'))
                    )

        reservation.write({
            'start_date': self.new_start_date,
            'end_date': self.new_end_date,
            'trainer_id': self.new_trainer_id.id,
        })
        return {'type': 'ir.actions.act_window_close'}
