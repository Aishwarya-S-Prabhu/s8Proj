import os
from django.shortcuts import render
from .models import *
from .forms import *
import pandas as pd
from datetime import datetime
from io import StringIO
from pymongo import MongoClient
import csv
from user.models import Profile



def clean_csv(csv_file,shop_id):
    # Read in the CSV file
    df = pd.read_csv(csv_file)
    # delete some columns
    df = df[['Product', 'Sales']]

    df['Sales'] = pd.to_numeric(
        df['Sales'], errors='coerce')    
    # Drop any rows with missing data
    df = df.dropna()

    # Remove any leading or trailing whitespace from column names
    df.columns = df.columns.str.strip()

    # Convert any string columns to lowercase
    string_columns = df.select_dtypes(include='object').columns
    # df[string_columns] = df[string_columns].apply(lambda x: x.str.lower())

    # Grouping and calculatig total sales
    sum_df = df.groupby('Product')['Sales'].sum().reset_index()

    # get today's datetime
    now = datetime.now()
    first_day_of_month = now.replace(day=1)
    # Adding date column
    sum_df['Date'] = first_day_of_month.date()
    sum_df['shop_id']=shop_id

    # If merge required
    result_df = pd.DataFrame()
   
    result_df = sum_df

    # Return the cleaned DataFrame
    return result_df.to_csv(index=False)



def upload_csv(request, pk=None):
    user = request.user
    currentUser = Profile.objects.filter(staff=user).first()
    print(currentUser)
    connection_string = 'mongodb+srv://chainaid:7XKgw7yjs1ZBkkEn@cluster0.1n1dhzf.mongodb.net/?retryWrites=true&w=majority'
    client = MongoClient(connection_string)

    db = client['ChainAid']

    # collection object
    collection = db['shopsales']
    form = CsvFileForm()
    if request.method == 'POST':
        form = CsvFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Extracting information from the submitted form
            csvFile = form.cleaned_data['csv_file']
            

            cleaned_csv_str = clean_csv(csvFile,currentUser.branchID)
            cleaned_csv = StringIO(cleaned_csv_str)
            

            # MONGODB WORKS HERE
            # Create a CSV reader object
            reader = csv.DictReader(cleaned_csv)

            # Loop through each row of the CSV file
            for row in reader:
                # Insert the row as a document into the collection
                collection.insert_one(row)

    context = {'form': form}
    return render(request, 'csvs/upload.html', context)
