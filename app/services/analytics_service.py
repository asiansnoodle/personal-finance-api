from decimal import Decimal
from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.budget import Budget
from app.schemas.analytics import CategorySpend, SpendSummary, BudgetVariance


def _expense_rows_by_category(db: Session, user_id: int, month: int, year: int):
    """Expenses for the user in the given month/year, grouped by category.

    Returns rows with labelled columns: row.category, row.total, row.count.
    Shared by both analytics functions.
    """
    return (
        db.query(
            Transaction.category.label("category"),
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count"),
        )
        .join(Account)
        .filter(
            Account.user_id == user_id,
            Transaction.is_income.is_(False),
            extract("month", Transaction.transaction_date) == month,
            extract("year", Transaction.transaction_date) == year,
        )
        .group_by(Transaction.category)
        .all()
    )


def get_spend_summary(db: Session, user_id: int, month: int, year: int) -> SpendSummary:
    spend_rows = _expense_rows_by_category(db, user_id, month, year)

    # Total expenses for the month = sum of every category's total.
    total_spend = sum((row.total for row in spend_rows), Decimal("0"))

    # Total income is a single value (no grouping). .scalar() returns one value
    # or None when there were no income rows, so default to 0.
    total_income = (
        db.query(func.sum(Transaction.amount))
        .join(Account)
        .filter(
            Account.user_id == user_id,
            Transaction.is_income.is_(True),
            extract("month", Transaction.transaction_date) == month,
            extract("year", Transaction.transaction_date) == year,
        )
        .scalar()
    ) or Decimal("0")

    by_category = [
        CategorySpend(
            category=row.category or "uncategorized",
            total=row.total,
            transaction_count=row.count,
            # Guard divide-by-zero when there's no spend at all this month.
            percentage=float(row.total / total_spend * 100) if total_spend else 0.0,
        )
        for row in spend_rows
    ]

    return SpendSummary(
        month=month,
        year=year,
        total_spend=total_spend,
        total_income=total_income,
        net=total_income - total_spend,
        by_category=by_category,
    )


def get_budget_variance(db: Session, user_id: int, month: int, year: int) -> list[BudgetVariance]:
    budgets = (
        db.query(Budget)
        .filter(
            Budget.user_id == user_id,
            Budget.month == month,
            Budget.year == year,
        )
        .all()
    )

    # Actual spend per category, as an O(1) lookup. A budgeted category with no
    # transactions simply won't appear here and falls back to 0 via .get().
    spend_rows = _expense_rows_by_category(db, user_id, month, year)
    actual_by_category = {row.category: row.total for row in spend_rows}

    variances = []
    for budget in budgets:
        actual = actual_by_category.get(budget.category, Decimal("0"))
        variances.append(
            BudgetVariance(
                category=budget.category,
                budgeted=budget.monthly_limit,
                actual=actual,
                # Positive variance = under budget, negative = over.
                variance=budget.monthly_limit - actual,
                percentage_used=(
                    float(actual / budget.monthly_limit * 100)
                    if budget.monthly_limit
                    else 0.0
                ),
            )
        )

    return variances
