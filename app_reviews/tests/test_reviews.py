from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from app_auth.models import UserProfile
from app_reviews.models import Review

class ReviewTests(APITestCase):

    def setUp(self):
        """ Users, Profiles, Tokens """
        self.business_user = User.objects.create_user(username="biz", password="pass123")
        self.customer_user = User.objects.create_user(username="cust", password="pass123")

        self.business_profile = UserProfile.objects.create(user=self.business_user, type="business")
        self.customer_profile = UserProfile.objects.create(user=self.customer_user, type="customer")

        self.business_token = Token.objects.create(user=self.business_user)
        self.customer_token = Token.objects.create(user=self.customer_user)

        """ Existing Review """
        self.review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=5,
            description="Excellent service!"
        )

        self.client = APIClient()

    def authenticate_user(self, user_type):
        if user_type == "business":
            token = self.business_token
        elif user_type == "customer":
            token = self.customer_token
        else:
            raise ValueError("Unknown user type")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


    """ TESTS REVIEWS """
    """ ------------- """

    # GET review list (valid)
    def test_get_review_list(self):
        self.authenticate_user("customer")
        url = reverse("review-list")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['rating'], 5)
        self.assertEqual(response.data[0]['description'], "Excellent service!")
        self.assertEqual(response.data[0]['reviewer'], self.customer_user.id)
        self.assertEqual(response.data[0]['business_user'], self.business_user.id)


    # POST review as customer (duplicate) (valid)
    def test_create_review_duplicate(self):
        self.authenticate_user("customer")
        url = reverse("review-list")
        payload = {
            "business_user": self.business_user.id,
            "rating": 4,
            "description": "Good job"
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 1)
        self.assertIn(
            "You have already reviewed this business.",
            str(response.data)
        )


    # POST review as business (invalid)
    def test_create_review_as_business_fails(self):
        self.authenticate_user("business")
        url = reverse("review-list")
        payload = {
            "business_user": self.business_user.id,
            "rating": 4,
            "description": "Trying to review self"
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), 1)


    # PATCH review as reviewer (valid)
    def test_patch_review_as_reviewer(self):
        self.authenticate_user("customer")
        url = reverse("review-detail", args=[self.review.pk])
        payload = {"rating": 3, "description": "Changed mind"}
        response = self.client.patch(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 3)
        self.assertEqual(self.review.description, "Changed mind")


    # PATCH review as other user (invalid)
    def test_patch_review_as_other_user_fails(self):
        self.authenticate_user("business")
        url = reverse("review-detail", args=[self.review.pk])
        payload = {"rating": 1}
        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    # PATCH invalid rating (invalid)
    def test_patch_review_invalid_rating_fails(self):
        self.authenticate_user("customer")
        url = reverse("review-detail", args=[self.review.pk])
        payload = {"rating": 10}  # max is 5
        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    # DELETE review as reviewer (valid)
    def test_delete_review_as_reviewer(self):
        self.authenticate_user("customer")
        url = reverse("review-detail", args=[self.review.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())


    # DELETE review as other user (invalid)
    def test_delete_review_as_other_user_fails(self):
        self.authenticate_user("business")
        url = reverse("review-detail", args=[self.review.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Review.objects.filter(pk=self.review.pk).exists())