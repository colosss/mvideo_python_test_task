import random
from ipaddress import IPv4Address

from src.core.domain.models import GeneratedHttpLog

HTTP_METHODS=("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")
HTTP_STATUS_CODES=(200, 201, 204, 301, 400, 401, 403, 404, 409, 422, 500, 502)
URI_TEMPLATES=(
    "/api/users",
    "/api/users/{id}",
    "/api/orders",
    "/api/orders/{id}",
    "/api/products",
    "/api/products/{id}",
    "/api/cart",
    "/api/search?q=item-{id}",
)
MIN_IPV4=int(IPv4Address("1.0.0.1"))
MAX_IPV4=int(IPv4Address("253.255.255.254"))

class RandomHttpLogGenerator:
    def __init__(self, random_source: random.Random|None=None)->None:
        self._random=random_source or random.Random()

    def generate(self)->GeneratedHttpLog:
        item_id=self._random.randint(1,100_000)
        uri_template=self._random.choice(URI_TEMPLATES)
        ip=IPv4Address(self._random.randint(MIN_IPV4, MAX_IPV4))
        return GeneratedHttpLog(
            ip=str(ip),
            method=self._random.choice(HTTP_METHODS),
            uri=uri_template.format(id=item_id),
            status_code=self._random.choice(HTTP_STATUS_CODES)
        )