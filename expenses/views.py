from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

@login_required
def profile(request):
    """Display and handle user profile information."""
    context = {
        'user': request.user,
    }
    return render(request, 'expenses/profile.html', context)


from .models import Category, Budget, Expense, Alert
from .forms import CategoryForm, BudgetForm, ExpenseForm, SignUpForm, LoginForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'expenses/signup.html', {'form': form})

@login_required
def dashboard(request):
    # Get recent expenses
    recent_expenses = Expense.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Get current month's expenses by category
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    monthly_expenses = Expense.objects.filter(
        user=request.user,
        date__year=current_year,
        date__month=current_month
    ).values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Calculate total spent this month
    total_spent = sum(expense['total'] for expense in monthly_expenses)
    
    # Get budgets for the current period
    today = timezone.now().date()
    active_budgets = Budget.objects.filter(
        user=request.user,
        start_date__lte=today
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    )
    
    # Calculate budget vs actuals
    budget_data = []
    for budget in active_budgets:
        expenses = Expense.objects.filter(
            user=request.user,
            category=budget.category,
            date__gte=budget.start_date,
            date__lte=budget.end_date if budget.end_date else today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        budget_data.append({
            'category': budget.category.name,
            'budget': budget.amount,
            'spent': expenses,
            'remaining': budget.amount - expenses,
            'percent_used': min(100, (expenses / budget.amount * 100) if budget.amount > 0 else 0)
        })
    
    # Get unread alerts
    unread_alerts = Alert.objects.filter(user=request.user, is_read=False).count()
    
    context = {
        'recent_expenses': recent_expenses,
        'monthly_expenses': monthly_expenses,
        'total_spent': total_spent,
        'budget_data': budget_data,
        'unread_alerts': unread_alerts,
    }
    
    return render(request, 'expenses/dashboard.html', context)

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user).order_by('name')
    return render(request, 'expenses/category_list.html', {'categories': categories})

@login_required
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('expenses:category_list')
    else:
        form = CategoryForm()
    return render(request, 'expenses/category_form.html', {'form': form, 'title': 'Add Category'})

@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('expenses:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'expenses/category_form.html', {'form': form, 'title': 'Edit Category'})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('expenses:category_list')
    return render(request, 'expenses/confirm_delete.html', {'object': category, 'type': 'category'})

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    
    # Filtering
    category_id = request.GET.get('category')
    if category_id:
        expenses = expenses.filter(category_id=category_id)
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)
    
    # Pagination
    paginator = Paginator(expenses, 10)  # Show 10 expenses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(user=request.user).order_by('name')
    
    context = {
        'expenses': page_obj,
        'categories': categories,
        'selected_category': int(category_id) if category_id else '',
        'date_from': date_from or '',
        'date_to': date_to or '',
    }
    
    return render(request, 'expenses/expense_list.html', context)

