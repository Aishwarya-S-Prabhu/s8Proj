import base64
import urllib
import io
import pandas as pd
import pymongo
import numpy as np
from django.shortcuts import render
import itertools
from statsmodels.tsa.statespace.sarimax import SARIMAX

import matplotlib.pyplot as plt
from django.core.mail import send_mail
from user.models import Profile
import simplyfyproject.settings as settings

client = pymongo.MongoClient(
    'mongodb+srv://chainaid:7XKgw7yjs1ZBkkEn@cluster0.1n1dhzf.mongodb.net/?retryWrites=true&w=majority')
db = client['ChainAid']

# collection object
collection = db['shopsales']


def dfshop(request):
    user = request.user
    currentUser = Profile.objects.filter(staff=user).first()

    shop_id = currentUser.branchID
    print("Shop ID:"+shop_id)

    # Load data from MongoDB
    # Replace 'your_db_name' with your actual MongoDB database name and 'your_collection_name' with your actual collection name
   # data = pd.DataFrame(list(db.collection.find({'shop_id': shop_id})))
    data = pd.DataFrame(list(collection.find({'shop_id': shop_id})))
    print(data)
    product = "Product"
    # Get a list of all products in the shop

    products = list(data[product].unique())
    # Pass the list of products to the template
    context = {'products': products, }
    return render(request, 'forecasting/dfshop.html', context)


def outdfs(request):
    # shop_id = request.user.shop_id

    user = request.user
    currentUser = Profile.objects.filter(staff=user).first()

    shop_id = currentUser.branchID
    data = pd.DataFrame(list(collection.find({'shop_id': shop_id})))
    products = "Product"
    if request.method == 'POST':
        # Get selected product from dropdown
        selected_product = request.POST.get('selected_product')

        # Filter data to get sales of the selected product
        product_data = data[data[products] == selected_product]
      #  product_data = produc_data.iloc[:-12, :]
        # Define parameter grid for hyperparameter tuning
        p = d = q = range(0, 2)
        seasonal_pdq = [(0, 0, 0, 12), (0, 1, 0, 12), (1, 0, 0, 12), (1, 1, 0, 12),
                        (0, 0, 1, 12), (0, 1, 1, 12), (1, 0, 1, 12), (1, 1, 1, 12)]

        best_aic = np.inf
        best_order = None
        best_seasonal_order = None
        # Hyperparameter tuning
        for i in p:
            for j in d:
                for k in q:
                    for l in seasonal_pdq:
                        try:
                            product_data['Sales'] = pd.to_numeric(
                                product_data['Sales'], errors='coerce')

                            model = SARIMAX(product_data['Sales'], order=(
                                i, j, k), seasonal_order=l, enforce_stationarity=False, enforce_invertibility=False)
                            results = model.fit()
                            print(results.aic, i, j, k, l)

                            if results.aic < best_aic:
                                best_aic = results.aic
                                best_order = (i, j, k)
                                best_seasonal_order = l
                        except:
                            continue
        print(best_order)
        print(best_seasonal_order)
      #  model = SARIMAX(product_data['Sales'], order=(1, 1, 1), seasonal_order=(1, 1, 0, 12)).fit()
        product_data['Sales'] = pd.to_numeric(
            product_data['Sales'], errors='coerce')
        model = SARIMAX(product_data['Sales'], order=best_order, seasonal_order=best_seasonal_order,
                        enforce_stationarity=False, enforce_invertibility=False).fit()

        forecast = model.forecast(steps=12)

        # Create a list of months for the forecast
        months = pd.date_range(start=product_data['Date'].max(
        ), periods=12, freq='MS').strftime('%B %Y')

        # Combine forecast and months into a dictionary
        forecast_dict = dict(zip(months, np.round(forecast, 2)))

        threshold_dict = {'A': 13600,
                          'B': 1000000,
                          'C': 2000000}
       
        first_key = next(iter(forecast_dict))
        print(settings.EMAIL_HOST_USER,settings.RECIPIENT_ADDRESS)
        if forecast_dict[first_key] <= threshold_dict[selected_product]:
            send_mail(
                subject='Warning alert',
                message="Sales value of product {} is below set threshold value".format(selected_product), 
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.RECIPIENT_ADDRESS])

        # print(forecast_dict)

        plot_data = generate_plot(forecast_dict)

        # Pass the forecast dictionary and the list of products to the template
        context = {'plot_data': plot_data, 'forecast': forecast_dict,
                   'selected_product': selected_product, 'shopid': shop_id, 'product_data': product_data['Sales']}
        return render(request, 'forecasting/outDFS.html', context)


