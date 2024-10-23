import psycopg2
import unittest
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from unittest.mock import patch, MagicMock
import json

# Variables de connexion
DB_NAME = "db_athome"
DB_HOST = "db_home"  # Nom du conteneur
DB_USER = "odoo"  # Nom d'utilisateur de la base de données
DB_PASSWORD = "odoo"  # Mot de passe de la base de données

# Connexion globale
connection = None

def createConnection():
    global connection
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST
        )
        print("Connexion établie à la base de données.")
    except Exception as e:
        print(f"Erreur lors de la connexion à la base de données : {e}")

def closeConnection():
    global connection
    if connection:
        connection.close()
        print("Connexion fermée à la base de données.")

def setUpModule():
    """ Fonction appelée avant tous les tests du module. """
    createConnection()

def tearDownModule():
    """ Fonction appelée après tous les tests du module. """
    closeConnection()
@tagged('-at_install', 'post_install')
class TestTarifs(TransactionCase):
    @classmethod
    @patch('requests.post')
    @patch('odoo.addons.integration_sah.models.authentication.AuthenticaionSAH.establish_connection')
    def setUpClass(self, mock_auth, mock_post):
        super(TestTarifs, self).setUpClass()
        mock_auth.return_value = {'Authorization': 'Bearer token'}
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {
            'Id': 9999,
            'Prices': [{'Id': 123456}]  # Ajoutez la structure attendue ici
        })
        self.product_template = self.env['product.template'].create({
            'name': 'Test Product',
            'list_price': 100.0,
            'standard_price': 80.0,
            'taxes_id': self.env['account.tax'].create({'name': 'Tax 20%', 'amount': 20}).ids
        })
        self.pricelist = self.env['product.pricelist'].create({
            'name': 'Test Pricelist',
            'price_list_sah_id': 123456
        })
        self.tarif_vals = {
            'product_tmpl_id': self.product_template.id,
            'pricelist_id': self.pricelist.id,
            'date_start': '2023-01-01',
            'date_end': '2023-12-31',
            'min_quantity': 5,
            'fixed_price': 95.0
        }
        # self.tarif = self.env['product.pricelist.item'].create(self.tarif_vals)
        with patch('requests.put') as mock_put:
            mock_put.return_value = MagicMock(status_code=200, json=lambda: {'RolePrices': [{'Id': 7890}]})
            
            # Créer le tarif ici pour que l'appel à requests.put soit simulé
            self.tarif = self.env['product.pricelist.item'].create(self.tarif_vals)

    @patch('requests.put')
    @patch('requests.get')
    @patch('odoo.addons.integration_sah.models.authentication.AuthenticaionSAH.establish_connection')
    def test_create_tarif(self, mock_auth, mock_get, mock_put):
        mock_auth.return_value = {'Authorization': 'Bearer token'}
        mock_put.return_value = MagicMock(status_code=200, json=lambda: {'RolePrices': [{'Id': 7890}]})

        # Simulate creation
        tarif = self.env['product.pricelist.item'].create(self.tarif_vals)

        # Verify API call was made with the right values
        self.assertEqual(int(tarif.price_sah_id), 7890)
        mock_put.assert_called()
        self.assertEqual(mock_put.call_count, 2)

        # Extract the JSON payload from the PUT request and check it
        payload = mock_put.call_args.kwargs['json']
        self.assertEqual(payload['ProductId'], self.product_template.produit_sah_id)
        self.assertEqual(payload['PriceExclTax'], self.product_template.list_price)

    @patch('requests.put')
    @patch('odoo.addons.integration_sah.models.authentication.AuthenticaionSAH.establish_connection')
    def test_write_tarif(self, mock_auth, mock_put):
        """Test the 'write' method with mocked API calls."""
        mock_auth.return_value = {'Authorization': 'Bearer token'}
        mock_put.return_value = MagicMock(status_code=200, json=lambda: {'RolePrices': [{'Id': 7890}]})
        updated_vals = {'fixed_price': 95.0}
        self.tarif.write(updated_vals)
        mock_put.assert_called_once()
        payload = mock_put.call_args.kwargs['json']
        self.assertEqual(payload['RolePrices'][0]['NewPriceExclTax'], 95.0)

    """ @patch('requests.get')
    @patch('odoo.addons.integration_sah.models.authentication.AuthenticaionSAH.establish_connection')
    def test_recuperation_liste_prices(self, mock_auth, mock_get):
        mock_auth.return_value = {'Authorization': 'Bearer token'}
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {
            'prices': [{'ProductId': 118823, 'PriceExclTax': 100.0, 'PriceInclTax': 120.0}]
        })
        prices = self.tarif.recuperation_liste_prices()
        mock_get.assert_called_once()
        params = mock_get.call_args.kwargs['params']
        self.assertEqual(params['productid'], 118823)
        self.assertIn('prices', prices)
        self.assertEqual(prices['prices'][0]['ProductId'], 118823)"""
    @classmethod 
    def tearDownClass(cls): 
        super(TestTarifs, cls).tearDownClass()