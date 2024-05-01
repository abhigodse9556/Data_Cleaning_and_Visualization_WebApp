from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, render
from userapp.models import userFiles
import pandas as pd
import numpy as np 
import warnings
import os

def removeduplicatesforuser(request):
    cleaned_data = None
    modified_file_path = None
    html_table = None 
    if request.method == 'POST':
        try:
            file = request.FILES['file']
            loggeduser = request.POST.get('username')
            file_obj = userFiles.objects.create(
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
            
            df = remove_duplicates(df, axis=0)  # Remove duplicate rows
            df = remove_duplicates(df, axis=1)  # Remove duplicate columns
            
            # Use the "downloads" directory as the default path
            downloads_directory = os.path.join(os.path.expanduser("~"), "Downloads")
            
            # Construct the modified file path in the "downloads" directory
            modified_file_path = os.path.join(downloads_directory, 'modified_file.csv')
            
            # Save the modified DataFrame to the "downloads" directory
            df.to_csv(modified_file_path, index=False)

            # Convert cleaned DataFrame to HTML for display
            cleaned_data = df.to_html()
            
            # Save the modified file to the model
            file_obj.modified_file = modified_file_path
            file_obj.save()

        except pd.errors.EmptyDataError:
            cleaned_data = "Error: The file is empty."
        except pd.errors.ParserError as e:
            cleaned_data = f"Error during data cleaning: {e}"
        except Exception as e:
            cleaned_data = f"Error: {e}"

    return render(request, 'duplicate_for_user.html', {'username': loggeduser, 'html_table': html_table, 'cleaned_data': cleaned_data, 'modified_file_path': modified_file_path})

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
    
    
    

def remove_duplicates(df, axis):
    """
    Remove duplicate rows or columns from a DataFrame.

    Parameters:
    df (DataFrame): The DataFrame to remove duplicates from.
    axis (int, default=0): Axis along which to remove duplicates. 
        0 for rows, 1 for columns.

    Returns:
    DataFrame: DataFrame with duplicates removed.
    """
    if axis == 0:
        # Remove duplicate rows
        df_no_duplicates = df.drop_duplicates()
    elif axis == 1:
        # Remove duplicate columns
        df_no_duplicates = df.T.drop_duplicates().T
    else:
        raise ValueError("Axis value should be 0 for rows or 1 for columns.")
    
    return df_no_duplicates