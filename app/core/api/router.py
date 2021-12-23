from rest_framework import routers
from core.api.viewset import CardViewSet, UserViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

route_list = [
    (r'users', UserViewSet),
    (r'cards', CardViewSet),
    ]

[router.register(route[0], route[1]) for route in route_list]
