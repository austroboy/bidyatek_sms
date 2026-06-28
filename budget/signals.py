from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


def update_budget_actual_for_entry(instance, is_income):
    """
    Called after an IncomeitemList or Expenseitemlist entry is saved/deleted.
    Finds matching BudgetMonthlyAllocation rows and recalculates actual amounts.
    Also triggers alert checks.
    """
    try:
        from budget.models import BudgetCategory, BudgetMonthlyAllocation
        from budget.utils import check_budget_alerts

        if is_income:
            entry_date = instance.income_date
            head_field = {'income_head': instance.incometype_id}
        else:
            entry_date = instance.expense_date
            head_field = {'expense_head': instance.expensetype_id}

        if not entry_date:
            return

        # Find budget categories that cover this entry's date and head
        categories = BudgetCategory.objects.filter(
            budget_year__year_start__lte=entry_date,
            budget_year__year_end__gte=entry_date,
            budget_year__status='ACTIVE',
            **head_field
        )

        for cat in categories:
            # Update the matching monthly allocation
            alloc = BudgetMonthlyAllocation.objects.filter(
                budget_category=cat,
                month=entry_date.month,
                year=entry_date.year
            ).first()

            if alloc:
                alloc.recalculate_actual()
                check_budget_alerts(cat)

    except Exception as e:
        # Never break income/expense saving due to budget errors
        print(f"[Budget Signal Error] {e}")


# ─── Connect to crucial models ────────────────────────────────────────────────

def _on_income_save(sender, instance, **kwargs):
    update_budget_actual_for_entry(instance, is_income=True)


def _on_expense_save(sender, instance, **kwargs):
    update_budget_actual_for_entry(instance, is_income=False)


# Signals are connected in AppConfig.ready() via post_save/post_delete
# We import the crucial models here to connect signals

def connect_signals():
    try:
        from crucial.models import IncomeitemList, Expenseitemlist
        post_save.connect(_on_income_save, sender=IncomeitemList)
        post_delete.connect(_on_income_save, sender=IncomeitemList)
        post_save.connect(_on_expense_save, sender=Expenseitemlist)
        post_delete.connect(_on_expense_save, sender=Expenseitemlist)
    except Exception as e:
        print(f"[Budget] Could not connect signals: {e}")


connect_signals()
