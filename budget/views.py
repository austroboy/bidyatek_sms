from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from decimal import Decimal

from .models import BudgetYear, BudgetCategory, BudgetMonthlyAllocation, BudgetRevision, BudgetAlert
from .forms import BudgetYearForm, BudgetCategoryForm, BudgetMonthlyAllocationForm, BudgetRevisionForm
from .utils import create_monthly_allocations, redistribute_monthly_allocations, check_budget_alerts


# ─── Dashboard ────────────────────────────────────────────────────────────────

def budget_dashboard(request):
    """Main landing page — list all budget years."""
    budgets = BudgetYear.objects.all()
    active_budget = budgets.filter(status='ACTIVE').first()
    context = {
        'budgets': budgets,
        'active_budget': active_budget,
    }
    return render(request, 'budget/dashboard.html', context)


# ─── Create Budget Year ────────────────────────────────────────────────────────

def budget_create(request):
    """Create a new BudgetYear (DRAFT status)."""
    if request.method == 'POST':
        form = BudgetYearForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.status = 'DRAFT'
            # Attach staff profile if available
            try:
                budget.created_by = request.user.staffprofile
            except Exception:
                pass
            budget.save()
            messages.success(request, f'Budget "{budget.title}" created successfully. Now add categories.')
            return redirect('budget_detail', pk=budget.pk)
    else:
        form = BudgetYearForm()
    return render(request, 'budget/create.html', {'form': form})


# ─── Budget Detail ─────────────────────────────────────────────────────────────

def budget_detail(request, pk):
    """Main detail page with income and expense category tables."""
    budget = get_object_or_404(BudgetYear, pk=pk)
    income_cats = budget.categories.filter(category_type='INCOME')
    expense_cats = budget.categories.filter(category_type='EXPENSE')

    # Precompute actuals for display
    for cat in list(income_cats) + list(expense_cats):
        cat._actual = cat.get_actual_amount()
        cat._variance = cat.get_variance()
        cat._pct = cat.get_variance_percent()
        cat._status = cat.get_status_class()

    alerts = BudgetAlert.objects.filter(
        budget_category__budget_year=budget,
        is_acknowledged=False
    ).select_related('budget_category')[:5]

    context = {
        'budget': budget,
        'income_cats': income_cats,
        'expense_cats': expense_cats,
        'alerts': alerts,
    }
    return render(request, 'budget/detail.html', context)


# ─── Category Add ─────────────────────────────────────────────────────────────

def budget_category_add(request, pk):
    """HTMX modal — add a budget category to a budget year."""
    budget = get_object_or_404(BudgetYear, pk=pk)

    if request.method == 'POST':
        form = BudgetCategoryForm(request.POST, budget_year=budget)
        if form.is_valid():
            with transaction.atomic():
                cat = form.save(commit=False)
                cat.budget_year = budget
                # Clear the wrong head based on type
                if cat.category_type == 'INCOME':
                    cat.expense_head = None
                else:
                    cat.income_head = None
                cat.save()
                # Auto-create monthly allocations
                create_monthly_allocations(cat)

            # HTMX: return empty response to trigger list refresh
            response = HttpResponse('')
            response['HX-Trigger'] = 'budgetCategoryChanged'
            return response
        # If form invalid, re-render modal with errors
        return render(request, 'budget/partials/category_form.html', {
            'form': form, 'budget': budget
        })

    else:
        # Pre-fill category_type from query param
        initial = {}
        cat_type = request.GET.get('type', 'INCOME')
        initial['category_type'] = cat_type
        form = BudgetCategoryForm(initial=initial, budget_year=budget)
        return render(request, 'budget/partials/category_form.html', {
            'form': form, 'budget': budget, 'cat_type': cat_type
        })


# ─── Category Edit ────────────────────────────────────────────────────────────

