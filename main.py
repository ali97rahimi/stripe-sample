import os
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import stripe

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.get("/redirect-to-checkout")
async def redirect_to_checkout():
    user_id = "my_user_id"
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "T-shirt",
                        },
                        "unit_amount": 2000,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://localhost:8000/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:8000/cancel?session_id={CHECKOUT_SESSION_ID}",
            metadata={"user_id": user_id},
        )
        return RedirectResponse(url=checkout_session.url)
    except Exception as e:
        return {"error": str(e)}


@app.get("/success")
async def success(session_id: str = Query(None)):
    if session_id:
        try:
            # Retrieve the session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            # Get the user_id from the session metadata
            user_id = session.metadata.get("user_id")
            return f"Payment successful! User ID: {user_id}"
        except Exception as e:
            return {"error": str(e)}
    return "Payment successful!"


@app.get("/cancel")
async def cancel(session_id: str = Query(None)):
    if session_id:
        try:
            # Retrieve the session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            # Get the user_id from the session metadata
            user_id = session.metadata.get("user_id")
            return f"Payment canceled! User ID: {user_id}"
        except Exception as e:
            return {"error": str(e)}
    return "Payment canceled!"
