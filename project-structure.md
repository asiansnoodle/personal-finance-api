personal-finance-api/
├── app/
│   ├── main.py               # FastAPI app entry point
│   ├── config.py             # Settings via pydantic-settings
│   ├── database.py           # SQLAlchemy engine + session
│   ├── models/               # ORM models
│   │   ├── user.py
│   │   ├── account.py
│   │   ├── transaction.py
│   │   └── budget.py
│   ├── schemas/              # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── transaction.py
│   │   ├── budget.py
│   │   └── analytics.py
│   ├── routers/              # One file per resource
│   │   ├── auth.py
│   │   ├── accounts.py
│   │   ├── transactions.py
│   │   ├── budgets.py
│   │   └── analytics.py
│   ├── services/             # Business logic lives here, not in routers
│   │   ├── auth_service.py
│   │   ├── transaction_service.py
│   │   └── analytics_service.py
│   └── dependencies.py       # get_db, get_current_user injection
├── alembic/                  # DB migrations
│   └── versions/
├── tests/
│   ├── conftest.py
│   └── test_transactions.py
├── alembic.ini
├── requirements.txt
├── .env
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md