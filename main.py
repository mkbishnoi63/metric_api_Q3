import time
import uuid

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


EMAIL = "24f2004796@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-sxjcnu.example.com"


api = FastAPI()


@api.get("/stats")
async def get_stats(values: str = Query(...)):
    try:
        numbers = [int(v.strip()) for v in values.split(",")]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="values must contain comma-separated integers",
        )

    return {
        "email": EMAIL,
        "count": len(numbers),
        "sum": sum(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "mean": sum(numbers) / len(numbers),
    }


cors_app = CORSMiddleware(
    app=api,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


class RequestHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                elapsed = time.perf_counter() - start
                headers = list(message.get("headers", []))
                headers.extend([
                    (b"x-request-id", request_id.encode()),
                    (b"x-process-time", f"{elapsed:.6f}".encode()),
                ])
                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_with_headers)


app = RequestHeadersMiddleware(cors_app)