def dfowner(request):

    data = pd.DataFrame(list(collection.find()))
    print(data)
    product = "Product"
    shop_id = "shop_id"
    # Get a list of all products in the shop
    products = list(data[product].unique())
    shop_ids = list(data[shop_id].unique())

    # Pass the list of products to the template
    context = {'products': products, 'shop_ids': shop_ids}
    return render(request, 'forecasting/dfowner.html', context)


def generate_plot(forecast_dict):
    # Create a figure and axis object
    fig, ax = plt.subplots(figsize=(11, 14))

    # Plot the forecast
    ax.plot(forecast_dict.keys(), forecast_dict.values())

    # Set the title and labels
    ax.set_title('Forecast Graph')
    ax.set_xlabel('Month')
    ax.set_ylabel('Demand')

    # Rotate x-axis labels
    plt.xticks(rotation='vertical')
    # Save the plot to a temporary buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the plot as base64 string
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')

    return plot_data


def outdfo(request):
    if request.method == 'POST':
        # Get selected shop from dropdown
        selected_shop = request.POST.get('selected_shop')
        # Get selected product from dropdown
        selected_product = request.POST.get('selected_product')
        data = pd.DataFrame(list(collection.find()))
        # Filter data to get sales of the selected product
        product = "Product"
        shop_id = "shop_id"
        produc_data = data[data[product] == selected_product]
        print(produc_data)
        product_data = produc_data[produc_data[shop_id] == selected_shop]
        print(product_data)
        # Define parameter grid for hyperparameter tuning
        p = d = q = range(0, 2)
        seasonal_pdq = [(0, 0, 0, 12), (0, 1, 0, 12), (1, 0, 0, 12), (1, 1, 0, 12),
                        (0, 0, 1, 12), (0, 1, 1, 12), (1, 0, 1, 12), (1, 1, 1, 12)]

        best_aic = np.inf
        best_order = None
        best_seasonal_order = None
        # Hyperparameter tuning

        for i in p:
            for j in d:
                for k in q:
                    for l in seasonal_pdq:
                        try:
                            product_data['Sales'] = pd.to_numeric(
                                product_data['Sales'], errors='coerce')

                            model = SARIMAX(product_data['Sales'], order=(
                                i, j, k), seasonal_order=l, enforce_stationarity=False, enforce_invertibility=False)
                            results = model.fit()
                            print(results.aic, i, j, k, l)

                            if results.aic < best_aic:
                                best_aic = results.aic
                                best_order = (i, j, k)
                                best_seasonal_order = l
                        except:
                            continue
        print(best_order)
        print(best_seasonal_order)
      #  model = SARIMAX(product_data['Sales'], order=(1, 1, 1), seasonal_order=(1, 1, 0, 12)).fit()
        product_data['Sales'] = pd.to_numeric(
            product_data['Sales'], errors='coerce')

        model = SARIMAX(product_data['Sales'], order=best_order, seasonal_order=best_seasonal_order,
                        enforce_stationarity=False, enforce_invertibility=False).fit()

        # Use the model to predict demand for the next 12 months
        forecast = model.forecast(steps=12)

        # Create a list of months for the forecast
        months = pd.date_range(start=product_data['Date'].max(
        ), periods=12, freq='MS').strftime('%B %Y')

        # Combine forecast and months into a dictionary
        forecast_dict = dict(zip(months, np.round(forecast, 2)))

        # Generate the plot
        plot_data = generate_plot(forecast_dict)

        context = {'plot_data': plot_data, 'forecast': forecast_dict,
                   'selected_product': selected_product, 'shopid': shop_id, 'selected_shop': selected_shop}
        return render(request, 'forecasting/outDFO.html', context)
