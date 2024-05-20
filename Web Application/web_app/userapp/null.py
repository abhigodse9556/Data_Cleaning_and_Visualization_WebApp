from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, render
from userapp.models import userFiles
import pandas as pd
import numpy as np 
import warnings
import os

def removenullforuser(request):
    cleaned_data = None
    modified_file_path = None
    html_table = None 
    if request.method == 'POST':
        try:
            file = request.FILES['file']
            loggeduser = request.POST.get('username')
            file_obj = userFiles.objects.create(
                uploaded_file_name=file, 
                uploaded_file=file, 
                username=loggeduser
            )
            file_path = file_obj.uploaded_file.path

            # Perform data cleaning and outlier handling
            if file.name.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file.name.lower().endswith('.json'):
                df = pd.read_json(file_path)
            elif file.name.lower().endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                return HttpResponseServerError("Unsupported file format. Only CSV, JSON, and XLSX (Excel) formats are supported.")

            # Convert DataFrame to HTML table
            html_table = df.to_html()

            find_and_fill_null_values(df)
            
            # Use the "downloads" directory as the default path
            downloads_directory = os.path.join(os.path.expanduser("~"), "Downloads")
            
            # Construct the modified file path in the "downloads" directory
            modified_file_path = os.path.join(downloads_directory, 'modified_file.csv')
            
            # Save the modified DataFrame to the "downloads" directory
            df.to_csv(modified_file_path, index=False)

            # Convert cleaned DataFrame to HTML for display
            cleaned_data = df.to_html()
            
            # Save the modified file to the model
            file_obj.modified_file_name = modified_file_path
            file_obj.modified_file = modified_file_path
            file_obj.save()

        except pd.errors.EmptyDataError:
            cleaned_data = "Error: The file is empty."
        except (pd.errors.ParserError, Exception) as e:
            cleaned_data = f"Error during data cleaning: {e}"

    return render(request, 'null_for_user.html', {'username':loggeduser, 'html_table': html_table, 'cleaned_data': cleaned_data, 'modified_file_path': modified_file_path})

def download_modified_userfile(request):
    modified_file_path = request.GET.get('modified_file_path', None)

    if modified_file_path:
        try:
            with open(modified_file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(modified_file_path)}'
                return response
        except FileNotFoundError:
            return HttpResponseServerError("Error: Modified file not found.")
    else:
        return HttpResponseServerError("Error: Modified file path not provided.")
    
    
    

def fill_null_values(df):
    
    
    for column in df.columns:
        if pd.api.types.is_object_dtype(df[column]):
            mode_value = df[column].mode().iloc[0]
            df[column].fillna(mode_value, inplace=True)
        elif pd.api.types.is_numeric_dtype(df[column]):
            if df[column].isnull().any():
                mean_value = df[column].mean()
                median_value = df[column].median()

                if df[column].skew() > 1:
                    df[column].fillna(median_value, inplace=True)
                else:
                    df[column].fillna(mean_value, inplace=True)
        elif pd.api.types.is_datetime64_any_dtype(df[column]):
            mode_value = df[column].mode().iloc[0]
            df[column].fillna(mode_value, inplace=True)


def find_and_fill_null_values(df):
    # Check for null values in the dataset
    null_values=['NaN','NA','NULL','N/A','Na','null','na','nul','Null','NALL',' ']
    df.replace(null_values, np.nan, inplace=True)
    null_values = df.isnull().sum()

    # Print rows with null values and the corresponding values
    null_rows = df[df.isnull().any(axis=1)]
    if not null_rows.empty:
        df.dropna(how='all', inplace=True)

    # Drop rows with all-null values
    df.dropna(how='all', inplace=True)

    # Drop columns with all-null values
    df.dropna(axis='columns', how='all', inplace=True)

    # Fill null values
    fill_null_values(df)