def budget_category_edit(request, cat_pk):
    """HTMX modal — edit/revise a budget category."""
    cat = get_object_or_404(BudgetCategory, pk=cat_pk)
    budget = cat.budget_year
    is_active = budget.status == 'ACTIVE'

    if request.method == 'POST':
        if is_active:
            # Active budget: only revision allowed
            rev_form = BudgetRevisionForm(request.POST)
            if rev_form.is_valid():
                with transaction.atomic():
                    old_amount = cat.planned_amount
                    new_amount = rev_form.cleaned_data['new_amount']
                    reason = rev_form.cleaned_data['reason']
                    # Save revision history
                    BudgetRevision.objects.create(
                        budget_category=cat,
                        old_amount=old_amount,
                        new_amount=new_amount,
                        reason=reason,
                        revised_by=getattr(request.user, 'staffprofile', None)
                    )
                    # Update planned amount
                    cat.planned_amount = new_amount
                    cat.save()
                    # Redistribute monthly allocations if equal split
                    if cat.distribution_type == 'EQUAL_MONTHLY':
                        redistribute_monthly_allocations(cat)
                response = HttpResponse('')
                response['HX-Trigger'] = 'budgetCategoryChanged'
                return response
            return render(request, 'budget/partials/category_edit.html', {
                'cat': cat, 'budget': budget,
                'rev_form': rev_form, 'is_active': is_active
            })
        else:
            # Draft: full edit allowed
            form = BudgetCategoryForm(request.POST, instance=cat, budget_year=budget)
            if form.is_valid():
                with transaction.atomic():
                    old_amount = cat.planned_amount
                    updated_cat = form.save(commit=False)
                    if updated_cat.category_type == 'INCOME':
                        updated_cat.expense_head = None
                    else:
                        updated_cat.income_head = None
                    updated_cat.save()
                    # Update monthly allocations if amount changed
                    if old_amount != updated_cat.planned_amount:
                        cat.monthly_allocations.all().delete()
                        create_monthly_allocations(updated_cat)
                response = HttpResponse('')
                response['HX-Trigger'] = 'budgetCategoryChanged'
                return response
            return render(request, 'budget/partials/category_edit.html', {
                'cat': cat, 'budget': budget,
                'form': form, 'is_active': is_active
            })

    else:
        if is_active:
            rev_form = BudgetRevisionForm(initial={'new_amount': cat.planned_amount})
            return render(request, 'budget/partials/category_edit.html', {
                'cat': cat, 'budget': budget,
                'rev_form': rev_form, 'is_active': is_active
            })
        else:
            form = BudgetCategoryForm(instance=cat, budget_year=budget)
            revisions = cat.revisions.all()[:5]
            return render(request, 'budget/partials/category_edit.html', {
                'cat': cat, 'budget': budget,
                'form': form, 'is_active': is_active,
                'revisions': revisions
            })


# ─── Category Delete ──────────────────────────────────────────────────────────

def budget_category_delete(request, cat_pk):
    """Delete a category — only allowed in DRAFT status."""
    cat = get_object_or_404(BudgetCategory, pk=cat_pk)
    budget = cat.budget_year
    if budget.status != 'DRAFT':
        return HttpResponse('Cannot delete from an active budget.', status=403)
    if request.method == 'DELETE' or request.method == 'POST':
        cat.delete()
        response = HttpResponse('')
        response['HX-Trigger'] = 'budgetCategoryChanged'
        return response
    return HttpResponse(status=405)


# ─── Category List Partial ────────────────────────────────────────────────────

def budget_category_list(request, pk):
    """HTMX partial — returns updated category tables after changes."""
    budget = get_object_or_404(BudgetYear, pk=pk)
    income_cats = budget.categories.filter(category_type='INCOME')
    expense_cats = budget.categories.filter(category_type='EXPENSE')

    for cat in list(income_cats) + list(expense_cats):
        cat._actual = cat.get_actual_amount()
        cat._variance = cat.get_variance()
        cat._pct = cat.get_variance_percent()
        cat._status = cat.get_status_class()

    return render(request, 'budget/partials/category_tables.html', {
        'budget': budget,
        'income_cats': income_cats,
        'expense_cats': expense_cats,
    })


# ─── Monthly Allocations ──────────────────────────────────────────────────────

def budget_monthly(request, cat_pk):
    """View and edit monthly allocations for a budget category."""
    cat = get_object_or_404(BudgetCategory, pk=cat_pk)
    budget = cat.budget_year
    allocations = cat.monthly_allocations.all()

    if request.method == 'POST' and budget.status == 'DRAFT':
        # Update multiple monthly amounts at once
        with transaction.atomic():
            for alloc in allocations:
                if not alloc.is_locked:
                    field_name = f'amount_{alloc.pk}'
                    val = request.POST.get(field_name)
                    if val is not None:
                        try:
                            alloc.planned_amount = Decimal(val)
                            alloc.save(update_fields=['planned_amount'])
                        except Exception:
                            pass
        messages.success(request, 'Monthly allocations updated.')
        return redirect('budget_monthly', cat_pk=cat_pk)

    # Calculate totals
    total_planned = allocations.aggregate(t=Sum('planned_amount'))['t'] or Decimal('0.00')
    total_actual = allocations.aggregate(t=Sum('actual_amount'))['t'] or Decimal('0.00')
    remaining = cat.planned_amount - total_planned

    return render(request, 'budget/monthly.html', {
        'cat': cat,
        'budget': budget,
        'allocations': allocations,
        'total_planned': total_planned,
        'total_actual': total_actual,
        'remaining': remaining,
    })


# ─── Activate Budget ──────────────────────────────────────────────────────────

def budget_activate(request, pk):
    """Activate a DRAFT budget. Only one budget can be ACTIVE."""
    budget = get_object_or_404(BudgetYear, pk=pk)
    if request.method == 'POST':
        if budget.status != 'DRAFT':
            messages.error(request, 'Only DRAFT budgets can be activated.')
            return redirect('budget_detail', pk=pk)
        if budget.categories.count() == 0:
            messages.error(request, 'Add at least one category before activating.')
            return redirect('budget_detail', pk=pk)
        # Deactivate any other active budgets
        BudgetYear.objects.filter(status='ACTIVE').update(status='CLOSED')
        budget.status = 'ACTIVE'
        try:
            budget.approved_by = request.user.staffprofile
        except Exception:
            pass
        budget.save()
        messages.success(request, f'Budget "{budget.title}" is now ACTIVE.')
        return redirect('budget_detail', pk=pk)
    return redirect('budget_detail', pk=pk)


