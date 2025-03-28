from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Product
from django.core.exceptions import ValidationError
import json
import pandas as pd
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO  # Import BytesIO
from datetime import datetime
from sklearn.linear_model import LinearRegression
from django.conf import settings
from sklearn.model_selection import train_test_split
import os
import csv

def home(request):
    login_error = None
    signup_error = None
    form = UserCreationForm()

    if request.method == 'POST':
        if 'login' in request.POST:
            # Handle Login
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                login_error = 'Invalid username or password'
        
        elif 'signup' in request.POST:
            # Handle Signup
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect('dashboard')
            else:
                signup_error = form.errors  # Print form errors for debugging

    return render(request, 'home.html', {
        'login_error': login_error,
        'signup_error': signup_error,
        'signup_form': form
    })



@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def sales(request):
    if request.method == 'POST':
        if 'update_item' in request.POST:
            try:
                item_id = int(request.POST.get('update_id'))
                new_sales = float(request.POST.get('update_sales'))
                item_to_update = Product.objects.get(id=item_id)
                item_to_update.sales = new_sales
                item_to_update.save()
            except (Product.DoesNotExist, ValueError):
                return render(request, 'sales.html', {
                    'data': Product.objects.all().order_by('-sales'),
                    'error': 'Invalid data for update.'
                })
            return redirect('sales')

        elif 'delete_item' in request.POST:
            try:
                item_id = int(request.POST.get('delete_id'))
                item_to_delete = Product.objects.get(id=item_id)
                item_to_delete.delete()
            except (Product.DoesNotExist, ValueError):
                return render(request, 'sales.html', {
                    'data': Product.objects.all().order_by('-sales'),
                    'error': 'Invalid product ID for deletion.'
                })
            return redirect('sales')

        elif 'add_item' in request.POST:
            try:
                new_product = Product(
                    name=request.POST.get('name'),
                    category=request.POST.get('category'),
                    sales=float(request.POST.get('sales')),
                    quantity=int(request.POST.get('quantity')),
                    profit=float(request.POST.get('profit'))
                )
                new_product.save()
            except ValueError:
                return render(request, 'sales.html', {
                    'data': Product.objects.all().order_by('-sales'),
                    'error': 'Invalid data for new product.'
                })
            return redirect('sales')

    # Load product data, limit to top 5 by sales
    data = Product.objects.all().order_by('-sales') [:5]
    return render(request, 'sales.html', {'data': data})

def charts(request):
    try:
        # Read the CSV file
        data = pd.read_csv('myapp/files/stores_sales_forecasting.csv', encoding='ISO-8859-1')
        
        # Prepare data for Pie Chart (Example: distribution of Sales by Region)
        pie_data = data.groupby('Region')['Sales'].sum().reset_index()
        pie_chart_data = {
            'labels': pie_data['Region'].tolist(),
            'values': pie_data['Sales'].tolist()
        }
        
        # Prepare data for Bar Chart (Example: Sales by Month)
        # Convert 'Order Date' to datetime and extract month
        data['Order Date'] = pd.to_datetime(data['Order Date'])
        data['Month'] = data['Order Date'].dt.to_period('M').astype(str)
        bar_data = data.groupby('Month')['Sales'].sum().reset_index()
        bar_chart_data = {
            'x': bar_data['Month'].tolist(),
            'y': bar_data['Sales'].tolist()
        }
        
        # Prepare data for Line Chart (Example: Sales over time)
        line_data = data.groupby('Order Date')['Sales'].sum().reset_index()
        line_chart_data = {
            'x': line_data['Order Date'].astype(str).tolist(),
            'y': line_data['Sales'].tolist()
        }
        
        context = {
            'pie_chart_data': json.dumps(pie_chart_data),
            'bar_chart_data': json.dumps(bar_chart_data),
            'line_chart_data': json.dumps(line_chart_data)
        }
    except Exception as e:
        context = {
            'error': str(e)
        }

    return render(request, 'charts.html', context)

def render_to_pdf(template_src, context_dict={}):
    template = render_to_string(template_src, context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(template.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def report(request):
    try:
        products = Product.objects.all().values('name', 'category', 'sales', 'quantity', 'profit')
        data = pd.DataFrame(products)
        report_data = data.to_dict(orient='records')
        context = {
            'report_data': report_data,
        }
    except Exception as e:
        context = {
            'error': str(e)
        }

    if 'pdf' in request.GET:
        pdf = render_to_pdf('report.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Report_%s.pdf" % ("latest")
            content = "inline; filename=%s" % (filename)
            response['Content-Disposition'] = content
            return response
        return render_to_pdf('report.html', context)

    return render(request, 'report.html', context)

def About(request):
    return render(request, 'About.html')


def search(request):
    query = request.GET.get('query', '')
    search_results = []

    if query:
        try:
            # Update the path as per your project structure
            csv_file_path = 'myapp/files/stores_sales_forecasting.csv'
            data = pd.read_csv(csv_file_path, encoding='ISO-8859-1')

            # Filter the data based on the query
            search_results = data[data.apply(lambda row: query.lower() in row.astype(str).str.lower().to_list(), axis=1)].to_dict(orient='records')
        except Exception as e:
            return render(request, 'search.html', {'error': str(e)})

    return render(request, 'search.html', {'search_results': search_results, 'query': query})
