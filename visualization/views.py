import base64
import urllib
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib
import plotly.graph_objs as go
import plotly.offline as py
import pandas as pd
import pymongo
import numpy as np
from django.shortcuts import render

import plotly.graph_objects as go
import plotly.io as py
import base64
from user.models import Profile
from functools import partial
# import asyncio
# import chart_studio

# import io
# import IPython
from dashboard.models import Producer

import plotly.graph_objects as go
from contextvars import Context

from plotly.offline import plot

import mysql.connector
matplotlib.use('agg')

client = pymongo.MongoClient("mongodb+srv://simplify:mineeproject@cluster0.glsg7.mongodb.net/?retryWrites=true&w=majority")
db = client.simplify
collection = db.newsales
collection1 = db.producer


def generate_plot(data):
    fig = go.Figure(data=[
        go.Scatter(x=list(data.keys()), y=list(data.values()), mode='lines+markers')
    ])
    fig.update_layout(
        title='Sales by Date',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Sales')
    )
    return fig.to_html(full_html=True)


def generate_plotbar(data):
    fig = go.Figure(data=[
        go.Bar(x=list(data.keys()), y=list(data.values()))
    ])
    fig.update_layout(
        title='Product Sales',
        xaxis=dict(title='Product'),
        yaxis=dict(title='Sales')
    )
    return fig.to_html(full_html=True)


def generate_plotbarshop(forecast_dict):
    # Create a bar chart figure
    fig = go.Figure(data=[go.Bar(x=list(forecast_dict.keys()), y=list(forecast_dict.values()))])

    # Set the title and labels
    fig.update_layout(title='Visualization plot', xaxis_title='Shop ids', yaxis_title='Sales')

    # Convert the figure to HTML string
    plot_data = fig.to_html(full_html=True)

    return plot_data    

def generate_plotgrp(compare_data, present_data):
    # Create a Plotly bar chart
    fig = go.Figure()

    # Add the current data as a line chart
    fig.add_trace(go.Scatter(
        x=present_data['Product'],
        y=present_data['Sales'],
        mode='lines',
        name='Current Data'
    ))

    # Add the compare data as a line chart
    fig.add_trace(go.Scatter(
        x=compare_data['Product'],
        y=compare_data['Sales'],
        mode='lines',
        name='Compare Data'
    ))

    # Set the title and labels
    fig.update_layout(
        title='Comparison',
        xaxis=dict(title='Product'),
        yaxis=dict(title='Sales')
    )

    # Generate the HTML div element for the plot
    plot_data = py.plot(fig, output_type='div', include_plotlyjs=False)

    return plot_data

# def generate_plot(forecast_dict):
#     # Create a line chart figure
#     fig = go.Figure(data=[go.Line(x=list(forecast_dict.keys()), y=list(forecast_dict.values()))])

#     # Set the title and labels
#     fig.update_layout(title='Visualization plot', xaxis_title='Month', yaxis_title='Sales')

#     # Generate the HTML div element for the plot
#     plot_data = py.plot(fig, output_type='div', include_plotlyjs=False)

#     return plot_data


def vmshop(request):
    user = request.user
    currentUser = Profile.objects.filter(staff=user).first()
    shop_id = currentUser.branchID

    data = pd.DataFrame(list(collection.find({'shop_id': shop_id})))
    data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
    product = "Product"
    date = "Date"

    # Get a list of all products in the shop
    products = list(data[product].unique())
    currentdate = data[date].max()
    product_data = data[data[date] == currentdate]
    forecast_dict = dict(zip(product_data['Product'], np.round(product_data['Sales'], 2)))

    # Generate the Plotly bar chart
    plot_data = generate_plotbar(forecast_dict)

    # Pass the product list and Plotly HTML to the Django template
    context = {'products': products, 'plot_data': plot_data}
    return render(request, 'visualization/vmshop.html', context)