# ─── Close Budget ─────────────────────────────────────────────────────────────

def budget_close(request, pk):
    """Close an ACTIVE budget and lock all past monthly rows."""
    budget = get_object_or_404(BudgetYear, pk=pk)
    if request.method == 'POST':
        if budget.status != 'ACTIVE':
            messages.error(request, 'Only ACTIVE budgets can be closed.')
            return redirect('budget_detail', pk=pk)
        budget.status = 'CLOSED'
        budget.save()
        # Lock all monthly allocations
        BudgetMonthlyAllocation.objects.filter(
            budget_category__budget_year=budget
        ).update(is_locked=True)
        messages.success(request, f'Budget "{budget.title}" is now CLOSED.')
        return redirect('budget_detail', pk=pk)
    return redirect('budget_detail', pk=pk)


# ─── Alerts ───────────────────────────────────────────────────────────────────

def budget_alerts(request):
    """View all budget alerts with filter and acknowledge option."""
    filter_type = request.GET.get('type', '')
    show_ack = request.GET.get('acknowledged', '') == '1'

    alerts = BudgetAlert.objects.select_related(
        'budget_category', 'budget_category__budget_year',
        'budget_category__income_head', 'budget_category__expense_head'
    )

    if filter_type:
        alerts = alerts.filter(alert_type=filter_type)
    if not show_ack:
        alerts = alerts.filter(is_acknowledged=False)

    return render(request, 'budget/alerts.html', {
        'alerts': alerts,
        'filter_type': filter_type,
        'show_ack': show_ack,
    })


def budget_alert_acknowledge(request, alert_pk):
    """HTMX — mark an alert as acknowledged."""
    alert = get_object_or_404(BudgetAlert, pk=alert_pk)
    if request.method == 'POST':
        alert.is_acknowledged = True
        alert.save(update_fields=['is_acknowledged'])
        # Return empty so HTMX removes the row
        return HttpResponse('')
    return HttpResponse(status=405)


# ─── Annual Report ────────────────────────────────────────────────────────────

def budget_report(request, pk):
    """Full year Budget vs Actual report."""
    budget = get_object_or_404(BudgetYear, pk=pk)
    income_cats = budget.categories.filter(category_type='INCOME')
    expense_cats = budget.categories.filter(category_type='EXPENSE')

    # Precompute for report
    income_data = []
    for cat in income_cats:
        actual = cat.get_actual_amount()
        planned = cat.planned_amount
        variance = planned - actual
        pct = round((actual / planned * 100), 1) if planned > 0 else 0
        income_data.append({
            'name': cat.name,
            'planned': planned,
            'actual': actual,
            'variance': variance,
            'pct': pct,
            'status': 'success' if pct < 80 else ('warning' if pct < 100 else 'danger'),
        })

    expense_data = []
    for cat in expense_cats:
        actual = cat.get_actual_amount()
        planned = cat.planned_amount
        variance = planned - actual
        pct = round((actual / planned * 100), 1) if planned > 0 else 0
        expense_data.append({
            'name': cat.name,
            'planned': planned,
            'actual': actual,
            'variance': variance,
            'pct': pct,
            'status': 'success' if pct < 80 else ('warning' if pct < 100 else 'danger'),
        })

    # Monthly trend: 12 rows from all categories combined
    from crucial.models import IncomeitemList, Expenseitemlist
    monthly_trend = []
    from datetime import date
    start = budget.year_start
    end = budget.year_end
    y, m = start.year, start.month
    while date(y, m, 1) <= end:
        inc = IncomeitemList.objects.filter(
            income_date__year=y, income_date__month=m,
            income_date__gte=start, income_date__lte=end
        ).aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
        exp = Expenseitemlist.objects.filter(
            expense_date__year=y, expense_date__month=m,
            expense_date__gte=start, expense_date__lte=end
        ).aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
        monthly_trend.append({'month': m, 'year': y, 'income': inc, 'expense': exp})
        if m == 12:
            m, y = 1, y + 1
        else:
            m += 1

    # All revisions
    revisions = BudgetRevision.objects.filter(
        budget_category__budget_year=budget
    ).select_related('budget_category', 'revised_by')

    context = {
        'budget': budget,
        'income_data': income_data,
        'expense_data': expense_data,
        'monthly_trend': monthly_trend,
        'revisions': revisions,
        'total_income_planned': sum(d['planned'] for d in income_data),
        'total_income_actual': sum(d['actual'] for d in income_data),
        'total_expense_planned': sum(d['planned'] for d in expense_data),
        'total_expense_actual': sum(d['actual'] for d in expense_data),
    }
    return render(request, 'budget/report.html', context)
