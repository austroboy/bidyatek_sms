from decimal import Decimal


def check_budget_alerts(budget_category):
    """
    Check if a budget category has crossed alert thresholds.
    Creates BudgetAlert records only once per threshold per category.
    """
    from budget.models import BudgetAlert

    if budget_category.planned_amount <= 0:
        return

    actual = budget_category.get_actual_amount()
    pct = (actual / budget_category.planned_amount) * 100

    thresholds = [
        (Decimal('100'), 'OVERSPEND'),
        (Decimal('100'), 'CRITICAL'),
        (Decimal('80'), 'WARNING'),
    ]

    # Determine which alert type to fire
    alert_type = None
    threshold_pct = Decimal('0')

    if pct > 100:
        alert_type = 'OVERSPEND'
        threshold_pct = Decimal(str(round(pct, 2)))
    elif pct >= 100:
        alert_type = 'CRITICAL'
        threshold_pct = Decimal('100')
    elif pct >= 80:
        alert_type = 'WARNING'
        threshold_pct = Decimal('80')

    if alert_type:
        # Only create if this exact alert_type doesn't already exist
        already_exists = BudgetAlert.objects.filter(
            budget_category=budget_category,
            alert_type=alert_type,
            is_acknowledged=False
        ).exists()

        if not already_exists:
            BudgetAlert.objects.create(
                budget_category=budget_category,
                alert_type=alert_type,
                threshold_percent=threshold_pct,
                actual_at_trigger=actual
            )


def create_monthly_allocations(budget_category):
    """
    Auto-create 12 monthly BudgetMonthlyAllocation rows for a category.
    Uses EQUAL_MONTHLY split or creates 0-amount rows for MANUAL.
    """
    from budget.models import BudgetMonthlyAllocation
    import calendar

    year_start = budget_category.budget_year.year_start
    year_end = budget_category.budget_year.year_end

    # Build list of all months in the budget year
    months = []
    current_year = year_start.year
    current_month = year_start.month

    while True:
        months.append((current_month, current_year))
        if current_year == year_end.year and current_month == year_end.month:
            break
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1

    num_months = len(months)
    if num_months == 0:
        return

    if budget_category.distribution_type == 'EQUAL_MONTHLY' and num_months > 0:
        per_month = round(budget_category.planned_amount / num_months, 2)
        # Give the first month any rounding remainder
        remainder = budget_category.planned_amount - (per_month * num_months)
    else:
        per_month = Decimal('0.00')
        remainder = Decimal('0.00')

    for i, (month, year) in enumerate(months):
        amount = per_month
        if i == 0:
            amount += remainder  # add rounding remainder to first month

        BudgetMonthlyAllocation.objects.get_or_create(
            budget_category=budget_category,
            month=month,
            year=year,
            defaults={'planned_amount': amount, 'actual_amount': Decimal('0.00')}
        )


def redistribute_monthly_allocations(budget_category):
    """
    Redistribute remaining unlocked months equally after a revision.
    Only used when distribution_type = EQUAL_MONTHLY.
    """
    from budget.models import BudgetMonthlyAllocation

    unlocked = budget_category.monthly_allocations.filter(is_locked=False)
    count = unlocked.count()
    if count == 0:
        return

    per_month = round(budget_category.planned_amount / budget_category.monthly_allocations.count(), 2)
    remainder = budget_category.planned_amount - (per_month * count)

    for i, alloc in enumerate(unlocked):
        alloc.planned_amount = per_month + (remainder if i == 0 else Decimal('0.00'))
        alloc.save(update_fields=['planned_amount'])
