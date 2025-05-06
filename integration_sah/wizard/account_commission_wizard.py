from odoo import models, fields, api
import base64
import io
import pandas as pd
from datetime import datetime

class AccountCommissionWizard(models.TransientModel):
    _name = 'account.commission.wizard'
    _description = 'Wizard d’importation des commissions VDI'

    file = fields.Binary(string="Fichier Excel", required=True)
    filename = fields.Char(string="Nom du fichier")

    def action_import_commissions(self):
        data = base64.b64decode(self.file)
        df = pd.read_excel(io.BytesIO(data))

        # Attendu : colonnes ['Date', 'Montant', 'VDI_ID']
        grouped = df.groupby(df['Date'].dt.to_period('M'))

        journal = self.env['account.journal'].search([('code', '=', 'COMM')], limit=1)
        if not journal:
            raise ValueError("Le journal 'COMM' (commission) n’existe pas.")

        account_622 = self.env['account.account'].search([('code', '=', '622')], limit=1)
        if not account_622:
            raise ValueError("Le compte 622 n’existe pas.")

        for period, group in grouped:
            date = group['Date'].iloc[0].to_pydatetime().replace(day=1)

            # Vérifier si pièce déjà existante
            move_exist = self.env['account.move'].search([
                ('journal_id', '=', journal.id),
                ('date', '>=', date),
                ('date', '<=', date.replace(day=28)),
                ('state', '=', 'draft'),
            ])
            if move_exist:
                continue

            lines = []
            for _, row in group.iterrows():
                vdi = self.env['res.partner'].browse(int(row['VDI_ID']))
                if not vdi.property_account_payable_id:
                    raise ValueError(f"Le fournisseur {vdi.name} n’a pas de compte fournisseur défini.")

                lines.append((0, 0, {
                    'name': 'Commission VDI',
                    'debit': row['Montant'],
                    'credit': 0.0,
                    'account_id': account_622.id,
                }))
                lines.append((0, 0, {
                    'name': f"Commission - {vdi.name}",
                    'debit': 0.0,
                    'credit': row['Montant'],
                    'account_id': vdi.property_account_payable_id.id,
                    'partner_id': vdi.id,
                }))

            self.env['account.move'].create({
                'date': date,
                'journal_id': journal.id,
                'move_type': 'entry',
                'line_ids': lines
            })
