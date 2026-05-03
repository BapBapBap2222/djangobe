import django_filters
from .models import Property, PropertyType, ListingType, PropertyStatus


class PropertyFilter(django_filters.FilterSet):
    # Lọc theo loại BĐS và hình thức
    property_type = django_filters.ChoiceFilter(choices=PropertyType.choices)
    listing_type  = django_filters.ChoiceFilter(choices=ListingType.choices)
    status        = django_filters.ChoiceFilter(choices=PropertyStatus.choices)

    # Lọc theo giá (khoảng)
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    # Lọc theo diện tích (khoảng)
    area_min = django_filters.NumberFilter(field_name='area', lookup_expr='gte')
    area_max = django_filters.NumberFilter(field_name='area', lookup_expr='lte')

    # Lọc theo địa điểm
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')
    # Backward-compatible alias (old FE used province)
    province = django_filters.CharFilter(field_name='city', lookup_expr='icontains')
    district = django_filters.CharFilter(lookup_expr='icontains')

    # Lọc theo số phòng ngủ (tối thiểu)
    bedrooms_min = django_filters.NumberFilter(field_name='bedrooms', lookup_expr='gte')

    # Tiện ích
    has_parking  = django_filters.BooleanFilter()
    has_pool     = django_filters.BooleanFilter()
    is_furnished = django_filters.BooleanFilter()
    is_featured  = django_filters.BooleanFilter()

    # Lọc theo chủ sở hữu
    owner = django_filters.NumberFilter(field_name='owner__id')

    class Meta:
        model = Property
        fields = [
            'property_type', 'listing_type', 'status',
            'price_min', 'price_max', 'area_min', 'area_max',
            'city', 'province', 'district', 'bedrooms_min',
            'has_parking', 'has_pool', 'is_furnished', 'is_featured', 'owner',
        ]
