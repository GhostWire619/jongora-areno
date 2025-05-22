from django.shortcuts import get_object_or_404, render
from Customer_Apis.serializers import ShopProductsSerializer, SellerProfileSerializer, ShopBrandSerializer, ShopCategorySerializer, ArenoHomeAdSerializer, ArenoShoppingAdSerializer, ArenoRestaurantAdSerializer, ArenoBookingAdSerializer
from ArenoApp.models import ShopProduct, SellerProfile, ShopProduct, UserRate, Following, ShopBrand, ShopCategory, ArenoHomeAd, ArenoShoppingAd, ArenoRestaurantAd, ArenoBookingAd
from Customer_Apis.querypaginations import *
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.decorators import api_view
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.


# all product list
class ProductsView(ListAPIView):
    
    queryset = ShopProduct.objects.filter(action="Approved").order_by('-pk')
    serializer_class = ShopProductsSerializer
    pagination_class = CustomProductsPagination # custom pagination size
    
    @swagger_auto_schema(
        operation_description="Get list of all approved shop products",
        operation_summary="List all approved products",
        manual_parameters=[
            openapi.Parameter('query', openapi.IN_QUERY, description="Search term for filtering products", type=openapi.TYPE_STRING, required=False),
        ],
        responses={
            200: openapi.Response('OK', ShopProductsSerializer(many=True))
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()

        # Apply search filter if there's a query parameter
        query = self.request.GET.get('query', '').strip()
        if query:
            queryset = queryset.filter(
                Q(user__sellerprofile__businessname__icontains=query) | Q(productname__icontains=query) | 
                Q(productcategory__icontains=query) | Q(productdescription__icontains=query) | Q(productlocation__icontains=query)
            ).distinct()

        return queryset

###SHOPPING###
    
# product detail
class ShopProductDetail(RetrieveAPIView):
    queryset = ShopProduct.objects.filter(action="Approved").order_by('pk')
    serializer_class = ShopProductsSerializer
    lookup_field = "id"

    @swagger_auto_schema(
        operation_description="Get detailed information about a specific product",
        operation_summary="Get product details", 
        responses={
            200: openapi.Response('OK', ShopProductsSerializer),
            404: "Product not found"
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            product = self.get_object()
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except ShopProduct.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        

# related products
class GetRelatedProducts(RetrieveAPIView):
    queryset = ShopProduct.objects.filter(action = "Approved").order_by('-pk')
    serializer_class = ShopProductsSerializer

    @swagger_auto_schema(
        operation_description="Get products related to a specific product by category",
        operation_summary="Get related products",
        responses={
            200: openapi.Response('OK', ShopProductsSerializer(many=True)),
            404: "Product not found"
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        product_id = self.kwargs['product_id']
        return get_object_or_404(ShopProduct, pk = product_id, action = "Approved")
    
    def retrieve(self, request, *args, **kwargs):
        product = self.get_object()
        relatedproducts = ShopProduct.objects.filter(action = "Approved", productcategory = product.productcategory).exclude(pk=product.pk).order_by('?')[:10] #only 10

        productlistserializer = ShopProductsSerializer(relatedproducts, many=True)

        response = {
            "products":productlistserializer.data
        }
        return Response(response, status=status.HTTP_200_OK)

# display all product sellers
class ProductSellers(ListAPIView):
    queryset = SellerProfile.objects.filter(businesstype = 'Shopping', status='Approved').order_by('?')
    serializer_class = SellerProfileSerializer
    pagination_class = CustomSellersPagination

    @swagger_auto_schema(
        operation_description="Get a list of all approved product sellers",
        operation_summary="List all product sellers",
        manual_parameters=[
            openapi.Parameter('query', openapi.IN_QUERY, description="Search term for filtering sellers", type=openapi.TYPE_STRING, required=False),
        ],
        responses={
            200: openapi.Response('OK', SellerProfileSerializer(many=True))
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        query = self.request.GET.get('query', '').strip()
        if query:
            queryset = queryset.filter(
                                    Q(fullname__icontains=query) | Q(businessname__icontains=query) |
                                    Q(email__icontains=query) | Q(location__icontains=query) | Q(bio__icontains=query) 
                                    ).distinct()
        return queryset



# display product seller detail page
class ProductSellerPage(RetrieveAPIView):
    queryset = SellerProfile.objects.filter(businesstype = 'Shopping', status='Approved').order_by('pk')
    serializer_class = SellerProfileSerializer

    @swagger_auto_schema(
        operation_description="Get detailed information about a specific seller",
        operation_summary="Get seller details and statistics",
        responses={
            200: openapi.Response('OK', SellerProfileSerializer),
            404: "Seller not found"
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        user_id = self.kwargs['user_id']
        return get_object_or_404(SellerProfile, pk=user_id, businesstype='Shopping', status='Approved')

    def retrieve(self, request, *args, **kwargs):
        try:
            seller = self.get_object()
            sellerproducts = ShopProduct.objects.filter(user=seller.user, action="Approved").order_by('pk') # get products
            productscount = sellerproducts.count()
            followers = Following.objects.filter(following_user=seller.user).order_by('pk') # get followers instance
            followerscount = followers.count()

            # generate rates
            rates = UserRate.objects.filter(selleruser = seller.user)
            totalrates = rates.count()
            if totalrates > 0:
                totalsum = sum(int(rate.rate) for rate in rates) # sum of all rates
                average = totalsum / totalrates
            else: average = 0

            # serializer data
            sellerdata = SellerProfileSerializer(seller)
            products = ShopProductsSerializer(sellerproducts, many=True)

            response = {
                "seller" : sellerdata.data,
                #"products" : products.data,
                "productscount" : productscount,
                "followerscount" : followerscount,
                "averagerate" : average
            }

            return Response(response, status=status.HTTP_200_OK)
        except SellerProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


# display products of a seller
class SellerProducts(RetrieveAPIView):
    queryset = SellerProfile.objects.filter(businesstype = 'Shopping', status = "Approved").order_by('pk')
    serializer_class = SellerProfileSerializer
    pagination_class = CustomSellerProductsPagination

    @swagger_auto_schema(
        operation_description="Get all products from a specific seller",
        operation_summary="Get seller's products",
        responses={
            200: openapi.Response('OK', ShopProductsSerializer(many=True)),
            404: "Seller not found"
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        user_id = self.kwargs['user_id']
        return get_object_or_404(SellerProfile, pk=user_id, businesstype = 'Shopping', status = "Approved")
    
    def retrieve(self, request, *args, **kwargs):
        try:
            seller = self.get_object()
            products = ShopProduct.objects.filter(user=seller.user, action = "Approved").order_by('-pk')

            # pagination
            paginator = self.pagination_class()
            paginated_products = paginator.paginate_queryset(products, request)

            productserializer = ShopProductsSerializer(paginated_products, many=True)
            response = paginator.get_paginated_response(productserializer.data)

            
            return response
        
        except SellerProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


# get all shopping brands
class ShoppingBrands(ListAPIView):
    queryset = ShopBrand.objects.all().order_by('pk')
    serializer_class = ShopBrandSerializer

    @swagger_auto_schema(
        operation_description="Get list of all shopping brands",
        operation_summary="List all shopping brands",
        responses={
            200: openapi.Response('OK', ShopBrandSerializer(many=True))
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# get all shopping categories
class ShoppingCategories(ListAPIView):
    queryset = ShopCategory.objects.all().order_by('pk')
    serializer_class = ShopCategorySerializer

    @swagger_auto_schema(
        operation_description="Get list of all shopping categories",
        operation_summary="List all shopping categories",
        responses={
            200: openapi.Response('OK', ShopCategorySerializer(many=True))
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

#####END OF SHOPPING#####


#### GETING ALL ADS####

# main home ads
class HomeAds(ListAPIView):
    queryset = ArenoHomeAd.objects.all().order_by('pk')
    serializer_class = ArenoHomeAdSerializer

    @swagger_auto_schema(
        operation_description="Get list of all home advertisements",
        operation_summary="List all home ads",
        responses={
            200: openapi.Response('OK', ArenoHomeAdSerializer(many=True))
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# shopping ads
class ShoppingAds(ListAPIView):
    queryset = ArenoShoppingAd.objects.all().order_by('pk')
    serializer_class = ArenoShoppingAdSerializer

    @swagger_auto_schema(
        operation_description="Get list of all shopping advertisements",
        operation_summary="List all shopping ads",
        responses={
            200: openapi.Response('OK', ArenoShoppingAdSerializer(many=True))
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# restaurant ads
class RestaurantAds(ListAPIView):
    queryset = ArenoRestaurantAd.objects.all().order_by('pk')
    serializer_class = ArenoRestaurantAdSerializer

    @swagger_auto_schema(
        operation_description="Get list of all restaurant advertisements",
        operation_summary="List all restaurant ads",
        responses={
            200: openapi.Response('OK', ArenoRestaurantAdSerializer(many=True))
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# booking ads
class BookingAds(ListAPIView):
    queryset = ArenoBookingAd.objects.all().order_by('pk')
    serializer_class = ArenoBookingAdSerializer

    @swagger_auto_schema(
        operation_description="Get list of all booking advertisements",
        operation_summary="List all booking ads",
        responses={
            200: openapi.Response('OK', ArenoBookingAdSerializer(many=True))
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

### END OF GETTING ADS ####
