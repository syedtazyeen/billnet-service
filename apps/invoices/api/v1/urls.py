"""Users API v1 URLs"""

from rest_framework.routers import SimpleRouter
from apps.invoices.api.v1.views import InvoiceViewSet

router = SimpleRouter()
router.register("", InvoiceViewSet, basename="invoice")
urlpatterns = router.urls


__all__ = ["urlpatterns"]
