from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from .models import ExpenseInfo, Budget
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout,login,authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import matplotlib.pyplot as plt
import numpy as np
from django.db.models import Q
# Create your views here.


def index(request):
    expense_items = ExpenseInfo.objects.filter(user_expense=request.user).order_by('-date_added')
    page = request.GET.get('page', 1)
    paginator = Paginator(expense_items, 5)
    try:
        expense_items = paginator.page(page)
    except PageNotAnInteger:
        expense_items = paginator.page(1)
    except EmptyPage:
        expense_items = paginator.page(paginator.num_pages)
    
    try:
        budget_total = ExpenseInfo.objects.filter(user_expense=request.user).aggregate(budget=Sum('cost',filter=Q(cost__gt=0)))
        if budget_total['budget'] == None:
            budget_total['budget'] = 0
    except TypeError:
        budget_total['budget'] = 0
    try:
        expense_total = ExpenseInfo.objects.filter(user_expense=request.user).aggregate(expenses=Sum('cost',filter=Q(cost__lt=0)))
        if expense_total['expenses'] == None:
            expense_total['expenses'] = 0
    except TypeError:
        expense_total['expenses'] = 0
    
    try:
        list_items = Budget.objects.get(user_limit=request.user)
        saldo = list_items.saldo
        try:
            if list_items == None:
                limit = 0.0
                saldo = 0.0
            else:
                list_items = Budget.objects.filter(user_limit=request.user).aggregate(total=Sum('limit',filter=Q(limit__gt=0)))
                limit = list_items['total']
        except TypeError:
            limit = 0.0
            saldo = 0.0
    except Budget.DoesNotExist:
        limit = 0.0
        saldo = 0.0
            
    fig,ax=plt.subplots()
    ax.bar(['Gastos','Presupuesto'], [abs(expense_total['expenses']),budget_total['budget']],color=['red','green'])
    ax.set_title('Gastos vs Presupuesto')
    plt.savefig('budget_app/static/budget_app/expense.jpg')
    
    context = {'saldo':saldo,'limit_list': limit,'expense_items':expense_items,'budget':budget_total['budget'],'expenses':abs(expense_total['expenses'])}
    return render(request,'budget_app/index.html',context=context)

def add_item(request):
    name = request.POST['expense_name']
    expense_cost = request.POST['cost']
    expense_date = request.POST['expense_date']
    
    try:
        list_items = Budget.objects.get(user_limit=request.user)
        try:
            if list_items == None:
                limit = 0.0
            else:
                list_items = Budget.objects.filter(user_limit=request.user).aggregate(total=Sum('limit',filter=Q(limit__gt=0)))
                limit = list_items['total']
        except TypeError:
            limit = 0.0
    except Budget.DoesNotExist:
        limit = 0.0
    
    if limit == 0.0:
        Budget.objects.create(limit=expense_cost,saldo=expense_cost,user_limit=request.user)
    
    listvalue = Budget.objects.get(user_limit=request.user)
    
    ExpenseInfo.objects.create(expense_name=name,cost=expense_cost,date_added=expense_date,user_expense=request.user)
    
    budget_total = ExpenseInfo.objects.filter(user_expense=request.user).aggregate(budget=Sum('cost',filter=Q(cost__gt=0)))
    if budget_total['budget'] == None:
        budget_total['budget'] = 0
    expense_total = ExpenseInfo.objects.filter(user_expense=request.user).aggregate(expenses=Sum('cost',filter=Q(cost__lt=0)))
    if expense_total['expenses'] == None:
        expense_total['expenses'] = 0
        
    listvalue.saldo = budget_total['budget'] + expense_total['expenses']
        
    if limit > 0.0:
        if limit > listvalue.saldo:            
            listvalue.limit = listvalue.limit + (listvalue.limit - listvalue.saldo) * 0.1
    
    listvalue.save()    
    
    fig,ax=plt.subplots()
    ax.bar(['Expenses','Budget'], [abs(expense_total['expenses']),budget_total['budget']],color=['red','green'])
    ax.set_title('Your total expenses vs. total budget')
    plt.savefig('budget_app/static/budget_app/expense.jpg')
    return HttpResponseRedirect('app')

def delete_item(request,part_id =None):
    object = ExpenseInfo.objects.get(id=part_id)
    object.delete()
    
    listvalue = Budget.objects.get(user_limit=request.user)
    budget_total = ExpenseInfo.objects.filter(user_expense=request.user).aggregate(budget=Sum('cost',filter=Q(cost__gt=0)))
    if budget_total['budget'] == None:
        budget_total['budget'] = 0
    expense_total = ExpenseInfo.objects.filter(user_expense=request.user).aggregate(expenses=Sum('cost',filter=Q(cost__lt=0)))
    if expense_total['expenses'] == None:
        expense_total['expenses'] = 0
        
    listvalue.saldo = budget_total['budget'] + expense_total['expenses']
    listvalue.save()
    
    return HttpResponseRedirect('app')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


def sign_up(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request,user)
            return HttpResponseRedirect('app')
    else:
        form = UserCreationForm
    return render(request,'budget_app/sign_up.html',{'form':form})
