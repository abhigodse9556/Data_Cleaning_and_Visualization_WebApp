import warnings
from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, render
from userapp.models import userFiles
import pandas as pd
import numpy as np 
import warnings
import os

def removeoutlierforuser(request):
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

            handle_outliers(df)
            
            # Use the "downloads" directory as the default path
            downloads_directory = os.path.join(os.path.expanduser("~"), "Downloads")
            
            # Construct the modified file path in the "downloads" directory
            modified_file_path = os.path.join(settings.MEDIA_ROOT, 'modified_file.csv')
            
            # Save the modified DataFrame to the "downloads" directory
            df.to_csv(modified_file_path, index=False)

            # Convert cleaned DataFrame to HTML for display
            cleaned_data = df.to_html()
            
            # Save the modified file to the model
            file_obj.modified_file = modified_file_path
            file_obj.save()
            
        except pd.errors.EmptyDataError:
            cleaned_data = "Error: The file is empty."
        except (pd.errors.ParserError, Exception) as e:
            cleaned_data = f"Error during data cleaning: {e}"

    return render(request, 'outlier_for_user.html', {'username': loggeduser, 'html_table': html_table, 'cleaned_data': cleaned_data, 'modified_file_path': modified_file_path})


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

def handle_outliers(df, method='drop'):
    max_rows_to_drop = int(df.shape[0] * 0.1)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        z_scores = (df - df.mean(numeric_only=True)) / df.std(numeric_only=True)
    outlier_rows = df[(z_scores.abs() > 3).any(axis=1)]

    if not outlier_rows.empty:
        if method == 'trim':
            trimmed_df = df[(z_scores.abs() <= 3).all(axis=1)]
            if not trimmed_df.empty:
                return trimmed_df

        if method == 'cap':
            cap_value = df.mean() + 3 * df.std()
            capped_df = df.clip(lower=df.min(), upper=cap_value, axis=1)
            if not capped_df.empty:
                return capped_df

        if method == 'impute':
            imputed_df = df.mask(z_scores.abs() > 3, df.mean(), axis=1)
            if not imputed_df.empty:
                return imputed_df

        if method == 'drop':
            max_rows_to_drop = min(max_rows_to_drop, len(outlier_rows))
            if max_rows_to_drop > 0:
                df.drop(outlier_rows.head(max_rows_to_drop).index, inplace=True)
                return df

    return df