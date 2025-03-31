import json
import os
import threading
from typing import Optional

from quart import Quart, Response


class HealthExtension:
    def __init__(self, app: Optional[Quart] = None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Quart) -> None:
        @app.route("/health")
        async def get_health_info() -> Response:
            return Response(
                json.dumps({"pid": os.getpid(), "status": "ok", "version": app.config.get("API_VERSION")}),
                status=200,
                content_type="application/json",
            )

        @app.route("/threads")
        async def get_threads_info() -> Response:
            num_threads = threading.active_count()
            threads = threading.enumerate()

            thread_list = []
            for thread in threads:
                thread_name = thread.name
                thread_id = thread.ident
                is_alive = thread.is_alive()

                thread_list.append(
                    {
                        "name": thread_name,
                        "id": thread_id,
                        "is_alive": is_alive,
                    }
                )

            return Response(
                json.dumps({"pid": os.getpid(), "thread_num": num_threads, "threads": thread_list}),
                status=200,
                content_type="application/json",
            )


health_extn = HealthExtension()
