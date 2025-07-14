from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from pytz import timezone, UTC
from odoo.exceptions import ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)


class AdmissionRenewalWizard(models.TransientModel):
    _name = 'admission.renewal.wizard'
    _description = 'Admission Renewal Wizard'

    admission_id = fields.Many2one('student.admission', string='Admission', required=True,
                                   default=lambda self: self.env.context.get('active_id'))

    weekday_ids = fields.Many2many('weekday', string='Days')

    name = fields.Char('Name', required=True,
                       readonly=True, default=lambda self: _('New'))

    student_id = fields.Many2one('res.partner', string='Trainee Name', required=True,
                                 domain=[('is_coach', '=', False)])

    sport_id = fields.Many2one(
        'product.product', string="Sport Name", domain=[('is_sportname', '=', True)], required=True, )

    level_id = fields.Many2one('res.partner', string="Sport Center", domain=[
        ('is_sport', '=', True)], required=True, )

    trainer_id = fields.Many2one(comodel_name='res.partner', domain=[('is_coach', '=', True)], string='Coach')

    start_date = fields.Float(string="Start Date")
    end_date = fields.Float(string="End Date")

    start_duration = fields.Date(string='Start Date')
    old_start_duration = fields.Date(string='Start Date')
    end_duration = fields.Date(string='End Date', compute='_compute_end_duration')
    duration = fields.Integer("Duration(Days)", compute='_compute_duration')
    n_of_reservations = fields.Integer(string='Number of reservations', )
    is_vip = fields.Boolean(string='VIP')

    c_level_id = fields.Many2one('level.level', string='Level')

    @api.depends('start_duration', 'n_of_reservations', 'weekday_ids')
    def _compute_end_duration(self):
        for record in self:
            # Default value assignment
            record.end_duration = False

            # Ensure all required fields are present
            if not record.start_duration or not record.weekday_ids or not record.n_of_reservations:
                _logger.warning("Missing required fields for record ID %s", record.id)
                continue

            try:
                start_date = fields.Date.from_string(record.start_duration)
                weekdays = record.weekday_ids.mapped('name')
                weekday_map = {day: i for i, day in enumerate(
                    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])}

                # Filter and sort the selected weekdays
                selected_weekdays = sorted([weekday_map[day] for day in weekdays])
                reservations_left = record.n_of_reservations
                current_date = start_date

                # Calculate the end date
                while reservations_left > 0:
                    if current_date.weekday() in selected_weekdays:
                        reservations_left -= 1
                    current_date += timedelta(days=1)

                # Assign the last reserved date
                record.end_duration = current_date - timedelta(days=1)
            except Exception as e:
                # Log the error for debugging
                _logger.error("Error computing end_duration for record ID %s: %s", record.id, e)
                record.end_duration = False

    @api.depends('start_duration', 'end_duration')
    def _compute_duration(self):
        for record in self:
            if record.start_duration and record.end_duration:
                # Calculate the number of days directly
                delta = (record.end_duration - record.start_duration).days
                record.duration = float(delta) + 1  # Convert to float if needed
            else:
                record.duration = 0.0

    def action_confirm(self):

        for record in self:
            if record.admission_id:
                record.admission_id.write({
                    'weekday_ids': record.weekday_ids.ids,
                    'start_date': record.start_date,
                    'end_date': record.end_date,
                    'start_duration': record.start_duration,
                    'n_of_reservations': record.n_of_reservations,
                    'is_vip': record.is_vip,
                })

                record.admission_id.action_enroll()
                print(record.admission_id.end_duration)

                # record.admission_id.write({
                #     'n_of_reservations': len(record.admission_id.reservation_ids),
                # })
                print(record.admission_id.end_duration)

                record.admission_id.write({
                    'end_duration': record.end_duration,
                })

                print(record.admission_id.end_duration)
                record.action_create_invoice()
                print(record.admission_id.end_duration)

                return {'type': 'ir.actions.act_window_close'}

    def action_create_invoice(self):
        admission_id = self.admission_id
        if admission_id:
            sale_journals = self.env['account.journal'].sudo().search([('type', '=', 'sale')])
            invoice = self.env['account.move'].create({
                'invoice_origin': admission_id.name or '',
                'move_type': 'out_invoice',
                'ref': admission_id.name or '',
                'journal_id': sale_journals and sale_journals[0].id or False,
                'partner_id': admission_id.student_id.id,
                'invoice_date': fields.date.today(),
                'currency_id': admission_id.student_id.currency_id.id or self.env.user.currency_id.id,
                'company_id': self.env.user.company_id.id or False,
                'student_admission_id': admission_id.id or '',
            })

            # Calculate quantity in months based on duration and a predefined number of days per month
            days_per_month = 31  # Adjust this value as needed
            invoice_line_quantity = (self.duration + days_per_month - 1) // days_per_month

            if admission_id.sport_id:
                invoice.write({'invoice_line_ids': [
                    (0, 0, {
                        'product_id': admission_id.sport_id.id,
                        'name': admission_id.sport_id.display_name or '',
                        'product_uom_id': admission_id.sport_id.uom_id.id,
                        'price_unit': admission_id.sport_id.lst_price,
                        'quantity': invoice_line_quantity,  # Use calculated quantity in months
                        'move_name': admission_id.name or '',
                    })]})

        else:
            raise ValidationError('Admission Registration not found!')

    @api.constrains('n_of_reservations')
    def _check_n_of_reservations(self):
        for record in self:
            if record.n_of_reservations <= 0:
                raise ValidationError("The number of reservations cannot be 0 or negative.")

    @api.constrains('start_date', 'end_date')
    def _check_start_date_end_date(self):
        for record in self:
            if record.start_date <= 0:
                raise ValidationError(
                    "Enter a correct hour format for sessions time, EX: 13.50 (1:50 PM) or 18.25 (6:25 PM)")

            if record.end_date <= 0:
                raise ValidationError("Pick a correct hour format for end date, EX: 13.50 (1:50 PM) or 18.25 (6:25 PM)")
