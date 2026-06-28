from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from decimal import Decimal


class BudgetYear(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('ARCHIVED', 'Archived'),
    ]

    title = models.CharField(max_length=150)
    year_start = models.DateField()
    year_end = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        'user.StaffProfile', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_budgets'
    )
    approved_by = models.ForeignKey(
        'user.StaffProfile', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_budgets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year_start']
        verbose_name = 'Budget Year'
        verbose_name_plural = 'Budget Years'

    def __str__(self):
        return f"{self.title} ({self.status})"

    def clean(self):
        if self.year_start and self.year_end:
            if self.year_start >= self.year_end:
                raise ValidationError("Year start must be before year end.")

    @property
    def total_income_budget(self):
        return self.categories.filter(category_type='INCOME').aggregate(
            total=Sum('planned_amount'))['total'] or Decimal('0.00')

    @property
    def total_expense_budget(self):
        return self.categories.filter(category_type='EXPENSE').aggregate(
            total=Sum('planned_amount'))['total'] or Decimal('0.00')

    @property
    def total_actual_income(self):
        from crucial.models import IncomeitemList
        return IncomeitemList.objects.filter(
            income_date__gte=self.year_start,
            income_date__lte=self.year_end
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    @property
    def total_actual_expense(self):
        from crucial.models import Expenseitemlist
        return Expenseitemlist.objects.filter(
            expense_date__gte=self.year_start,
            expense_date__lte=self.year_end
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    @property
    def net_budget(self):
        return self.total_income_budget - self.total_expense_budget

    @property
    def net_actual(self):
        return self.total_actual_income - self.total_actual_expense

    @property
    def income_usage_percent(self):
        if self.total_income_budget > 0:
            return round((self.total_actual_income / self.total_income_budget) * 100, 1)
        return 0

    @property
    def expense_usage_percent(self):
        if self.total_expense_budget > 0:
            return round((self.total_actual_expense / self.total_expense_budget) * 100, 1)
        return 0

    @property
    def unacknowledged_alerts_count(self):
        return BudgetAlert.objects.filter(
            budget_category__budget_year=self,
            is_acknowledged=False
        ).count()


class BudgetCategory(models.Model):
    CATEGORY_TYPE_CHOICES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]
    DISTRIBUTION_CHOICES = [
        ('EQUAL_MONTHLY', 'Equal Monthly'),
        ('MANUAL', 'Manual'),
    ]

    budget_year = models.ForeignKey(
        BudgetYear, on_delete=models.CASCADE, related_name='categories'
    )
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPE_CHOICES)
    income_head = models.ForeignKey(
        'crucial.IncomeHead', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='budget_categories'
    )
    expense_head = models.ForeignKey(
        'crucial.ExpenseHead', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='budget_categories'
    )
    planned_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    distribution_type = models.CharField(
        max_length=15, choices=DISTRIBUTION_CHOICES, default='EQUAL_MONTHLY'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Budget Category'
        verbose_name_plural = 'Budget Categories'

    def __str__(self):
        head = self.income_head or self.expense_head
        return f"{self.budget_year.title} - {head}"

    def clean(self):
        if self.category_type == 'INCOME' and not self.income_head:
            raise ValidationError("Income head is required for INCOME category.")
        if self.category_type == 'EXPENSE' and not self.expense_head:
            raise ValidationError("Expense head is required for EXPENSE category.")
        if self.income_head and self.expense_head:
            raise ValidationError("A category cannot have both income head and expense head.")

    @property
    def name(self):
        if self.income_head:
            return self.income_head.incometype
        if self.expense_head:
            return self.expense_head.expensetype
        return "—"

    def get_actual_amount(self):
        """Sum actual entries for this category within the budget year date range."""
        from crucial.models import IncomeitemList, Expenseitemlist
        start = self.budget_year.year_start
        end = self.budget_year.year_end
        if self.category_type == 'INCOME':
            return IncomeitemList.objects.filter(
                incometype_id=self.income_head,
                income_date__gte=start,
                income_date__lte=end
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        else:
            return Expenseitemlist.objects.filter(
                expensetype_id=self.expense_head,
                expense_date__gte=start,
                expense_date__lte=end
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    def get_variance(self):
        return self.planned_amount - self.get_actual_amount()

    def get_variance_percent(self):
        if self.planned_amount > 0:
            actual = self.get_actual_amount()
            return round((actual / self.planned_amount) * 100, 1)
        return 0

    def get_status_class(self):
        pct = self.get_variance_percent()
        if pct >= 100:
            return 'danger'
        elif pct >= 80:
            return 'warning'
        return 'success'

    def get_monthly_allocations_sum(self):
        return self.monthly_allocations.aggregate(
            total=Sum('planned_amount'))['total'] or Decimal('0.00')


class BudgetMonthlyAllocation(models.Model):
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
    ]

    budget_category = models.ForeignKey(
        BudgetCategory, on_delete=models.CASCADE, related_name='monthly_allocations'
    )
    month = models.PositiveIntegerField(choices=MONTH_CHOICES)
    year = models.PositiveIntegerField()
    planned_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    actual_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    is_locked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('budget_category', 'month', 'year')
        ordering = ['year', 'month']
        verbose_name = 'Monthly Allocation'

    def __str__(self):
        return f"{self.budget_category} - {self.get_month_display()} {self.year}"

    @property
    def variance(self):
        return self.planned_amount - self.actual_amount

    @property
    def usage_percent(self):
        if self.planned_amount > 0:
            return round((self.actual_amount / self.planned_amount) * 100, 1)
        return 0

    @property
    def status_class(self):
        pct = self.usage_percent
        if pct >= 100:
            return 'danger'
        elif pct >= 80:
            return 'warning'
        return 'success'

    def recalculate_actual(self):
        """Recalculate actual amount from real entries for this month/year."""
        from crucial.models import IncomeitemList, Expenseitemlist
        cat = self.budget_category
        if cat.category_type == 'INCOME':
            total = IncomeitemList.objects.filter(
                incometype_id=cat.income_head,
                income_date__month=self.month,
                income_date__year=self.year
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        else:
            total = Expenseitemlist.objects.filter(
                expensetype_id=cat.expense_head,
                expense_date__month=self.month,
                expense_date__year=self.year
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        self.actual_amount = total
        self.save(update_fields=['actual_amount'])


class BudgetRevision(models.Model):
    budget_category = models.ForeignKey(
        BudgetCategory, on_delete=models.CASCADE, related_name='revisions'
    )
    old_amount = models.DecimalField(max_digits=15, decimal_places=2)
    new_amount = models.DecimalField(max_digits=15, decimal_places=2)
    reason = models.TextField()
    revised_by = models.ForeignKey(
        'user.StaffProfile', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    revised_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-revised_at']
        verbose_name = 'Budget Revision'

    def __str__(self):
        return f"{self.budget_category} | {self.old_amount} → {self.new_amount}"


class BudgetAlert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('WARNING', 'Warning (80%)'),
        ('CRITICAL', 'Critical (100%)'),
        ('OVERSPEND', 'Overspend (>100%)'),
    ]

    budget_category = models.ForeignKey(
        BudgetCategory, on_delete=models.CASCADE, related_name='alerts'
    )
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPE_CHOICES)
    threshold_percent = models.DecimalField(max_digits=6, decimal_places=2)
    actual_at_trigger = models.DecimalField(max_digits=15, decimal_places=2)
    is_acknowledged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Budget Alert'

    def __str__(self):
        return f"{self.alert_type} — {self.budget_category}"
