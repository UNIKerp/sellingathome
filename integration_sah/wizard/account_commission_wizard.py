from odoo import models, fields
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
        # Décodage du fichier importé
        data = base64.b64decode(self.file)
        df = pd.read_excel(io.BytesIO(data))

        # Nettoyage des noms de colonnes pour éviter les espaces cachés
        df.columns = df.columns.str.strip()

        # Renommer les colonnes selon le fichier fourni
        df.rename(columns={
            'Identifiant du vendeur': 'VDI_ID',
            'Montant de commissions': 'Montant'
        }, inplace=True)

        # Vérification des colonnes nécessaires
        required_cols = ['Date', 'Montant', 'VDI_ID']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Colonne manquante dans le fichier : {col}")

        # Convertir les formats
        df['Montant'] = df['Montant'].astype(str).str.replace(',', '.').astype(float)
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Date'])  # Supprimer les lignes avec date invalide

        # Regrouper par mois
        grouped = df.groupby(df['Date'].dt.to_period('M'))

        journal = self.env['account.journal'].search([('code', '=', 'COMM')], limit=1)
        if not journal:
            raise ValueError("Le journal 'COMM' (commission) n’existe pas.")

        account_622 = self.env['account.account'].search([('code', '=', '622')], limit=1)
        if not account_622:
            raise ValueError("Le compte 622 n’existe pas.")

        for period, group in grouped:
            date = group['Date'].iloc[0].to_pydatetime().replace(day=1)

            # Vérifier si une pièce existe déjà
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
                vdi_id = int(row['VDI_ID'])
                vdi = self.env['res.partner'].browse(vdi_id)

                if not vdi.exists():
                    raise ValueError(f"Le partenaire avec l’ID {vdi_id} n’existe pas.")
                if not vdi.property_account_payable_id:
                    raise ValueError(f"Le partenaire {vdi.name} n’a pas de compte fournisseur défini.")

                montant = float(row['Montant'])

                lines.append((0, 0, {
                    'name': 'Commission VDI',
                    'debit': montant,
                    'credit': 0.0,
                    'account_id': account_622.id,
                }))
                lines.append((0, 0, {
                    'name': f"Commission - {vdi.name}",
                    'debit': 0.0,
                    'credit': montant,
                    'account_id': vdi.property_account_payable_id.id,
                    'partner_id': vdi.id,
                }))

            self.env['account.move'].create({
                'date': date,
                'journal_id': journal.id,
                'move_type': 'entry',
                'line_ids': lines,
            })


    """def action_import_commissions(self):
        # Décodage du fichier Excel
        data = base64.b64decode(self.file)
        df = pd.read_excel(io.BytesIO(data))

        # Vérification et conversion de la colonne date
        if 'Date de début de période' not in df.columns or 'Montant de commissions' not in df.columns or 'Identifiant du vendeur' not in df.columns:
            raise ValueError("Le fichier doit contenir les colonnes 'Date de début de période', 'Montant de commissions' et 'Identifiant du vendeur'.")

        df['Date de début de période'] = pd.to_datetime(df['Date de début de période'], dayfirst=True, errors='coerce')

        grouped = df.groupby(df['Date de début de période'].dt.to_period('M'))

        journal = self.env['account.journal'].search([('code', '=', 'COMM')], limit=1)
        if not journal:
            raise ValueError("Le journal 'COMM' (commission) n’existe pas.")

        account_622 = self.env['account.account'].search([('code', '=', '622')], limit=1)
        if not account_622:
            raise ValueError("Le compte 622 n’existe pas.")

        for period, group in grouped:
            date = group['Date de début de période'].iloc[0].to_pydatetime().replace(day=1)

            # Vérifie si un move existe déjà
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
                montant = float(str(row['Montant de commissions']).replace(',', '.'))

                vdi = self.env['res.partner'].browse(int(row['VDI_ID']))
                if not vdi.property_account_payable_id:
                    raise ValueError(f"Le fournisseur {vdi.name} n’a pas de compte fournisseur défini.")

                lines.append((0, 0, {
                    'name': 'Commission VDI',
                    'debit': montant,
                    'credit': 0.0,
                    'account_id': account_622.id,
                }))
                lines.append((0, 0, {
                    'name': f"Commission - {vdi.name}",
                    'debit': 0.0,
                    'credit': montant,
                    'account_id': vdi.property_account_payable_id.id,
                    'partner_id': vdi.id,
                }))

            self.env['account.move'].create({
                'date': date,
                'journal_id': journal.id,
                'move_type': 'entry',
                'line_ids': lines
            })"""