def outvms(request):
    user = request.user
    currentUser = Profile.objects.filter(staff=user).first()
    shop_id = currentUser.branchID

    data = pd.DataFrame(list(collection.find({'shop_id': shop_id})))
    data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
    products = "Product"
    if request.method == 'POST':
        selected_product = request.POST.get('selected_product')
        startdate = request.POST.get('startdate')

        product_data = data[(data[products] == selected_product) & (data['Date'] >= startdate)]
        if product_data.empty:
            # Handle case when no data is available for the selected product and start date
            # You can return an error message or redirect to a different page
            return render(request, 'visualization/no_data.html')

        max_date = product_data['Date'].max()
        if pd.isna(startdate) or pd.isna(max_date):
            # Handle case when start date or max date is missing or invalid
            # You can return an error message or redirect to a different page
            return render(request, 'visualization/invalid_dates.html')

        months = pd.date_range(start=startdate, end=max_date, freq='MS').strftime('%B %Y')
        forecast_dict = dict(zip(months, np.round(product_data['Sales'], 2)))

        # Generate the Plotly line chart
        plot_data = generate_plot(forecast_dict)

        context = {'startdate': startdate, 'forecast': forecast_dict,
                   'selected_product': selected_product, 'shopid': shop_id, 'product_data': product_data['Sales'],
                   'plot_data': plot_data}
        return render(request, 'visualization/outvms.html', context)
    else:
        # Handle the initial GET request
        # You can add code here to provide initial data when the page is first loaded
        return render(request, 'visualization/outvms.html')


def vmowner(request):
    data = pd.DataFrame(list(collection.find()))
    data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
    product = "Product"
    shop_id = "shop_id"
    date = "Date"
    products = list(data[product].unique())
    shop_ids = list(data[shop_id].unique())

    currentdate = data[date].max()
    product_data = data[data[date] == currentdate]
    prod_data = product_data.groupby('Product')['Sales'].sum()

    forecast_dict = dict(zip(prod_data.index, prod_data.values))

    # Generate the Plotly bar chart
    plot_data = generate_plotbar(forecast_dict)

    context = {'products': products, 'shop_ids': shop_ids, 'plot_data': plot_data}
    return render(request, 'visualization/vmowner.html', context)



def outvmo(request):
    if request.method == 'POST':
        # Get selected shop from dropdown
        selected_shop = request.POST.get('selected_shop')
        # Get selected product from dropdown
        selected_product = request.POST.get('selected_product')
        data = pd.DataFrame(list(collection.find()))
        data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
        # Filter data to get sales of the selected product
        product = "Product"
        shop_id = "shop_id"
        produc_data = data[data[product] == selected_product]

        product_data = produc_data[produc_data[shop_id] == selected_shop]

        startdate = request.POST.get('startdate')
        # Filter data to get sales of the selected product
        product_data = data[(data[product] == selected_product) & (data['Date'] >= startdate)]

        # Create a list of months
        months = pd.date_range(end=product_data['Date'].max(), start=startdate, freq='MS').strftime('%B %Y')

        # Combine sales values and months into a dictionary
        sales_dict = dict(zip(months, np.round(product_data['Sales'], 2)))

        # Generate the Plotly plot
        fig = go.Figure(data=[
            go.Scatter(x=list(sales_dict.keys()), y=list(sales_dict.values()), name='Sales')
        ])
        fig.update_layout(
            title='Sales Trend',
            xaxis=dict(title='Month'),
            yaxis=dict(title='Sales')
        )

        plot_data = fig.to_html(full_html=True)

        context = {'startdate': startdate, 'forecast': sales_dict,
                   'selected_product': selected_product, 'shopid': shop_id, 'selected_shop': selected_shop,
                   'plot_data': plot_data}
        return render(request, 'visualization/outvmo.html', context)


import plotly.offline as pyo
import plotly.graph_objs as go

