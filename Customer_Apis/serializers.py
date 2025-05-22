from ArenoApp.models import ShopProduct, SellerProfile, ShopCategory, ShopBrand, ArenoHomeAd, ArenoShoppingAd, ArenoRestaurantAd, ArenoBookingAd
from rest_framework import serializers

# All serializers here


# displaying products
class ShopProductsSerializer(serializers.ModelSerializer):
    """
    Serializer for shop products with detailed product information.
    
    Includes all product details such as name, description, price, images, and seller information.
    """
    # check if product seller is verified
    seller_verified = serializers.BooleanField(source='user.sellerprofile.is_verified', default=False)
    # seller details
    seller_id = serializers.CharField(source='user.sellerprofile.id', default="")
    businessname = serializers.CharField(source='user.sellerprofile.businessname', default="Seller Id")
    profileimage = serializers.ImageField(source='user.sellerprofile.profileimage', default="")

    class Meta:
        model = ShopProduct
        fields = '__all__'
        depth = 1  # Include related objects

# displaying all seller products
class SellerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for seller profiles with detailed seller information.
    
    Includes seller details such as business name, contact information, location, and user details.
    """
    class Meta:
        model = SellerProfile
        exclude = ['passwordtoken' ,] 
        depth = 1  # Include related objects

# shop brads
class ShopBrandSerializer(serializers.ModelSerializer):
    """
    Serializer for product brands.
    
    Includes brand name, description, and related information.
    """
    class Meta:
        model = ShopBrand
        fields = '__all__'

# shop brads
class ShopCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for product categories.
    
    Includes category name, description, and related information.
    """
    class Meta:
        model = ShopCategory
        fields = '__all__'

# all Ads
class ArenoHomeAdSerializer(serializers.ModelSerializer):
    """
    Serializer for home page advertisements.
    
    Includes ad title, image, link, and display information.
    """
    class Meta:
        model = ArenoHomeAd
        fields = '__all__'

class ArenoShoppingAdSerializer(serializers.ModelSerializer):
    """
    Serializer for shopping page advertisements.
    
    Includes ad title, image, link, and display information for the shopping section.
    """
    class Meta:
        model = ArenoShoppingAd
        fields = '__all__'

class ArenoRestaurantAdSerializer(serializers.ModelSerializer):
    """
    Serializer for restaurant page advertisements.
    
    Includes ad title, image, link, and display information for the restaurant section.
    """
    class Meta:
        model = ArenoRestaurantAd
        fields = '__all__'

class ArenoBookingAdSerializer(serializers.ModelSerializer):
    """
    Serializer for booking page advertisements.
    
    Includes ad title, image, link, and display information for the booking section.
    """
    class Meta:
        model = ArenoBookingAd
        fields = '__all__'