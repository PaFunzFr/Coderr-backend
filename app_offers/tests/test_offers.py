from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from app_offers.models import Offer, OfferDetail
from rest_framework.authtoken.models import Token

from app_auth.models import UserProfile


class OfferTests(APITestCase):

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

        # Single APIClient
        self.client = APIClient()


    def authenticate_user(self, user_type):
        if user_type == "business":
            token = self.business_token
        elif user_type == "customer":
            token = self.customer_token
        else:
            raise ValueError("Unknown user type")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


    """ TESTS OFFERS """
    """ ------------ """

    # GET offer_list (valid) - do min_price & min_delivery_time exist?
    def test_get_offer_list(self):
        url = reverse("offers-list")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)  # Pagination active?
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["min_price"], "50.00")
        self.assertEqual(response.data["results"][0]["min_delivery_time"], 1)
        self.assertEqual(response.data["results"][0]["user"], self.business_user.id) # valid owner?


    # CREATE as business (valid)
    def test_create_offer_as_business(self):
        self.authenticate_user("business")
        url = reverse("offers-list")
        payload = {
            "title": "New Offer",
            "description": "Desc",
            "details": [
                {"title": "Basic", "offer_type": "basic", "price": 10, "delivery_time_in_days": 7, "revisions": 2},
                {"title": "Standard", "offer_type": "standard", "price": 20, "delivery_time_in_days": 5, "revisions": 5},
                {"title": "Premium", "offer_type": "premium", "price": 30, "delivery_time_in_days": 3, "revisions": 3},
            ]
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 2)

        new_offer = Offer.objects.latest("id")
        self.assertEqual(new_offer.user, self.business_user)
        self.assertEqual(new_offer.details.count(), 3)


    # CREATE as customer (invalid)
    def test_create_offer_as_customer_forbidden(self):
        self.authenticate_user("customer")
        url = reverse("offers-list")
        payload = {
            "title": "Invalid",
            "description": "X",
            "details": [
                {"title": "Basic", "offer_type": "basic", "price": 10, "delivery_time_in_days": 7, "revisions": 2},
                {"title": "Standard", "offer_type": "standard", "price": 20, "delivery_time_in_days": 5, "revisions": 5},
                {"title": "Premium", "offer_type": "premium", "price": 30, "delivery_time_in_days": 3, "revisions": 3},
            ]
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Offer.objects.count(), 1) # nothing created


    # CREATE with less than 3 details (invalid)
    def test_create_offer_with_less_than_3_details_fails(self):
        self.authenticate_user("business")
        url = reverse("offers-list")
        payload = {
            "title": "Incomplete Offer",
            "description": "Desc",
            "details": [  # only 2 Details instead of 3
                {"title": "Basic", "offer_type": "basic", "price": 10, "delivery_time_in_days": 5},
                {"title": "Standard", "offer_type": "standard", "price": 20, "delivery_time_in_days": 3},
            ]
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Details must contain exactly 3 items (basic, standard, premium).",
            str(response.data)
        )
        self.assertEqual(Offer.objects.count(), 1)


    # CREATE with missing offer_type (invalid)
    def test_create_offer_missing_offer_type_fails(self):
        self.authenticate_user("business")
        url = reverse("offers-list")
        payload = {
            "title": "Incomplete",
            "description": "Desc",
            "details": [
                {"title": "Basic without type"},
                {"title": "Standard without type"},
                {"title": "Premium without type"},
            ]
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field is required.",str(response.data))
        self.assertEqual(Offer.objects.count(), 1)


    # PATCH with invalid offerdetail offer_type (invalid)
    def test_patch_offer_invalid_offer_type_fails(self):
        self.authenticate_user("business")
        url =  reverse("offer-detail", args=[self.offer.pk])
        payload = {
            "details": [
                {"title": "Basic", "offer_type": "invalid", "price": 10, "delivery_time_in_days": 7, "revisions": 2},
            ]
        }
        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not a valid choice",str(response.data))


    # DELETE offer by its owner (valid)
    def test_delete_offer_by_owner(self):
        self.authenticate_user("business")
        url =  reverse("offer-detail", args=[self.offer.pk])
        response = self.client.delete(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(pk=self.offer.pk).exists()) 