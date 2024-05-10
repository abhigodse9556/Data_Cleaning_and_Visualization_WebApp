from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, render
from userapp.models import userFiles
import pandas as pd
import numpy as np
import warnings
import os

def uploaduserfile(request):
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

            # Perform data preprocessing
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
            
            # Perform data preprocessing tasks
            find_and_fill_null_values(df)
            df = remove_duplicates(df, axis=0)  # Remove duplicate rows
            df = remove_duplicates(df, axis=1)  # Remove duplicate columns
            
            # Construct the modified file path
            modified_file_path = os.path.join(settings.MEDIA_ROOT, 'modified_file.csv')
            
            # Save the modified DataFrame to the specified file path
            df.to_csv(modified_file_path, index=False)

            # Convert cleaned DataFrame to HTML for display
            cleaned_data = df.to_html()
            
            # Save the modified file to the model
            file_obj.modified_file_name = modified_file_path
            file_obj.modified_file = modified_file_path
            file_obj.save()
            
        except pd.errors.EmptyDataError:
            cleaned_data = "Error: The file is empty."
        except pd.errors.ParserError as e:
            cleaned_data = f"Error during data parsing: {e}"
        except Exception as e:
            cleaned_data = f"Error: {e}"

    return render(request, 'automatic_for_user.html', {'username':loggeduser, 'html_table': html_table, 'cleaned_data': cleaned_data, 'modified_file_path': modified_file_path})

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

        if method == 'custom':
            # Implement custom outlier handling method here
            custom_handled_df = custom_handle_outliers(df, z_scores)
            if not custom_handled_df.empty:
                return custom_handled_df

    return df

def remove_duplicates(df, axis=0):
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


def custom_handle_outliers(df, z_scores):
    # Example of a custom outlier handling method
    # Identify and handle outliers not addressed by existing methods
    # Here, we can identify outliers based on a specific condition and handle them accordingly
    # For example, replacing outliers with the median value
    
    # Find rows where all z-scores are greater than 3 (extreme outliers)
    extreme_outliers = df[(z_scores.abs() > 3).all(axis=1)]
    
    # Handle extreme outliers by replacing them with median values
    if not extreme_outliers.empty:
        median_values = df.median()
        for col in df.columns:
            df.loc[extreme_outliers.index, col] = median_values[col]
    
    return df

date_formats_list = [
    '%Y-%m-%d', '%Y/%m/%d', '%Y%m%d', '%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y','%d-%m-%Y',
    '%d/%m/%y', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%m/%d/%Y %H:%M:%S',
    '%m/%d/%Y %H:%M'
]

def convert_data_types(df, date_formats=date_formats_list):
    df_converted = df.copy()

    data_type_mapping = {}

    for column in df_converted.columns:
        if pd.api.types.is_numeric_dtype(df_converted[column]):
            if pd.api.types.is_integer_dtype(df_converted[column]):
                data_type_mapping[column] = 'int'
            elif pd.api.types.is_float_dtype(df_converted[column]):
                data_type_mapping[column] = 'float'
        elif pd.api.types.is_datetime64_any_dtype(df_converted[column]):
            data_type_mapping[column] = 'datetime'
        elif pd.api.types.is_bool_dtype(df_converted[column]):
            data_type_mapping[column] = 'bool'
        else:
            data_type_mapping[column] = 'object'

    for column, data_type in data_type_mapping.items():
        if data_type == 'datetime' and column in df.columns:
            if date_formats is not None:
                for date_format in date_formats:
                    try:
                        df_converted[column] = pd.to_datetime(df_converted[column], errors='coerce', format=date_format)
                        break  
                    except ValueError:
                        continue  
            else:
                df_converted[column] = pd.to_datetime(df_converted[column], errors='coerce')

    for column, data_type in data_type_mapping.items():
        if data_type == 'int':
            df_converted[column] = pd.to_numeric(df_converted[column], errors='coerce').astype('Int64')
        elif data_type == 'float':
            df_converted[column] = pd.to_numeric(df_converted[column], errors='coerce')
        elif data_type == 'bool':
            df_converted[column] = df_converted[column].astype(bool)
        elif data_type == 'object':
            df_converted[column] = df_converted[column].astype(str)

    return df_converted



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

    # Identify and drop duplicate rows
    duplicate_rows = df[df.duplicated()]
    if not duplicate_rows.empty:

    # Drop duplicate rows
     df.drop_duplicates(inplace=True)

     # Call the convert_data_types function
     converted_df = convert_data_types(df)

    handle_outliers(df)