def vmprod(request):
    user = request.user
    currentUser = Producer.objects.filter(name=user).first()
    producer_id = currentUser.producer_id
    data = pd.DataFrame(list(collection1.find({'producer_id': producer_id})))

    print(data)
    product = "Product"
    date = "Date"
    sales = "Sales"
    # Get a list of all products in the shop
    products = list(data[product].unique())

    data = pd.DataFrame(list(collection.find({'Product': {'$in': products}})))
    data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
    shopids = list(data['shop_id'].unique())
    print(data)
    currentdate = data[date].max()
    print(currentdate)
    product_data = data[data[date] == currentdate]
    print(product_data)
    prod_data = product_data.loc[:, ['Product', 'Sales',]]
    print(prod_data)
    prod_data = product_data.groupby('Product')['Sales'].sum()

    forecast_dict = dict(zip(prod_data.index, prod_data.values))
    print(forecast_dict)

    # Generate the Plotly plot
    fig = go.Figure(data=[
        go.Bar(x=list(forecast_dict.keys()), y=list(forecast_dict.values()))
    ])
    fig.update_layout(
        title='Product Sales',
        xaxis=dict(title='Product'),
        yaxis=dict(title='Sales')
    )

    # Create an HTML file for the Plotly plot
    plot_filename = 'plot.html'
    # plot_data=py.plot(fig, filename=plot_filename, auto_open=False)
    plot_data=py.plot(fig, output_type='div', auto_open=False)
    
    context = {'products': products, 'plot_filename': plot_filename, 'shopids': shopids, 'data': data,'plot_data':plot_data}
    return render(request, 'visualization/vmprod.html', context)


def outvmp(request):
    sales_by_date = {}
    products = "Product"
    if request.method == 'POST':
        # Get selected product from dropdown
        selected_product = request.POST.get('selected_product')
        start_date = request.POST.get('startdate')

        collection = db.newsales
        product_data = pd.DataFrame(
            list(collection.find({products: selected_product})))
        product_data['Sales'] = pd.to_numeric(
            product_data['Sales'], errors='coerce')
        print(product_data)
        # Group rows by date and sum the sales values for each date
        sales_by_date = product_data.groupby('Date')['Sales'].sum()

        # Create a list of months
        months = pd.date_range(
            start=start_date, end=sales_by_date.index.max(), freq='MS').strftime('%B %Y')

        # Combine sales values and months into a dictionary
        forecast_dict = dict(zip(months, np.round(sales_by_date.values, 2)))

        # Generate the Plotly plot
        fig = go.Figure(data=[
            go.Scatter(x=list(forecast_dict.keys()), y=list(forecast_dict.values()), mode='lines+markers')
        ])
        fig.update_layout(
            title='Sales by Date',
            xaxis=dict(title='Date'),
            yaxis=dict(title='Sales')
        )

        # Create an HTML file for the Plotly plot
        plot_filename = 'plot.html'
        # pyo.plot(fig, filename=plot_filename, auto_open=False)
        plot_data=py.plot(fig, output_type='div', auto_open=False)

        # Pass the forecast dictionary and the list of products to the template
        context = {'plot_filename': plot_filename, 'startdate': start_date, 'forecast': forecast_dict,
                   'selected_product': selected_product, 'product_data': product_data['Sales'],'plot_data':plot_data}
        return render(request, 'visualization/outvmp.html', context)



def outvmscompare(request):
    shop_id = "1"
    data = pd.DataFrame(list(collection.find({'shop_id': shop_id})))
    data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
    product = "Product"
    date = "Date"
    currentdate = data[date].max()

    if request.method == 'POST':
        # Get selected product from dropdown
        comparedate = request.POST.get('comparedate')
        product_data = data[data[date] == currentdate]
        compare_data = data[data[date] == comparedate]

        # Select two columns from the dataframe
        product_data = product_data.loc[:, ['Product', 'Sales', 'Date']]
        compare_data = compare_data.loc[:, ['Product', 'Sales', 'Date']]

        # Generate the Plotly plot
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=product_data['Product'],
            y=product_data['Sales'],
            name='Current Data'
        ))
        fig.add_trace(go.Bar(
            x=compare_data['Product'],
            y=compare_data['Sales'],
            name='Compare Data'
        ))
        fig.update_layout(
            title='Comparison',
            xaxis=dict(title='Product'),
            yaxis=dict(title='Sales'),
            barmode='group'
        )

        # Generate the Plotly plot
        plot_data = py.plot(fig, output_type='div')

        context = {'comparedate': comparedate, 'plot_data': plot_data}
        return render(request, 'visualization/outvmscompare.html', context)

    return render(request, 'visualization/outvmscompare.html')


