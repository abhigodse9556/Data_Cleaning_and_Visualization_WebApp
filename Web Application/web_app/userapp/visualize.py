import shutil
import warnings
import pandas as pd
import numpy as np
import os
from django.shortcuts import render
from autoviz.AutoViz_Class import AutoViz_Class

# Date formats for date conversion
date_formats_list = [
    '%Y-%m-%d', '%Y/%m/%d', '%Y%m%d', '%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y', '%d-%m-%Y',
    '%d/%m/%y', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M'
]

def visualizeData(request):
    loggeduser = None
    if request.method == 'POST':
        loggeduser = request.POST.get('username')
        file = request.FILES['file']
        
        # Save the uploaded file
        file_path = os.path.join('uploads', file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Call your data cleaning function
        updated_dataset = find_and_fill_null_values(file_path)
        
        # Save the updated dataset to a CSV file
        cleaned_file_path = 'updated_dataset.csv'
        updated_dataset.to_csv(cleaned_file_path, index=False)
        
        # Call AutoViz for automatic visualization
        AV = AutoViz_Class()
        dfte = AV.AutoViz(cleaned_file_path, sep=",", verbose=2)
        
        # Create directories for storing plots
        filename = "AutoViz_Plots"
        source_directory = os.path.join(filename, 'AutoViz')
        destination_directory = os.path.join('static', 'AutoViz_Plots')
        os.makedirs(destination_directory, exist_ok=True)
        
        # Copy AutoViz-generated SVG files to the destination directory
        for file_name in os.listdir(source_directory):
            if file_name.endswith('.svg'):
                shutil.copy(os.path.join(source_directory, file_name), destination_directory)
        
        plot_files = [f for f in os.listdir(destination_directory) if f.endswith('.svg')]
        
        # Pass the cleaned dataset and visualization data to the template
        context = {
            'dataset': updated_dataset.to_html(classes='table table-striped'),
            'plot_files': plot_files,
            'username': loggeduser
        }
        
        return render(request, 'visualize.html', context)
    else:
        return render(request, 'visualize.html', {'username': loggeduser})

def visualize_statistical_data(df):
    if isinstance(df, str):
        df = pd.read_csv(df)  # Read DataFrame from file path if input is a string

    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input is not a DataFrame or valid file path.")

    numerical_columns = df.select_dtypes(include=['int', 'float']).columns
    print("Statistical Information:")
    display(df[numerical_columns].describe())

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

def fill_null_values(df):
    print("\nData Types Before Filling Null Values:")
    print(df.dtypes)

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
        print("\nOutlier rows:")
        print(outlier_rows)

        if method == 'trim':
            trimmed_df = df[(z_scores.abs() <= 3).all(axis=1)]
            if not trimmed_df.empty:
                print("\nTrimming successful. Updated dataset:")
                print(trimmed_df)
                return trimmed_df

        if method == 'cap':
            cap_value = df.mean() + 3 * df.std()
            capped_df = df.clip(lower=df.min(), upper=cap_value, axis=1)
            if not capped_df.empty:
                print("\nCapping successful. Updated dataset:")
                print(capped_df)
                return capped_df

        if method == 'impute':
            imputed_df = df.mask(z_scores.abs() > 3, df.mean(), axis=1)
            if not imputed_df.empty:
                print("\nImputation successful. Updated dataset:")
                print(imputed_df)
                return imputed_df

        if method == 'drop':
            max_rows_to_drop = min(max_rows_to_drop, len(outlier_rows))
            if max_rows_to_drop > 0:
                df.drop(outlier_rows.head(max_rows_to_drop).index, inplace=True)
                print("\nDropping outlier rows. Updated dataset:")
                print(df)
                return df

        print("\nNo effective method found to handle outliers. No action taken.")
    else:
        print("\nNo outlier rows found.")

def find_and_fill_null_values(dataset):
    df = pd.read_csv(dataset) if dataset.endswith('.csv') else pd.read_json(dataset)

    null_values = ['NaN', 'NA', 'NULL', 'N/A', 'Na', 'null', 'na', 'nul', '']
    df.replace(null_values, np.nan, inplace=True)

    null_values_total = df.isnull().sum().sum()
    print("Null values in the dataset:", null_values_total)

    print("\nStatistical Information:")
    print(df.describe())

    null_rows = df[df.isnull().any(axis=1)]
    if not null_rows.empty:
        print("\nRows with null values:")
        print(null_rows)

        initial_rows = df.shape[0]
        print("\nDropping rows with all-null values:")
        df.dropna(how='all', inplace=True)

        remaining_rows = df.shape[0]
        rows_deleted = initial_rows - remaining_rows
        print(f"Number of rows deleted: {rows_deleted}")

        initial_columns = df.shape[1]
        print("\nDropping columns with all-null values:")
        df.dropna(axis='columns', how='all', inplace=True)

        remaining_columns = df.shape[1]
        columns_deleted = initial_columns - remaining_columns
        print(f"Number of columns deleted: {columns_deleted}")

        print("\nFilling null values:")
        fill_null_values(df)
        print("\nUpdated dataset after dropping and filling null values:")
        print(df)

    duplicate_rows = df[df.duplicated()]
    if not duplicate_rows.empty:
        print("\nDuplicate rows:")
        print(duplicate_rows)
        df.drop_duplicates(inplace=True)
        print("\nDropping duplicate rows. Updated dataset:")
        print(df)

    handle_outliers(df)
    df = convert_data_types(df)

    print("\nData Types After Conversion:")
    print(df.dtypes)
    
    return df
