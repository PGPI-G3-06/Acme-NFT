from django.test import TestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase, Client

from .models import Product, Address, Opinion, Complaint, Contact, ProductEntry, Order

from .management.commands.populateDB import Command


def setUpModule():
    print("Setting up module...")

    args = []
    opts = {}

    Command().handle(*args, **opts)

class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        user = User.objects.create_user(username="admin", password="admin")

    def test_login(self):
        response = self.client.post('/login', {'username': 'admin', 'password': 'admin'})
        self.assertEqual(response.status_code, 302)

    def test_signup(self):
        data = {
            'profile_pic': '',
            'username': 'test',
            'password': 'testtest',
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'Test',
        }

        response = self.client.post('/signup', data)
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username='test')

        self.assertEqual(user.username, 'test')
        self.assertEqual(user.email, 'test@test.com')

    def test_signup_negative(self):
        data = {
            'username': '',
            'password': 'test',
            'email': 'test@test.com',
            'first_name': 'test',
            'last_name': 'test',
        }

        response = self.client.post('/signup', data)
        self.assertEqual(response.status_code, 200)


    def test_edit_user(self):
        self.client.post('/login', {'username': 'admin', 'password': 'admin'})

        data = {
            'profile_pic': '',
            'email': 'a@gmail.com',
            'first_name': 'a',
            'last_name': 'a',
            'username': 'admin',
        }

        response = self.client.post('/profile', data)

        user = User.objects.get(username='admin')

        self.assertEqual(str(user.email), 'a@a.com')



class IndexTestCase(TestCase):

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

        user = User.objects.create_user(username="admin", password="admin", is_staff=True)

    def test_index(self):
        response = self.client.get('/', {'curent_page': '0'})
        self.assertEqual(response.status_code, 200)

        products_response = response.context['products']
        products = Product.objects.all()[:10]

        self.assertEqual(len(products_response), len(products))
        self.assertListEqual(list(products_response), list(products))
    
    def test_index_order_collection(self):
        response = self.client.get('/', {'order-by': 'collection', 'curent_page': '0'})
        self.assertEqual(response.status_code, 200)

        products_response = response.context['products']
        products = Product.objects.all().order_by('collection')[:10]


        self.assertTrue(set(products_response) == set(products))


    def test_index_order_author(self):
        response = self.client.get('/', {'order-by': 'author', 'curent_page': '0'})
        self.assertEqual(response.status_code, 200)

        products_response = response.context['products']
        products = Product.objects.all().order_by('author_id')[:10]

        self.assertTrue(set(products_response), set(products))


class ProductTestCase(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)


    def test_product_detail(self):
        product = Product.objects.all()[0]
        response = self.client.get('/product/' + str(product.id))

        product_response = response.context['product']

        self.assertEqual(product_response, product)


class AddressTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        user = User.objects.create_user(username="admin", password="admin")

    def test_new_address(self):
        self.client.login(username='admin', password='admin')

        data = {
            'title': 'test_title',
            'street_name': 'test',
            'number': '2',
            'floor': '2',
            'door': '2',
            'block': '2',
            'city': 'test',
            'code_postal': '14000',
        }

        response = self.client.post('/address/new', data)

        self.assertEqual(response.status_code, 302)

        address = Address.objects.get(street_name='test')

        self.assertEqual(address.code_postal, 14000)

    def test_update_address(self):
        self.client.login(username='admin', password='admin')

        data = {
            'title': 'test_title',
            'street_name': 'test',
            'number': '2',
            'floor': '2',
            'door': '2',
            'block': '2',
            'city': 'test',
            'code_postal': '14000',
        }

        response = self.client.post('/address/new', data)

        self.assertEqual(response.status_code, 302)

        address = Address.objects.get(street_name='test')

        self.assertEqual(address.code_postal, 14000)

        data = {
            'title': 'new_title',
            'street_name': 'test',
            'number': '45',
            'floor': '6',
            'door': '8',
            'block': '2',
            'city': 'test',
            'code_postal': '15000',
        }

        response = self.client.post('/address/update/' + str(address.id), data)

        self.assertEqual(response.status_code, 302)

        address = Address.objects.get(street_name='test')

        self.assertEqual(address.code_postal, 15000)
        self.assertEqual(address.number, 45)
        self.assertEqual(address.floor, 6)
        self.assertEqual(address.door,str(8))




    def test_delete_address(self):
        self.client.login(username='admin', password='admin')

        data = {
            'title': 'test_title',
            'street_name': 'test',
            'number': '2',
            'floor': '2',
            'door': '2',
            'block': '2',
            'city': 'test',
            'code_postal': '14000',
        }

        response = self.client.post('/address/new', data)

        self.assertEqual(response.status_code, 302)

        address = Address.objects.get(street_name='test')

        self.assertEqual(address.code_postal, 14000)

        response = self.client.get('/address/delete/' + str(address.id))

        self.assertEqual(response.status_code, 302)

        self.assertRaises(Address.DoesNotExist, Address.objects.get, street_name='test')

class CustomerServiceTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        user = User.objects.create_user(username="admin", password="admin")

    def test_new_opinion(self):
        self.client.login(username='admin', password='admin')

        data = {
            'title': 'Pruebaaaaa',
            'opinion': 'Pruebaaaaa',
        }

        response = self.client.post('/opinion', data)
        self.assertEqual(response.status_code, 302)

        opinion = Opinion.objects.get(title='Pruebaaaaa')
        self.assertEqual(opinion.title, 'Pruebaaaaa')

    def test_new_complaint(self):
        self.client.login(username='admin', password='admin')

        data = {
            'title': 'Pruebaaaaa',
            'complaint': 'Pruebaaaaa',

        }

        response = self.client.post('/complaint', data)
        self.assertEqual(response.status_code, 302)

        complaint = Complaint.objects.get(title='Pruebaaaaa')
        self.assertEqual(complaint.title, 'Pruebaaaaa')

    def test_new_contact(self):
        self.client.login(username='admin', password='admin')

        data = {
            'name': 'Periquito',
            'email': 'test@test.es',
            'subject': 'Mensaje de prueba',
            'comment': 'Mensaje de prueba',
        }

        response = self.client.post('/contact', data)
        self.assertEqual(response.status_code, 200)

        contact = Contact.objects.get(name='Periquito')
        self.assertEqual(contact.email, 'test@test.es')

class CartTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        user = User.objects.create_user(username="admin", password="admin", email='test@email.com', first_name='test', last_name='test')
        self.client.login(username='admin', password='admin')

    def test_add_cart(self):
        data = {
            'quantity': '1',
        }

        self.client.post('/cart/add/1', data)

        product_cart = ProductEntry.objects.get(product_id=1)

        self.assertEqual(product_cart.quantity, 1)
        self.assertEqual(product_cart.product_id, 1)
        self.assertEqual(product_cart.user.username, 'admin')

        response = self.client.get('/cart', data)

        self.assertEqual(response.status_code, 200)

    def test_delete_cart(self):
        data = {
            'quantity': '1',
        }

        self.client.post('/cart/add/1', data)

        product_cart = ProductEntry.objects.get(product_id=1)

        self.assertEqual(product_cart.quantity, 1)
        self.assertEqual(product_cart.product_id, 1)

        self.client.get('/cart/delete/1')

        self.assertRaises(ProductEntry.DoesNotExist, ProductEntry.objects.get, product_id=1)



    def test_up_quantity_cart(self):
        data = {
            'quantity': '1',
        }

        self.client.post('/cart/add/1', data)

        product_cart = ProductEntry.objects.get(product_id=1)

        self.assertEqual(product_cart.quantity, 1)
        self.assertEqual(product_cart.product_id, 1)

        data = {
            'quantity': '2',
        }

        self.client.post('/cart/update-quantity/1', data , content_type='application/json')

        product_cart = ProductEntry.objects.get(product_id=1)

        self.assertEqual(product_cart.quantity, 2)
        self.assertEqual(product_cart.product_id, 1)


    def test_add_address_in_cart(self):

        data = {
            'title': 'test_name',
            'street_name': 'test',
            'number': '2',
            'floor': '2',
            'door': '2',
            'block': '2',
            'city': 'test',
            'code_postal': '14000',
        }

        self.client.post('/cart/add-address', data)

        address = Address.objects.get(street_name='test')

        self.assertEqual(address.code_postal, 14000)

    def test_payment(self):
        data = {
            'quantity': '1',
        }

        self.client.post('/cart/add/1', data)

        product_cart = ProductEntry.objects.get(product_id=1)

        self.assertEqual(product_cart.quantity, 1)
        self.assertEqual(product_cart.product_id, 1)

        data = {
            'products': '3',
            'payment_method': 'transferencia',
            'address': 'test',
            'name': 'test_name',
            'email': 'test_email@email.com'

        }

        self.client.post('/cart/resueme/pay', data)

        order = Order.objects.get(pk=1)


        self.assertEqual(order.productentry_set.all()[0].id, 3)
        self.assertEqual(order.payment_method, 'TRANSFERENCIA')


# class SeleniumNavigationTest(TestCase):

#     def setUp(self):
        
#         options = webdriver.ChromeOptions()
#         options.headless = False
#         self.driver = webdriver.Chrome(options=options)
#         self.driver.get("http://localhost:8000/")
        
    
#     def tearDown(self):
#         self.driver.quit()

#     def test_navigation(self):
            
#             # Crear usuario
            
#             register_button = self.driver.find_element(by=By.CSS_SELECTOR, value="#navbarToggler > div.d-flex.justify-content-end > ul > div > li:nth-child(1) > button")
#             register_button.click()
            
            
