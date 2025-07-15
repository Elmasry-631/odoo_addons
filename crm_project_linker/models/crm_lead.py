from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    project_id = fields.Many2one('project.project', string='Related Project')
    sale_order_id = fields.Many2one('sale.order', string='Related Quotation')  # NEW

    def action_open_project(self):
        self.ensure_one()
        if self.project_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.project',
                'view_mode': 'form',
                'res_id': self.project_id.id,
                'target': 'current',
            }
        return False

    def action_create_project(self):
        for lead in self:
            if lead.project_id:
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'project.project',
                    'view_mode': 'form',
                    'res_id': lead.project_id.id,
                }
            project = self.env['project.project'].create({
                'name': lead.name,
                'partner_id': lead.partner_id.id,
                'user_id': lead.user_id.id,
                'crm_lead_id': lead.id,
            })
            lead.project_id = project.id
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.project',
                'view_mode': 'form',
                'res_id': project.id,
            }


class Project(models.Model):
    _inherit = 'project.project'

    crm_lead_id = fields.Many2one('crm.lead', string='CRM Opportunity')
    sale_order_id = fields.Many2one('sale.order', string='Related Quotation')  # NEW
    sale_order_ids = fields.One2many('sale.order', 'project_id', string="Quotations")

    def action_open_crm_lead(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'res_id': self.crm_lead_id.id,
        }

    def action_create_quotation_from_project(self):
        self.ensure_one()

        # ✅ استخدم الكوتيشن لو موجود
        if self.sale_order_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Quotation',
                'res_model': 'sale.order',
                'view_mode': 'form',
                'res_id': self.sale_order_id.id,
                'target': 'current',
            }

        # ✅ أنشئ عرض سعر جديد واربطة بكل الجهات
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'note': f"Quotation for project: {self.name}",
            'project_id': self.id,  # 💥 الربط بالمشروع من جوه عرض السعر
        })

        # ✅ خزن الربط العكسي
        self.sale_order_id = sale_order.id
        if self.crm_lead_id:
            self.crm_lead_id.sale_order_id = sale_order.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotation',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale_order.id,
            'target': 'current',
        }

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_id = fields.Many2one('project.project', string="Project")
