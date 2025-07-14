# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date
from pytz import timezone, UTC

import logging

_logger = logging.getLogger(__name__)


class StudentAdmission(models.Model):
    _name = "student.admission"
    _description = "Trainee Admission"

    weekday_ids = fields.Many2many('weekday', string='Days')

    day_one = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], string='First Day', )

    day_two = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], string='Second Day', )

    name = fields.Char('Name', required=True,
                       readonly=True, default=lambda self: _('New'))
    student_id = fields.Many2one('res.partner', string='Trainee Name', required=True,
                                 domain=[('is_coach', '=', False)])
    mobile = fields.Char('Mobile', related='student_id.mobile', store=True, readonly=False)
    p_name = fields.Char('Parent Name', related='student_id.p_name', readonly=False)
    parent_mobile = fields.Char('Parent Mobile', related='student_id.phone', readonly=False)
    p1_name = fields.Char('Parent Name ', related='inquiry_id.p_name', readonly=False)
    parent1_mobile = fields.Char('Parent Mobile ', related='inquiry_id.parent_mobile', readonly=False)
    email = fields.Char('Email', related='student_id.email', store=True, readonly=False)
    is_disability = fields.Boolean('Description', related='student_id.is_disability', store=True, readonly=False)
    disability_description = fields.Text('Disability Description', related='student_id.disability_description',
                                         store=True, readonly=False)
    sport_id = fields.Many2one(
        'product.product', string="Sport Name", domain=[('is_sportname', '=', True)], required=True, )
    level_id = fields.Many2one('res.partner', string="Sport Center", domain=[
        ('is_sport', '=', True)], required=True, )
    trainer_id = fields.Many2one(comodel_name='res.partner', domain=[('is_coach', '=', True)], string='Coach')
    state = fields.Selection([
        ('new', 'New'),
        ('enrolled', 'Enrolled'),
        ('student', 'Trainee'),
        ('cancel', 'Ended')], string='State',
        copy=False, default="new", store=True)
    is_invoiced = fields.Boolean()
    n_of_invoices = fields.Integer(compute='_compute_n_of_invoices')
    inquiry_id = fields.Many2one('student.inquiry', string='Inquiry')
    check_parent = fields.Boolean('Check Parent', related='inquiry_id.check_parent')
    check_register = fields.Boolean('Check Register')
    start_date = fields.Float(string="Start Date")
    end_date = fields.Float(string="End Date")

    start_duration = fields.Date(string='Start Date')
    end_duration = fields.Date(string='End Date', compute='_compute_end_duration')
    duration = fields.Integer("Duration(Days)", compute='_compute_duration')

    is_warning = fields.Boolean(string="Warning", compute="_compute_is_warning", store=True)
    n_of_reservations = fields.Integer(string='Number of reservations', )

    n_of_reservations_done = fields.Integer(string='Number of reservations done',
                                            compute='_compute_n_of_reservations_done')
    reservation_ids = fields.One2many('student.reservation', 'admission_id')
    is_reservation_done = fields.Boolean(compute='_compute_is_reservation_done')
    n_of_reservations_unfinished = fields.Integer(string='UnFinished reservations',
                                                  compute='_compute_n_of_reservations_unfinished', store=1)
    is_vip = fields.Boolean(string='VIP')
    birth_date = fields.Date(string='Birth Date', )
    age = fields.Integer(string='Age', compute='_compute_age')
    c_level_id = fields.Many2one('level.level', string='Level')
    is_admission_finished = fields.Boolean()

    @api.depends('state')
    def _compute_n_of_invoices(self):
        for rec in self:
            rec.n_of_invoices = len(self.env['account.move'].search([('invoice_origin', '=', self.name)]))

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

    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = date.today()
                birth_year = record.birth_date.year
                # Calculate age by subtracting birth year from current year and potentially adjusting for incomplete year
                age = today.year - birth_year - (
                        (today.month, today.day) < (record.birth_date.month, record.birth_date.day))
                record.age = age
            else:
                record.age = 0

    @api.depends('reservation_ids.state')
    def _compute_n_of_reservations_unfinished(self):
        for rec in self:
            n_of_unfinished_reservations = len(rec.reservation_ids.filtered(lambda r: r.state != 'finished'))
            rec.n_of_reservations_unfinished = n_of_unfinished_reservations

    @api.depends('reservation_ids')
    def _compute_is_reservation_done(self):
        for rec in self:
            if rec.reservation_ids and len(rec.reservation_ids) == rec.n_of_reservations:
                rec.is_reservation_done = True
            else:
                rec.is_reservation_done = False

    @api.depends('reservation_ids')
    def _compute_n_of_reservations_done(self):
        for rec in self:
            rec.n_of_reservations_done = len(rec.reservation_ids)

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

    @api.constrains('duration')
    def _check_duration(self):
        for record in self:
            if record.duration <= 0:
                raise ValidationError("The duration cannot be 0 or negative.")

    @api.constrains('start_date', 'end_date')
    def _check_valid_time(self):
        def float_to_time(hour_float):
            hour = int(hour_float)
            minute = round((hour_float - hour) * 100)  # Use round to avoid precision issues
            if minute >= 60:
                raise ValueError("Invalid time format: Minutes cannot exceed 59.")
            return datetime.strptime(f"{hour}:{minute:02}", "%H:%M").time()

        for record in self:
            try:
                start_time = float_to_time(record.start_date)
                end_time = float_to_time(record.end_date)

                # Additional Validation: Ensure start_time is before end_time
                if start_time >= end_time:
                    raise ValueError("Start time must be earlier than end time.")
            except ValueError as e:
                raise ValidationError(f"Invalid time format: {e}")

    @api.depends('end_duration')
    def _compute_is_warning(self):
        for record in self:
            if record.end_duration:
                # Calculate the warning date as a `datetime.date`
                warning_date = date.today() + timedelta(days=5)
                # Compare `end_date` (date) with `warning_date` (also date)
                record.is_warning = record.end_duration <= warning_date
            else:
                record.is_warning = False

    @api.model
    def _update_is_warning(self):
        """Update the warning field for all records."""
        admissions = self.search([])
        for admission in admissions:
            admission._compute_is_warning()

    @api.depends('start_duration', 'end_duration')
    def _compute_duration(self):
        for record in self:
            if record.start_duration and record.end_duration:
                # Calculate the number of days directly
                delta = (record.end_duration - record.start_duration).days
                record.duration = float(delta) + 1  # Convert to float if needed
            else:
                record.duration = 0.0

    @api.onchange('trainer_id')
    def _onchange_trainer_id(self):
        if self.trainer_id and self.student_id:
            self.student_id.trainer_id = self.trainer_id.id

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'student.admission') or _('New')

        res = super(StudentAdmission, self).create(vals_list)

        portal_wizard_obj = self.env['portal.wizard']
        for record in res:
            if record.email:  # Ensure email exists
                try:
                    # Attempt to create portal access
                    created_portal_wizard = portal_wizard_obj.create({})
                    portal_wizard_user_obj = self.env['portal.wizard.user']
                    wiz_user_vals = {
                        'wizard_id': created_portal_wizard.id,
                        'partner_id': record.student_id.id,
                        'email': record.student_id.email,
                    }
                    created_portal_wizard_user = portal_wizard_user_obj.create(wiz_user_vals)
                    if created_portal_wizard_user:
                        created_portal_wizard_user.action_grant_access()
                except UserError as e:
                    # Skip granting access if the user already has portal access
                    if 'portal access' in str(e):
                        continue
                    else:
                        raise e

        return res

    def action_enroll(self):
        def local_to_utc_naive(dt):
            user_tz = timezone(self.env.user.tz or 'UTC')
            local_dt = user_tz.localize(dt)
            utc_dt = local_dt.astimezone(UTC)
            return utc_dt.replace(tzinfo=None)

        def float_to_time(hour_float):
            """Convert a float hour to a datetime.time object."""
            hour = int(hour_float)
            minute = round((hour_float - hour) * 60)
            return datetime.strptime(f"{hour}:{minute:02}", "%H:%M").time()

        def next_weekday(start_date, weekday):
            """Get the next occurrence of a specific weekday."""
            days_ahead = (weekday - start_date.weekday() + 7) % 7
            return start_date + timedelta(days=days_ahead)

        # Ensure we have valid weekdays selected
        if not self.weekday_ids or len(self.weekday_ids) < 1:
            raise ValidationError("You must select at least one weekday.")

        start_time = float_to_time(self.start_date)
        end_time = float_to_time(self.end_date)

        start_day = self.start_duration
        weekday_numbers = sorted([int(weekday.id - 1) for weekday in self.weekday_ids])

        weekday_schedule = []
        for _ in range(self.n_of_reservations):
            for weekday in weekday_numbers:
                next_date = next_weekday(start_day, weekday)
                weekday_schedule.append(next_date)
            start_day += timedelta(days=7)

        weekday_schedule.sort()
        for record in self:
            if record.trainer_id:
                for current_date in weekday_schedule[:record.n_of_reservations]:

                    start_datetime = datetime.combine(current_date, start_time)
                    end_datetime = datetime.combine(current_date, end_time)

                    start_datetime_utc = local_to_utc_naive(start_datetime)
                    end_datetime_utc = local_to_utc_naive(end_datetime)

                    overlapping_reservations = self.env['student.reservation'].search([
                        ('trainer_id', '=', record.trainer_id.id),
                        ('start_date', '<=', end_datetime_utc),
                        ('end_date', '>=', start_datetime_utc),
                    ])

                    vip_reservations = overlapping_reservations.filtered(lambda r: r.is_vip)

                    if vip_reservations:
                        return {
                            'type': 'ir.actions.act_window',
                            'res_model': 'reservation.conflict.wizard',
                            'view_mode': 'form',
                            'target': 'new',
                            'context': {
                                'default_trainer_id': record.trainer_id.id,
                                'default_conflict_message': "There is a VIP reservation in this time. Do you want to proceed?",
                                'active_id': record.id,
                            },
                        }

                    if len(overlapping_reservations) >= 5:
                        return {
                            'type': 'ir.actions.act_window',
                            'res_model': 'reservation.conflict.wizard',
                            'view_mode': 'form',
                            'target': 'new',
                            'context': {
                                'default_trainer_id': record.trainer_id.id,
                                'default_conflict_message': f"Trainer {record.trainer_id.name} already has 5 reservations in this time frame. Do you want to proceed?",
                                'active_id': record.id,
                            },
                        }

        # Proceed with enrollment if no conflicts
        self.action_create_reservation_auto_multi()
        self.state = 'enrolled'
        self.student_id.admission_id = self.id

        if self.is_invoiced:
            self.state = 'student'

        template = self.env.ref(
            'bi_sport_center_management.student_admission_enroll_email_template')
        if template:
            template.send_mail(self.id, force_send=True)

    def action_make_student(self):
        if not self.is_invoiced:

            return {
                'name': 'Create Invoice',
                'view_mode': 'form',
                'res_model': 'create.invoice',
                'type': 'ir.actions.act_window',
                'context': self._context,
                'target': 'new',
            }
        if self.is_invoiced:
            self.state = 'student'
            self.student_id.update({'is_student': True})

    def action_create_invoice(self):
        return {
            'name': 'Create Invoice',
            'view_mode': 'form',
            'res_model': 'create.invoice',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
        }

    def action_cancel(self):
        self.ensure_one()
        invoice_ids = self.env['account.move'].search([('invoice_origin', '=', self.name)])
        if len(invoice_ids.ids) == 1:
            invoice = invoice_ids
            invoice.button_cancel()
        self.state = 'cancel'
        self.student_id.update({'is_student': False})
        for reserv in self.reservation_ids:
            if reserv.state != 'finished':
                reserv.unlink()

    def action_cancel_cron(self):
        current_date = datetime.now().date()
        admissions = self.search([])

        for admission in admissions:
            if admission.end_duration:
                end_date = admission.end_duration

                if current_date >= end_date:
                    admission.is_admission_finished = True
                    admission.state = 'cancel'

    def action_new(self):
        self.ensure_one()
        self.state = 'new'

    def action_view_invoice(self):
        self.ensure_one()
        invoice_ids = self.env['account.move'].search([('invoice_origin', '=', self.name)])
        print(invoice_ids)
        if invoice_ids:
            action = {
                'name': _("Admission Invoices"),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'target': 'current',
            }
            if len(invoice_ids.ids) == 1:
                invoice = invoice_ids.ids[0]
                action['res_id'] = invoice
                action['view_mode'] = 'form'
                action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            else:
                action['view_mode'] = 'list,form'
                action['domain'] = [('id', 'in', invoice_ids.ids)]
            return action

    def action_create_reservation(self):
        """Open a new form view for creating a reservation."""
        self.ensure_one()  # Ensure the action is executed on a single record
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Reservation',
            'res_model': 'student.reservation',
            'view_mode': 'form',
            'view_id': self.env.ref('bi_sport_center_management.student_reservation_view_form').id,
            'target': 'new',  # Open in dialog (new form)
            'context': {
                'default_student_id': self.student_id.id,  # Pre-fill student
                'default_admission_id': self.id,  # Link to current admission
                'default_trainer_id': self.trainer_id.id,  # Link to current admission
                'default_sport_id': self.sport_id.id,  # Link to current admission
                'default_level_id': self.level_id.id,  # Link to current admission
            }
        }

    def action_create_reservation_auto_multi(self):
        self.ensure_one()

        # Ensure at least two weekdays are selected
        if not self.weekday_ids or len(self.weekday_ids) < 1:
            raise ValidationError("You must select at least one  weekdays.")

        # Convert float time to datetime.time
        def float_to_time(hour_float):
            hour = int(hour_float)
            minute = round((hour_float - hour) * 100)  # Avoid precision issues
            if minute >= 60:
                raise ValueError("Invalid time format: Minutes cannot exceed 59.")
            return datetime.strptime(f"{hour}:{minute:02}", "%H:%M").time()

        # Calculate the next occurrence of a given weekday
        def next_weekday(current_date, weekday):
            days_ahead = (weekday - current_date.weekday() + 7) % 7
            return current_date + timedelta(days=days_ahead)

        # Convert to UTC and make datetime naive
        def local_to_utc_naive(dt):
            user_tz = timezone(self.env.user.tz or 'UTC')  # User's timezone
            local_dt = user_tz.localize(dt)  # Localize datetime
            utc_dt = local_dt.astimezone(UTC)  # Convert to UTC
            return utc_dt.replace(tzinfo=None)  # Remove timezone info

        start_time = float_to_time(self.start_date)
        end_time = float_to_time(self.end_date)
        start_day = self.start_duration

        weekday_numbers = sorted([int(weekday.id - 1) for weekday in self.weekday_ids])

        # Prepare a queue of dates for selected weekdays
        weekday_schedule = []
        for _ in range(self.n_of_reservations):
            for weekday in weekday_numbers:
                next_date = next_weekday(start_day, weekday)
                weekday_schedule.append(next_date)
            start_day += timedelta(days=7)  # Move to next week

        # Sort schedule to maintain chronological order
        weekday_schedule.sort()

        reservations = []

        # Generate reservations
        for i in range(self.n_of_reservations):
            # Cycle through the selected weekdays
            current_date = weekday_schedule[i]

            start_datetime = datetime.combine(current_date, start_time)
            end_datetime = datetime.combine(current_date, end_time)

            # Convert to UTC and make naive
            start_datetime_utc = local_to_utc_naive(start_datetime)
            end_datetime_utc = local_to_utc_naive(end_datetime)

            reservations.append({
                'student_id': self.student_id.id,
                'admission_id': self.id,
                'trainer_id': self.trainer_id.id,
                'sport_id': self.sport_id.id,
                'level_id': self.level_id.id,
                'start_date': start_datetime_utc,
                'end_date': end_datetime_utc,
                'is_vip': self.is_vip
            })

        # Batch create reservations
        self.env['student.reservation'].create(reservations)
        self.student_id.admission_id = self.id

    def action_view_reservations(self):
        self.ensure_one()
        reservation_ids = self.env['student.reservation'].search([('ref', '=', self.name)])
        if reservation_ids:
            action = {'name': _("Student Reservations"), 'type': 'ir.actions.act_window',
                      'res_model': 'student.reservation', 'target': 'current', 'view_mode': 'list,form',
                      'domain': [('id', 'in', reservation_ids.ids)]}

            return action

    def action_open_renewal_wizard(self):
        """Opens the reservation change wizard."""
        self.ensure_one()  # Ensure only one record is selected
        view_id = self.env.ref('bi_sport_center_management.admission_renewal_wizard_form').id
        context = self.env.context.copy()
        context['active_id'] = self.id
        context['default_weekday_ids'] = self.weekday_ids.ids
        context['default_student_id'] = self.student_id.id
        context['default_sport_id'] = self.sport_id.id
        context['default_level_id'] = self.level_id.id
        context['default_trainer_id'] = self.trainer_id.id
        context['default_is_vip'] = self.is_vip
        context['default_c_level_id'] = self.c_level_id.id
        context['default_start_duration'] = self.end_duration + timedelta(days=1)
        context['default_old_start_duration'] = self.start_duration

        return {
            'name': _('Admission Renewal'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'admission.renewal.wizard',
            'view_id': view_id,
            'context': context,
            'target': 'new',
        }

    def unlink(self):
        for record in self:
            if record.state in ['student', 'enrolled', 'cancel']:
                raise ValidationError(
                    _("You cannot delete an admission after its enrollment."))
        return super(StudentAdmission, self).unlink()
