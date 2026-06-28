from django.contrib import admin
from .models import BudgetYear, BudgetCategory, BudgetMonthlyAllocation, BudgetRevision, BudgetAlert


class BudgetCategoryInline(admin.TabularInline):
    model = BudgetCategory
    extra = 0
    fields = ['category_type', 'income_head', 'expense_head', 'planned_amount', 'distribution_type']


@admin.register(BudgetYear)
class BudgetYearAdmin(admin.ModelAdmin):
    list_display = ['title', 'year_start', 'year_end', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['title']
    inlines = [BudgetCategoryInline]


class BudgetMonthlyInline(admin.TabularInline):
    model = BudgetMonthlyAllocation
    extra = 0
    fields = ['month', 'year', 'planned_amount', 'actual_amount', 'is_locked']
    readonly_fields = ['actual_amount']


class BudgetRevisionInline(admin.TabularInline):
    model = BudgetRevision
    extra = 0
    readonly_fields = ['old_amount', 'new_amount', 'reason', 'revised_by', 'revised_at']


@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ['budget_year', 'category_type', 'income_head', 'expense_head', 'planned_amount']
    list_filter = ['category_type', 'budget_year']
    inlines = [BudgetMonthlyInline, BudgetRevisionInline]


@admin.register(BudgetMonthlyAllocation)
class BudgetMonthlyAllocationAdmin(admin.ModelAdmin):
    list_display = ['budget_category', 'month', 'year', 'planned_amount', 'actual_amount', 'is_locked']
    list_filter = ['year', 'is_locked']


@admin.register(BudgetRevision)
class BudgetRevisionAdmin(admin.ModelAdmin):
    list_display = ['budget_category', 'old_amount', 'new_amount', 'revised_by', 'revised_at']
    readonly_fields = ['revised_at']


@admin.register(BudgetAlert)
class BudgetAlertAdmin(admin.ModelAdmin):
    list_display = ['budget_category', 'alert_type', 'threshold_percent', 'is_acknowledged', 'created_at']
    list_filter = ['alert_type', 'is_acknowledged']
    actions = ['acknowledge_alerts']

    def acknowledge_alerts(self, request, queryset):
        queryset.update(is_acknowledged=True)
        self.message_user(request, "Selected alerts acknowledged.")
    acknowledge_alerts.short_description = "Acknowledge selected alerts"
