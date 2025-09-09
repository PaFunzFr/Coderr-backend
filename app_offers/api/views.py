from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from django_filters.rest_framework import DjangoFilterBackend

from django.db.models import Min

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .paginations import LargeResultsSetPagination
from .filters import OfferFilter
from app_offers.models import Offer, OfferDetail
from .serializers import OfferCreateUpdateSerializer, OfferDetailNestedDetailSerializer, OfferListSerializer
from .permissions import IsAssignedBusinessOrAdmin,IsBusinessUser


def add_min_fields_to_offer():
    """
    Annotates Offer queryset with minimum price and minimum delivery time
    from related OfferDetails.
    """
    return Offer.objects.all().annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )


@extend_schema(
    description="List all offers or create a new offer. Supports filtering, searching, ordering, and pagination.",
    responses={
        200: OpenApiResponse(response=OfferListSerializer, description="List of offers with minimum price and delivery time."),
        201: OpenApiResponse(response=OfferCreateUpdateSerializer, description="Offer successfully created.")
    }
)
class OffersListCreateView(generics.ListCreateAPIView):
    """
    GET: List all offers with optional filters, search, and ordering.
    POST: Create a new offer (Business users only).
    """
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']
    filterset_class = OfferFilter
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        """Return queryset with annotated min_price and min_delivery_time."""
        return add_min_fields_to_offer()
    
    def get_serializer_class(self):
        """Select serializer based on HTTP method."""
        if self.request.method == "POST":
            return OfferCreateUpdateSerializer
        return OfferListSerializer
    
    def get_permissions(self):
        """Assign permissions based on request method."""
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsBusinessUser()]


@extend_schema(
    description="Retrieve, update, or delete a specific offer.",
    responses={
        200: OpenApiResponse(response=OfferListSerializer, description="Detailed offer information."),
        204: OpenApiResponse(description="Offer deleted successfully."),
        403: OpenApiResponse(description="Permission denied.")
    }
)
class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve offer details.
    PUT/PATCH: Update offer (assigned business or admin only).
    DELETE: Delete offer (assigned business or admin only).
    """

    def get_queryset(self):
        """Return queryset with annotated min_price and min_delivery_time."""
        return add_min_fields_to_offer()
    
    def get_serializer_class(self):
        """Select serializer based on HTTP method."""
        if self.request.method in ["PUT", "PATCH"]:
            return OfferCreateUpdateSerializer
        return OfferListSerializer
    
    def get_permissions(self):
        """Assign permissions based on request method."""
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAssignedBusinessOrAdmin()]


@extend_schema(
    description="Retrieve detailed information of a specific OfferDetail.",
    responses={
        200: OpenApiResponse(response=OfferDetailNestedDetailSerializer, description="Detailed offer detail information."),
        403: OpenApiResponse(description="Permission denied.")
    }
)
class OfferDetailsDetailView(generics.RetrieveAPIView):
    """
    GET: Retrieve detailed information for a single OfferDetail.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailNestedDetailSerializer
    permission_classes = [IsAuthenticated]