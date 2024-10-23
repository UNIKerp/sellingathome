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
    @patch('requests.get')  # Add this line to mock the GET request
    @patch('requests.post')
    @patch('odoo.addons.integration_sah.models.authentication.AuthenticaionSAH.establish_connection')
    def setUpClass(cls, mock_auth, mock_post, mock_get):
        super(TestTarifs, cls).setUpClass()

        # Mock GET response with correct structure
        mock_get.return_value = MagicMock(status_code=200, json=lambda: [
            {
                "Id":1,
                "Reference": 'UUUUUUUU',
                "ParentCategoryId": 1,
                "IsPublished": True,
                "CategoryLangs": [
                    {"Name": 'mor', "Description": 'None', "ISOValue": "fr"}
                ]
            }
        ])

        # Existing POST mock and other setup logic...
        mock_auth.return_value = {'Authorization': 'Bearer token'}
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {
            'Id': 9999,
            'Prices': [{'Id': 118840}]
        })

        # Your product and pricelist creation logic...
        cls.product_template = cls.env['product.template'].create({
            'name': 'Test Product',
            'list_price': 100.0,
            'standard_price': 80.0,
            'taxes_id': cls.env['account.tax'].create({'name': 'Tax 20%', 'amount': 20}).ids
        })
        cls.pricelist = cls.env['product.pricelist'].create({
            'name': 'Test Pricelist',
            'price_list_sah_id': 118840
        })
        cls.tarif_vals = {
            'product_tmpl_id': cls.product_template.id,
            'pricelist_id': cls.pricelist.id,
            'date_start': '2023-01-01',
            'date_end': '2023-12-31',
            'min_quantity': 5,
            'fixed_price': 95.0
        }
        with patch('requests.put') as mock_put:
            mock_put.return_value = MagicMock(status_code=200, json=lambda: {'RolePrices': [{'Id': 7890}]})
            
            # Creating the tariff
            cls.tarif = cls.env['product.pricelist.item'].create(cls.tarif_vals)

    @patch('requests.put')
    @patch('requests.get')
    @patch('odoo.addons.integration_sah.models.authentication.AuthenticaionSAH.establish_connection')
    def test_create_tarif(self, mock_auth, mock_get, mock_put):
        mock_auth.return_value = {'Authorization': 'Bearer token'}
        
        # Ensure that mock_put returns the correct structure (adjusted)
        mock_put.return_value = MagicMock(status_code=200, json=lambda: {
            'ProductId': 118838,
            'TwoLetterISOCode': 'FR',
            'PriceExclTax': 100.0,
            'PriceInclTax': 120.0,
            'ProductCost': 80.0,
            'RolePrices': [
                {
                    'CustomerRoleId': 1,
                    'Quantity': 5,
                    'NewPriceExclTax': 95.0,
                    'StartDate': '2023-01-01T00:00:00.000000+02:00',
                    'EndDate': '2023-12-31T00:00:00.000000+02:00'
                }
            ]
        })

        # Simulate creation
        tarif = self.env['product.pricelist.item'].create(self.tarif_vals)

        # Verify API call was made with the right values
        mock_put.assert_called()
        self.assertEqual(mock_put.call_count, 1)
        payload = mock_put.call_args.kwargs['json']

        # Assert against 'RolePrices' instead of 'Prices'
        self.assertIn('RolePrices', payload, "'RolePrices' key missing in the payload")

        # Verify the price in 'RolePrices' matches the expected value
        self.assertEqual(payload['RolePrices'][0]['NewPriceExclTax'], 95.0)

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

    @classmethod 
    def tearDownClass(cls): 
        super(TestTarifs, cls).tearDownClass()