def outvmpprodwise(request):
    producer_id = "1"
    data = pd.DataFrame(list(collection1.find({'producer_id': producer_id})))

    product = "Product"
    date = "Date"
    sales = "Sales"
    # Get a list of all products in the shop
    products = list(data[product].unique())

    data = pd.DataFrame(list(collection.find({'Product': {'$in': products}})))
    data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
    shopids = list(data['shop_id'].unique())

    if request.method == 'POST':
        currentdate = data[date].max()
        current_data = data[data[date] == currentdate]
        selected_shop = request.POST.get('selected_shop')
        product_data = current_data[current_data['shop_id'] == selected_shop]
        # Visualize sales data by product using Plotly
        forecast_dict = dict(
            zip(product_data['Product'], np.round(product_data['Sales'], 2)))

        fig = go.Figure(data=[
            go.Bar(x=list(forecast_dict.keys()), y=list(forecast_dict.values()))
        ])
        fig.update_layout(
            title='Sales by Product',
            xaxis=dict(title='Product'),
            yaxis=dict(title='Sales')
        )

        # Generate the Plotly plot
        plot_data = py.plot(fig, output_type='div')

        context = {'plot_data': plot_data, 'forecast': forecast_dict, 'selected_shop': selected_shop}
        return render(request, 'visualization/outvmpprodwise.html', context)


def outvmpshopwise(request):
    producer_id = "1"
    data = pd.DataFrame(list(collection1.find({'producer_id': producer_id})))

    product = "Product"
    date = "Date"
    sales = "Sales"
    # Get a list of all products in the shop
    products = list(data[product].unique())

    data = pd.DataFrame(list(collection.find({'Product': {'$in': products}})))
    data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
    shopids = list(data['shop_id'].unique())

    if request.method == 'POST':
        currentdate = data[date].max()
        current_data = data[data[date] == currentdate]
        selected_product = request.POST.get('selected_product')
        product_data = current_data[current_data['Product'] == selected_product]
        # Visualize sales data by shop using Plotly
        forecast_dict = dict(
            zip(product_data['shop_id'], np.round(product_data['Sales'], 2)))

        fig = go.Figure(data=[
            go.Bar(x=list(forecast_dict.keys()), y=list(forecast_dict.values()))
        ])
        fig.update_layout(
            title='Sales by Shop',
            xaxis=dict(title='Shop ID'),
            yaxis=dict(title='Sales')
        )

        # Generate the Plotly plot
        plot_data = py.plot(fig, output_type='div')

        context = {'plot_data': plot_data, 'forecast': forecast_dict, 'selected_product': selected_product}
        return render(request, 'visualization/outvmpshopwise.html', context)


##########################################################################################################################################################



import plotly.offline as py
import plotly.graph_objs as go

def outvmoshop(request):
    if request.method == 'POST':
        shop_id = request.POST.get('selected_shop')
        data = pd.DataFrame(list(collection.find({'shop_id': shop_id})))
        data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
        product = "Product"
        date = "Date"

        # Get a list of all products in the shop
        products = list(data[product].unique())

        # Pass the list of products to the template
        currentdate = data[date].max()
        product_data = data[data[date] == currentdate]

        forecast_dict = dict(zip(product_data['Product'], np.round(product_data['Sales'], 2)))

        fig = go.Figure(data=[
            go.Bar(x=list(forecast_dict.keys()), y=list(forecast_dict.values()))
        ])
        fig.update_layout(
            title='Sales by Product',
            xaxis=dict(title='Product'),
            yaxis=dict(title='Sales')
        )

        # Convert the plot to HTML
        plot_data = py.plot(fig, output_type='div', include_plotlyjs=False)

        context = {
            'products': products,
            'plot_data': plot_data,
            'selected_shop': shop_id
        }

        return render(request, 'visualization/outvmoshop.html', context)


def outvmovms(request, selected_shop=None):
    if request.method == 'POST':
        shop_id = selected_shop

        data = pd.DataFrame(list(collection.find({'shop_id': shop_id})))
        data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
        products = "Product"

        # Get selected product from dropdown
        selected_product = request.POST.get('selected_product')
        startdate = request.POST.get('startdate')
        # Filter data to get sales of the selected product
        product_data = data[(data[products] == selected_product)
                            & (data['Date'] >= startdate)]

        months = pd.date_range(
            start=startdate, end=product_data['Date'].max(), freq='MS').strftime('%B %Y')

        forecast_dict = dict(zip(months, np.round(product_data['Sales'], 2)))

        fig = go.Figure(data=[
            go.Bar(x=list(forecast_dict.keys()), y=list(forecast_dict.values()))
        ])
        fig.update_layout(
            title='Sales Forecast',
            xaxis=dict(title='Date'),
            yaxis=dict(title='Sales')
        )

        # Convert the plot to HTML
        plot_data = py.plot(fig, output_type='div', include_plotlyjs=False)

        context = {'plot_data': plot_data, 'startdate': startdate, 'forecast': forecast_dict,
                   'selected_product': selected_product, 'selected_shop': shop_id, 'product_data': product_data['Sales']}
        return render(request, 'visualization/outvmovms.html', context)