@login_required
def expense_add(request):
    if request.method == 'POST':
        form = ExpenseForm(request.user, request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            
            # Check budget and create alert if exceeded
            check_budget_alert(expense)
            
            return redirect('expenses:expense_list')
    else:
        form = ExpenseForm(user=request.user)
    
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Add Expense'})

def check_budget_alert(expense):
    """Check if expense exceeds any budget and create alert if it does"""
    today = timezone.now().date()
    
    # Get all active budgets for this category
    budgets = Budget.objects.filter(
        user=expense.user,
        category=expense.category,
        start_date__lte=today
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    )
    
    for budget in budgets:
        # Calculate total expenses in the budget period
        total_expenses = Expense.objects.filter(
            user=expense.user,
            category=expense.category,
            date__gte=budget.start_date,
            date__lte=budget.end_date if budget.end_date else today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Check if budget is exceeded
        if total_expenses > budget.amount:
            Alert.objects.create(
                user=expense.user,
                alert_type='budget_exceeded',
                message=f'Budget exceeded for {expense.category.name}! You have spent {total_expenses} out of {budget.amount} {budget.get_period_display()}.',
                related_expense=expense
            )

@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.user, request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expenses:expense_list')
    else:
        form = ExpenseForm(user=request.user, instance=expense)
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Edit Expense'})

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('expenses:expense_list')
    return render(request, 'expenses/confirm_delete.html', {'object': expense, 'type': 'expense'})

@login_required
def budget_list(request):
    today = timezone.now().date()
    active_budgets = Budget.objects.filter(
        user=request.user,
        start_date__lte=today
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    ).order_by('-start_date')
    
    # Calculate spent amounts for each budget
    budget_data = []
    for budget in active_budgets:
        expenses = Expense.objects.filter(
            user=request.user,
            category=budget.category,
            date__gte=budget.start_date,
            date__lte=budget.end_date if budget.end_date else today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        budget_data.append({
            'budget': budget,
            'spent': expenses,
            'remaining': budget.amount - expenses,
            'percent_used': min(100, (expenses / budget.amount * 100) if budget.amount > 0 else 0)
        })
    
    # Get expired budgets
    expired_budgets = Budget.objects.filter(
        user=request.user,
        end_date__lt=today
    ).order_by('-end_date')
    
    return render(request, 'expenses/budget_list.html', {
        'active_budgets': budget_data,
        'expired_budgets': expired_budgets
    })

@login_required
def budget_set(request):
    if request.method == 'POST':
        form = BudgetForm(request.user, request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget set successfully!')
            return redirect('expenses:budget_list')
    else:
        form = BudgetForm(user=request.user)
    
    return render(request, 'expenses/budget_form.html', {'form': form, 'title': 'Set Budget'})

@login_required
def budget_edit(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.user, request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('expenses:budget_list')
    else:
        form = BudgetForm(user=request.user, instance=budget)
    return render(request, 'expenses/budget_form.html', {'form': form, 'title': 'Edit Budget'})

@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted successfully!')
        return redirect('expenses:budget_list')
    return render(request, 'expenses/confirm_delete.html', {'object': budget, 'type': 'budget'})

@login_required
def reports(request):
    # Default to current year
    year = int(request.GET.get('year', timezone.now().year))
    
    # Get monthly expenses for the selected year
    monthly_expenses = Expense.objects.filter(
        user=request.user,
        date__year=year
    ).values('date__month').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('date__month')
    
    # Get category-wise expenses for the year
    category_expenses = Expense.objects.filter(
        user=request.user,
        date__year=year
    ).values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Prepare data for charts
    months = [f"{month:02d}" for month in range(1, 13)]
    monthly_totals = [0] * 12
    
    for expense in monthly_expenses:
        month_index = expense['date__month'] - 1
        monthly_totals[month_index] = float(expense['total'])
    
    # Get available years for the dropdown
    years = Expense.objects.filter(user=request.user).dates('date', 'year').order_by('-year')
    years = [d.year for d in years]
    if not years:  # If no expenses yet, just show current year
        years = [timezone.now().year]
    
    context = {
        'year': year,
        'years': years,
        'months': months,
        'monthly_totals': monthly_totals,
        'category_expenses': category_expenses,
    }
    
    return render(request, 'expenses/reports.html', context)

@login_required
def alerts(request):
    alerts = Alert.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark all unread alerts as read
    unread_alerts = alerts.filter(is_read=False)
    if unread_alerts.exists():
        unread_alerts.update(is_read=True)
    
    return render(request, 'expenses/alerts.html', {'alerts': alerts})

@login_required
def delete_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id, user=request.user)
    alert.delete()
    messages.success(request, 'Alert deleted successfully!')
    return redirect('expenses:alerts')

@login_required
def clear_alerts(request):
    Alert.objects.filter(user=request.user).delete()
    messages.success(request, 'All alerts cleared successfully!')
    return redirect('expenses:alerts')

# API Views
@login_required
def api_expense_summary(request):
    """API endpoint for expense summary data"""
    today = timezone.now().date()
    last_month = today - timedelta(days=30)
    
    # Total spent this month
    monthly_total = Expense.objects.filter(
        user=request.user,
        date__year=today.year,
        date__month=today.month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Total spent last month
    last_month_total = Expense.objects.filter(
        user=request.user,
        date__year=last_month.year,
        date__month=last_month.month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate percentage change
    if last_month_total > 0:
        percent_change = ((monthly_total - last_month_total) / last_month_total) * 100
    else:
        percent_change = 0
    
    # Top spending categories this month
    top_categories = Expense.objects.filter(
        user=request.user,
        date__year=today.year,
        date__month=today.month
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')[:5]
    
    data = {
        'monthly_total': float(monthly_total),
        'percent_change': float(percent_change),
        'top_categories': list(top_categories)
    }
    
    return JsonResponse(data)

@login_required
def api_expense_chart_data(request):
    """API endpoint for expense chart data"""
    # Get expenses for the last 6 months
    today = timezone.now().date()
    six_months_ago = today - timedelta(days=180)
    
    # Get monthly totals
    monthly_expenses = Expense.objects.filter(
        user=request.user,
        date__gte=six_months_ago,
        date__lte=today
    ).extra({
        'month': "date_trunc('month', date)"
    }).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    # Prepare data for chart
    months = []
    amounts = []
    
    for expense in monthly_expenses:
        months.append(expense['month'].strftime('%b %Y'))
        amounts.append(float(expense['total']))
    
    data = {
        'labels': months,
        'datasets': [{
            'label': 'Monthly Expenses',
            'data': amounts,
            'backgroundColor': 'rgba(54, 162, 235, 0.2)',
            'borderColor': 'rgba(54, 162, 235, 1)',
            'borderWidth': 1
        }]
    }
    
    return JsonResponse(data)
