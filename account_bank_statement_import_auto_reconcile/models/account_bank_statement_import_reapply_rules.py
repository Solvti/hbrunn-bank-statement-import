# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError


class AccountBankStatementImportReapplyRules(models.TransientModel):
    _inherit = 'account.bank.statement.import'
    _name = 'account.bank.statement.import.reapply.rules'

    data_file = fields.Binary(required=False)

    @api.multi
    def action_reapply_rules(self):
        statements = self.env['account.bank.statement'].browse(
            self.env.context.get('active_ids', [])
        )
        journal = statements.mapped('journal_id')
        if len(journal) != 1:
            raise UserError(_(
                'You can only reapply rules on statements with the same '
                'journal!'
            ))

        reconcile_rules = journal.statement_import_auto_reconcile_rule_ids\
            .get_rules()

        for line in self.env['account.bank.statement.line'].search([
                ('statement_id', 'in', statements.ids),
                ('journal_entry_ids', '=', False),
        ]):
            for rule in reconcile_rules:
                if rule.reconcile(line):
                    break
        return {'type': 'ir.actions.act_window_close'}