def outvmovmscompare(request, selected_shop=None):
    if request.method == 'POST':
        shop_id = selected_shop
        data = pd.DataFrame(list(collection.find({'shop_id': shop_id})))
        data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
        product = "Product"
        date = "Date"
        currentdate = data[date].max()
        # Get selected product from dropdown
        comparedate = request.POST.get('comparedate')
        product_data = data[data[date] == currentdate]
        compare_data = data[data[date] == comparedate]

        # Select two columns from the dataframe
        product_data = product_data.loc[:, ['Product', 'Sales', 'Date']]
        compare_data = compare_data.loc[:, ['Product', 'Sales', 'Date']]

        fig = go.Figure()
        fig.add_trace(go.Line(
            x=compare_data['Product'],
            y=compare_data['Sales'],
            name='Compare Date'
        ))
        fig.add_trace(go.Line(
            x=product_data['Product'],
            y=product_data['Sales'],
            name='Current Date'
        ))

        fig.update_layout(
            title='Sales Comparison',
            xaxis=dict(title='Product'),
            yaxis=dict(title='Sales')
        )

        # Convert the plot to HTML
        plot_compare = py.plot(fig, output_type='div')
       
        context = {'plot_compare': plot_compare,
                   'comparedate': comparedate, 'selected_shop': shop_id}
        return render(request, 'visualization/outvmoVMScompare.html', context)


def outvmoprod(request):
    date = "Date"
    if request.method == 'POST':
        selected_product = request.POST.get('selected_product')
        data = pd.DataFrame(
            list(collection.find({'Product': selected_product})))
        data['Sales'] = pd.to_numeric(data['Sales'], errors='coerce')
        currentdate = data[date].max()
        current_data = data[data[date] == currentdate]
        product_data = current_data[current_data['Product']
                                    == selected_product]

        forecast_dict = dict(
            zip(product_data['shop_id'], np.round(product_data['Sales'], 2)))

        fig = go.Figure(data=[
            go.Bar(x=list(forecast_dict.keys()), y=list(forecast_dict.values()))
        ])
        fig.update_layout(
            title='Sales by Shop',
            xaxis=dict(title='Shop'),
            yaxis=dict(title='Sales')
        )

        # Convert the plot to HTML
        plot_data = py.plot(fig, output_type='div', include_plotlyjs=False)

        context = {'plot_data': plot_data, 'forecast': forecast_dict,
                   'selected_product': selected_product}
        return render(request, 'visualization/outvmoprod.html', context)


def outvmovmp(request, selected_product=None):
    sales_by_date = {}
    products = "Product"
    if request.method == 'POST':
        start_date = request.POST.get('startdate')

        collection = db.newsales
        product_data = pd.DataFrame(
            list(collection.find({products: selected_product})))
        product_data['Sales'] = pd.to_numeric(
            product_data['Sales'], errors='coerce')

        sales_by_date = product_data.groupby('Date')['Sales'].sum()

        months = pd.date_range(
            start=start_date, end=sales_by_date.index.max(), freq='MS').strftime('%B %Y')

        forecast_dict = dict(zip(months, np.round(sales_by_date.values, 2)))

        fig = go.Figure(data=[
            go.Bar(x=list(forecast_dict.keys()), y=list(forecast_dict.values()))
        ])
        fig.update_layout(
            title='Sales by Date',
            xaxis=dict(title='Date'),
            yaxis=dict(title='Sales')
        )

        # Convert the plot to HTML
        plot_data = py.plot(fig, output_type='div', include_plotlyjs=False)

        context = {'plot_data': plot_data, 'startdate': start_date, 'forecast': forecast_dict,
                   'selected_product': selected_product, 'product_data': product_data['Sales']}
        return render(request, 'visualization/outvmovmp.html', context)
