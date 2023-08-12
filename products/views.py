from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from products.models import Product


# Create your views here.
@api_view(["GET"])
def products_list_view(request):
    product_list = Product.objects.all()

    return_data = []

    for product in product_list:
        return_data.append(
            {
                "product_id": product.product_id,
                "product_type": product.product_type,
            }
        )

    return Response(data=return_data, status=status.HTTP_200_OK)
