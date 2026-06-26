"""Seed the database with a demo user, accounts, transactions, and budgets.

Run from the project root:  python seed.py

Idempotent: re-running removes the existing demo user's data and recreates it,
so you can run it as many times as you like (handy for demos / Swagger screenshots).
"""

import random
from datetime import date
from decimal import Decimal

from app.database import SessionLocal
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.services.auth_service import hash_password

# Reproducible data run-to-run
random.seed(42)

DEMO_EMAIL = "demo@financeapi.dev"
DEMO_PASSWORD = "demopass123"

CATEGORIES = [
    "groceries",
    "dining",
    "rent",
    "transportation",
    "entertainment",
    "utilities",
    "shopping",
]

# Realistic (min, max) expense amount ranges per category, and how many
# transactions to generate for each over the month.
CATEGORY_PROFILE = {
    "groceries":      {"range": (25, 120),  "count": 8, "descriptions": ["Whole Foods", "Trader Joe's", "Safeway", "Costco run", "Corner market"]},
    "dining":         {"range": (12, 75),   "count": 7, "descriptions": ["Chipotle", "Thai takeout", "Coffee shop", "Pizza night", "Sushi dinner", "Brunch"]},
    "transportation": {"range": (8, 60),    "count": 5, "descriptions": ["Uber", "Gas station", "Transit pass", "Parking"]},
    "entertainment":  {"range": (10, 50),   "count": 4, "descriptions": ["Netflix", "Movie tickets", "Concert", "Spotify"]},
    "utilities":      {"range": (40, 130),  "count": 3, "descriptions": ["Electric bill", "Internet", "Water bill"]},
    "shopping":       {"range": (20, 200),  "count": 5, "descriptions": ["Amazon order", "New shoes", "Bookstore", "Hardware store"]},
    # rent handled separately as a single fixed monthly charge
}

# Budgets are set intentionally tight in a couple of categories so the variance
# endpoint shows both under-budget and over-budget results.
BUDGETS = {
    "groceries":      Decimal("400.00"),
    "dining":         Decimal("200.00"),   # likely over budget
    "rent":           Decimal("1500.00"),
    "transportation": Decimal("150.00"),
    "entertainment":  Decimal("100.00"),   # likely over budget
    "utilities":      Decimal("250.00"),
    "shopping":       Decimal("300.00"),
}


def money(low: int, high: int) -> Decimal:
    """Random amount in [low, high] with cents, as a Decimal."""
    cents = random.randint(low * 100, high * 100)
    return (Decimal(cents) / Decimal(100)).quantize(Decimal("0.01"))


def clear_existing(db, user: User) -> None:
    """Remove the demo user's transactions, accounts, and budgets (and the user)."""
    account_ids = [a.id for a in db.query(Account).filter(Account.user_id == user.id).all()]
    if account_ids:
        db.query(Transaction).filter(Transaction.account_id.in_(account_ids)).delete(synchronize_session=False)
    db.query(Account).filter(Account.user_id == user.id).delete(synchronize_session=False)
    db.query(Budget).filter(Budget.user_id == user.id).delete(synchronize_session=False)
    db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
    db.commit()


def seed() -> None:
    db = SessionLocal()
    today = date.today()
    # Spread transactions across days already elapsed this month.
    max_day = today.day

    try:
        # Idempotency: wipe any previous demo data
        existing = db.query(User).filter(User.email == DEMO_EMAIL).first()
        if existing:
            clear_existing(db, existing)

        # 1. User
        user = User(
            email=DEMO_EMAIL,
            hashed_password=hash_password(DEMO_PASSWORD),
            full_name="Demo User",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # 2. Accounts
        checking = Account(user_id=user.id, name="Everyday Checking", account_type="checking", balance=Decimal("3200.00"), currency="USD")
        savings = Account(user_id=user.id, name="Rainy Day Savings", account_type="savings", balance=Decimal("12500.00"), currency="USD")
        credit = Account(user_id=user.id, name="Rewards Credit Card", account_type="credit", balance=Decimal("-640.00"), currency="USD")
        db.add_all([checking, savings, credit])
        db.commit()
        db.refresh(checking)
        db.refresh(credit)

        transactions: list[Transaction] = []

        # 3a. Monthly salary income (deposited to checking, early in the month)
        transactions.append(Transaction(
            account_id=checking.id,
            amount=Decimal("4200.00"),
            description="Monthly salary",
            category=None,
            transaction_date=today.replace(day=1),
            is_income=True,
        ))

        # 3b. Rent — single fixed charge from checking
        transactions.append(Transaction(
            account_id=checking.id,
            amount=Decimal("1450.00"),
            description="Apartment rent",
            category="rent",
            transaction_date=today.replace(day=min(3, max_day)),
            is_income=False,
        ))

        # 3c. Spending transactions across categories (charged to the credit card)
        for category, profile in CATEGORY_PROFILE.items():
            low, high = profile["range"]
            for _ in range(profile["count"]):
                transactions.append(Transaction(
                    account_id=credit.id,
                    amount=money(low, high),
                    description=random.choice(profile["descriptions"]),
                    category=category,
                    transaction_date=today.replace(day=random.randint(1, max_day)),
                    is_income=False,
                ))

        db.add_all(transactions)

        # 4. Budgets for the current month/year
        budgets = [
            Budget(
                user_id=user.id,
                category=category,
                monthly_limit=limit,
                month=today.month,
                year=today.year,
            )
            for category, limit in BUDGETS.items()
        ]
        db.add_all(budgets)

        db.commit()

        print("Seed complete.")
        print(f"  User:         {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print(f"  Accounts:     3 (checking, savings, credit)")
        print(f"  Transactions: {len(transactions)} ({today.strftime('%B %Y')})")
        print(f"  Budgets:      {len(budgets)}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
