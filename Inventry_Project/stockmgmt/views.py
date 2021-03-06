from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import csv
from .models import *
from .forms import *

def home(request):
	title = 'Welcome: This is the Home Page'
	form = 'Welcome: This is the Home Page'
	context = {
		"title": title,
		"test": form,
	}
	return redirect('/list_item')


def list_item(request):
    title = 'List of Items'
    form = StockSearchForm(request.POST or None)
    queryset = Stock.objects.all()
    
    context = {
        "form": form,
        "title": title,
        "queryset": queryset,
    }
    if request.method == 'POST':
        queryset = Stock.objects.filter(#category__icontains=form['category'].value(),
                                        item_name__icontains=form['item_name'].value()
                                       )
        
        if form['export_to_CSV'].value() == True:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="List of stock.csv"'
            writer = csv.writer(response)
            writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
            instance = queryset
            for stock in instance:
                writer.writerow([stock.category, stock.item_name, stock.quantity])
            return response
        context = {
        "form": form,
        "title": title,
        "queryset": queryset,
    }
    return render(request, "list_item.html", context)

@login_required
def add_items(request):
    form = StockCreateForm(request.POST or None)
    if form.is_valid():
        messages.success(request, 'Successfully Added')
        form.save()
        return redirect('/list_item/')
    context = {
        "form": form,
        "title": "Add Item",
    }
    return render(request, "add_item.html", context)

@login_required
def update_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = StockUpdateForm(instance=queryset)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, instance=queryset)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Updated')
            return redirect('/list_item')

    context = {
        'form':form
    }
    return render(request, 'add_item.html', context)

@login_required
def delete_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    if request.method == 'POST':
        messages.success(request, 'Successfully Deleted')
        queryset.delete()
        return redirect('/list_item')
    return render(request, 'delete_items.html')

@login_required
def stock_detail(request, pk):
    queryset = Stock.objects.get(id=pk)
    context = {
        "title": queryset.item_name,
        "queryset": queryset,
    }
    return render(request, "stock_detail.html", context)

@login_required
def issue_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = IssueForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.quantity -= instance.issue_quantity
        instance.issue_by = str(request.user)
        messages.success(request, "Issued SUCCESSFULLY. " + str(instance.quantity) + " " + str(instance.item_name) + "s now left in Store")
        instance.save()

        return redirect('/stock_detail/'+str(instance.id))
        # return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": 'Issue ' + str(queryset.item_name),
        "queryset": queryset,
        "form": form,
        "username": 'Issue By: ' + str(request.user),
    }
    return render(request, "add_item.html", context)


@login_required
def receive_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = ReceiveForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.quantity += instance.receive_quantity
        instance.save()
        messages.success(request, "Received SUCCESSFULLY. " + str(instance.quantity) + " " + str(instance.item_name)+"s now in Store")

        return redirect('/stock_detail/'+str(instance.id))
        # return HttpResponseRedirect(instance.get_absolute_url())
    context = {
            "title": 'Reaceive ' + str(queryset.item_name),
            "instance": queryset,
            "form": form,
            "username": 'Receive By: ' + str(request.user),
        }
    return render(request, "add_item.html", context)

@login_required
def reorder_level(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = ReorderLevelForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Reorder level for " + str(instance.item_name) + " is updated to " + str(instance.reorder_level))

        return redirect("/list_item")
    context = {
            "instance": queryset,
            "form": form,
        }
    return render(request, "add_item.html", context)

@login_required
def list_history(request):
    header = 'LIST OF ITEMS'
    queryset = StockHistory.objects.all()
    form = StockHistorySearchForm(request.POST or None)
    context = {
        "header": header,
        "queryset": queryset,
    }
    if request.method == 'POST':
        category = form['category'].value()
        queryset = StockHistory.objects.filter(
                    item_name__icontains=form['item_name'].value(),
                    last_updated__range=[
                                            form['start_date'].value(),
                                            form['end_date'].value()
                                        ]
                    )
        if (category != ''):
            queryset = queryset.filter(category_id=category)

        context = {
        "form": form,
        "header": header,
        "queryset": queryset,
    }
    return render(request, "list_history.html",context)