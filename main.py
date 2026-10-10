import os
from collections import defaultdict

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any


app = FastAPI()

# Allow the assignment page to call our API from a browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyticsRequest(BaseModel):
    events: list[dict[str, Any]]


@app.get("/")
def home():
    return {"message": "Q7 Analytics API is running"}


@app.post("/analytics")
def analytics(
    request: AnalyticsRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    expected_key = os.environ.get("APP_API_KEY")

    if not expected_key or x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    events = request.events
    user_totals = defaultdict(float)

    for event in events:
        user = event.get("user")
        amount = event.get("amount", 0)

        if user is None:
            raise HTTPException(
                status_code=400,
                detail="Each event must contain a user"
            )

        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise HTTPException(
                status_code=400,
                detail="Each event must contain a numeric amount"
            )

        if amount > 0:
            user_totals[user] += amount

    top_user = (
        max(user_totals, key=user_totals.get)
        if user_totals
        else None
    )

    return {
        "email": os.environ.get(
            "USER_EMAIL",
            "23f2004679@ds.study.iitm.ac.in"
        ),
        "total_events": len(events),
        "unique_users": len({event.get("user") for event in events}),
        "revenue": sum(
            event.get("amount", 0)
            for event in events
            if event.get("amount", 0) > 0
        ),
        "top_user": top_user,
    }
