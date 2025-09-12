from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from app_offers.models import Offer, OfferDetail
from app_orders.models import Order
from rest_framework.authtoken.models import Token

from app_auth.models import UserProfile


class OrderTests(APITestCase):

    def setUp(self):
        """ Create Users"""
        # Users
        self.business_user = User.objects.create_user(username="biz", password="pass123")
        self.customer_user = User.objects.create_user(username="cust", password="pass123")

        # Profiles
        self.business_profile = UserProfile.objects.create(user=self.business_user, type="business")
        self.customer_profile = UserProfile.objects.create(user=self.customer_user, type="customer")

        # Token
        self.business_token = Token.objects.create(user=self.business_user)
        self.customer_token = Token.objects.create(user=self.customer_user)

        """ Create Offer """
        self.offer = Offer.objects.create(user=self.business_user, title="Logo Design", description="Desc")
        # and its offerdetails
        OfferDetail.objects.create(
            offer=self.offer, title="Basic Offer", offer_type="basic", price=50, delivery_time_in_days=5, revisions=5
        )
        OfferDetail.objects.create(
            offer=self.offer, title="Standard Offer", offer_type="standard", price=100, delivery_time_in_days=3, revisions=3
        )
        OfferDetail.objects.create(
            offer=self.offer, title="Premium Offer", offer_type="premium", price=200, delivery_time_in_days=1, revisions=2
        )

        """ Create Order """
        self.details = list(self.offer.details.all())
        self.order = Order.objects.create(customer_user = self.customer_user, offer_detail=self.details[2])

        """ APIClient """
        self.client = APIClient()

    def authenticate_user(self, user_type):
        if user_type == "business":
            token = self.business_token
        elif user_type == "customer":
            token = self.customer_token
        else:
            raise ValueError("Unknown user type")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


    """ TESTS ORDERS """
    """ ------------ """

    # GET orders list (valid) - first entry is premium offer
    def test_get_order_list(self):
        self.authenticate_user("customer")
        url = reverse("orders-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], "Premium Offer")
        self.assertEqual(response.data[0]['status'], "in_progress")  # default set?
        self.assertEqual(response.data[0]['customer_user'], self.customer_user.id)


    # CREATE as customer (valid)
    def test_create_order_as_customer(self):
        self.authenticate_user("customer")
        url = reverse("orders-list")
        payload = {
            "offer_detail_id": self.details[1].id
        }
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(response.data['title'], "Standard Offer")
        self.assertEqual(response.data['customer_user'], self.customer_user.id)
        self.assertEqual(response.data['status'], "in_progress")  # default set?


    # CREATE as business (invalid)
    def test_create_order_as_business_fails(self):
        self.authenticate_user("business")
        url = reverse("orders-list")
        payload = {
            "offer_detail_id": self.details[2].id
        }
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), 1) # nothing created


    # PATCH as assigned business (valid)
    def test_patch_order_as_business(self):
        self.authenticate_user("business")
        url = reverse("order-detail", args=[self.order.pk])
        payload = {
            "status": "completed"
        }
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "completed")  # check db


    # PATCH as assigned business (valid)
    def test_patch_order_invalid_status_fails(self):
        self.authenticate_user("business")
        url = reverse("order-detail", args=[self.order.pk])
        payload = {
            "status": "invalid"
        }
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not a valid choice", str(response.data)) 


    # PATCH as customer (invalid)
    def test_patch_order_as_customer_fails(self):
        self.authenticate_user("customer")
        url = reverse("order-detail", args=[self.order.pk])
        payload = {
            "status": "cancelled"
        }
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "in_progress") # status did not change

    # PATCH order, that does no exist (invalid)
    def test_patch_order_not_existing_fails(self):
        self.authenticate_user("business")
        pk = 44
        url = reverse("order-detail", args=[pk])
        payload = {
            "status": "cancelled"
            }
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    # DELETE order as business (owner) (valid)
    def test_delete_order_by_owner(self):
        self.authenticate_user("business")
        url = reverse("order-detail", args=[self.order.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(pk=self.order.pk).exists()) # deleted?


    # DELETE order as customer / other than owner (invalid)
    def test_delete_order_by_other_fails(self):
        self.authenticate_user("customer")
        url = reverse("order-detail", args=[self.order.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Order.objects.filter(pk=self.order.pk).exists()) 