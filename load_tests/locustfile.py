import os
import random

from locust import HttpUser, between, events, task

HTTP_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")
HTTP_STATUS_CODES = (200, 201, 204, 301, 400, 401, 403, 404, 409, 422, 500, 502)
URI_TEMPLATES = (
    "/api/users",
    "/api/users/{id}",
    "/api/orders",
    "/api/orders/{id}",
    "/api/products",
    "/api/products/{id}",
    "/api/cart",
    "/api/search?q=item-{id}",
)


def _random_ip() -> str:
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def _random_log_line() -> str:
    item_id = random.randint(1, 100_000)
    uri = random.choice(URI_TEMPLATES).format(id=item_id)
    return " ".join(
        (
            _random_ip(),
            random.choice(HTTP_METHODS),
            uri,
            str(random.choice(HTTP_STATUS_CODES)),
        )
    )


class MVideoHttpLogUser(HttpUser):
    wait_time = between(0.05, 0.5)

    def on_start(self) -> None:
        self.client.get("/health", name="GET /health")

    @task(6)
    def create_log(self) -> None:
        with self.client.post(
            "/api/data",
            json={"log": _random_log_line()},
            name="POST /api/data",
            catch_response=True,
        ) as response:
            if response.status_code != 201:
                response.failure(f"Expected 201, got {response.status_code}")
                return

            payload = response.json()
            if "id" not in payload or "created" not in payload:
                response.failure("Response does not contain id/created")

    @task(3)
    def list_logs(self) -> None:
        self.client.get(
            "/api/data",
            params={
                "limit": random.choice((10, 25, 50)),
                "offset": 0,
                "order": random.choice(("asc", "desc")),
            },
            name="GET /api/data",
        )

    @task(1)
    def get_stats(self) -> None:
        self.client.get("/api/stats", name="GET /api/stats")

    @task(1)
    def health(self) -> None:
        self.client.get("/health", name="GET /health")


@events.quitting.add_listener
def check_thresholds(environment, **kwargs) -> None:
    stats = environment.stats.total
    max_fail_ratio = float(os.getenv("LOCUST_MAX_FAIL_RATIO", "0.02"))
    max_p95_ms = float(os.getenv("LOCUST_MAX_P95_MS", "1000"))

    if stats.num_requests == 0:
        print("Locust did not execute any requests")
        environment.process_exit_code = 1
        return

    p95_ms = stats.get_response_time_percentile(0.95)
    print(
        "Load test summary: "
        f"requests={stats.num_requests}, "
        f"fail_ratio={stats.fail_ratio:.4f}, "
        f"p95_ms={p95_ms:.2f}"
    )

    if stats.fail_ratio > max_fail_ratio:
        print(
            f"Fail ratio {stats.fail_ratio:.4f} is higher than "
            f"LOCUST_MAX_FAIL_RATIO={max_fail_ratio}"
        )
        environment.process_exit_code = 1
        return

    if p95_ms > max_p95_ms:
        print(f"P95 {p95_ms:.2f}ms is higher than LOCUST_MAX_P95_MS={max_p95_ms}")
        environment.process_exit_code = 1
