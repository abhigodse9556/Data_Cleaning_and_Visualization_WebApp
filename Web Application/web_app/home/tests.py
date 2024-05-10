from django.test import TestCase

# Create your tests here.

import warnings 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from autoviz.AutoViz_Class import AutoViz_Class

from django.shortcuts import render
from autoviz.AutoViz_Class import AutoViz_Class

def data_analysis(request):
    # Call your data cleaning function
    updated_dataset = find_and_fill_null_values(r"D:\Data Processing App\test files\height-weight.csv")
    
    # Generate statistical data visualization
    visualize_statistical_data(updated_dataset)
    
    # Call AutoViz for automatic visualization
    AV = AutoViz_Class()
    dfte = AV.AutoViz('path_to_your_dataset.csv', sep=",")
    
    # Pass the cleaned dataset and visualization data to the template
    context = {
        'dataset': updated_dataset.to_html(),
        'visualization': dfte
    }
    
    # Render the template with the context
    return render(request, 'analysis.html', context)

def visualize_statistical_data(df):
    """
    Visualizes statistical data in graphical form.

    Parameters:
    df (DataFrame or str): Input DataFrame containing numerical columns or file path to the DataFrame.

    Returns:
    None
    """
    if isinstance(df, str):
        df = pd.read_csv(df)  # Read DataFrame from file path if input is a string

    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input is not a DataFrame or valid file path.")

    # Filter numerical columns for visualization
    numerical_columns = df.select_dtypes(include=['int', 'float']).columns

    # Show statistical information in table format
    print("Statistical Information:")
    display(df[numerical_columns].describe())



date_formats_list = [
    '%Y-%m-%d', '%Y/%m/%d', '%Y%m%d', '%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y','%d-%m-%Y',
    '%d/%m/%y', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%m/%d/%Y %H:%M:%S',
    '%m/%d/%Y %H:%M'
]


def convert_data_types(df, date_formats=date_formats_list):
    """
    Automatically converts data types of DataFrame columns to the most appropriate type.

    Parameters:
    df (DataFrame): Input DataFrame.
    date_formats (list of str, optional): List of date formats to parse date columns.

    Returns:
    DataFrame: DataFrame with converted data types.
    """

    # Copy DataFrame to avoid modifying the original DataFrame
    df_converted = df.copy()

    # Define dictionary to map each column to its detected data type
    data_type_mapping = {}

    for column in df_converted.columns:
        # Detect data type for each column
        if pd.api.types.is_numeric_dtype(df_converted[column]):
            # Numeric data type detected
            if pd.api.types.is_integer_dtype(df_converted[column]):
                # Integer data type detected
                data_type_mapping[column] = 'int'
            elif pd.api.types.is_float_dtype(df_converted[column]):
                # Float data type detected
                data_type_mapping[column] = 'float'
        elif pd.api.types.is_datetime64_any_dtype(df_converted[column]):
            # Datetime data type detected
            data_type_mapping[column] = 'datetime'
        elif pd.api.types.is_bool_dtype(df_converted[column]):
            # Boolean data type detected
            data_type_mapping[column] = 'bool'
        else:
            # Assume object (string) data type if none of the above match
            data_type_mapping[column] = 'object'

    # Convert date columns to datetime with specified date formats
    for column, data_type in data_type_mapping.items():
        if data_type == 'datetime' and column in df.columns:
            if date_formats is not None:
                for date_format in date_formats:
                    try:
                        df_converted[column] = pd.to_datetime(df_converted[column], errors='coerce', format=date_format)
                        break  # Stop iteration if successful
                    except ValueError:
                        continue  # Continue to next format if parsing fails
            else:
                df_converted[column] = pd.to_datetime(df_converted[column], errors='coerce')

    # Convert other data types
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
            # For object (string) columns, fill null values with the mode
            mode_value = df[column].mode().iloc[0]
            df[column].fillna(mode_value, inplace=True)
        elif pd.api.types.is_numeric_dtype(df[column]):
            # For numeric columns, choose between mean and median based on data distribution
            if df[column].isnull().any():
                mean_value = df[column].mean()
                median_value = df[column].median()

                if df[column].skew() > 1:
                    # If the data is right-skewed, use median
                    df[column].fillna(median_value, inplace=True)
                else:
                    # Otherwise, use mean
                    df[column].fillna(mean_value, inplace=True)
        elif pd.api.types.is_datetime64_any_dtype(df[column]):
            # For date columns, fill null values with the mode
            mode_value = df[column].mode().iloc[0]
            df[column].fillna(mode_value, inplace=True)
        # Add more conditions for other data types if needed
    
    

def handle_outliers(df, method='drop'):
    # Calculate the maximum number of rows to be dropped (10% of dataset)
    max_rows_to_drop = int(df.shape[0] * 0.1)

    # Z-score method to detect outliers
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        z_scores = (df - df.mean(numeric_only=True)) / df.std(numeric_only=True)
    outlier_rows = df[(z_scores.abs() > 3).any(axis=1)]

    if not outlier_rows.empty:
        print("\nOutlier rows:")
        print(outlier_rows)

        if method == 'trim':
            print("\nAttempting to trim outlier values.")
            # Trim outlier values
            trimmed_df = df[(z_scores.abs() <= 3).all(axis=1)]
            if not trimmed_df.empty:
                print("\nTrimming successful. Updated dataset:")
                print(trimmed_df)
                return trimmed_df
            else:
                print("\nTrimming failed to handle outliers effectively. Proceeding to other methods.")

        if method == 'cap':
            print("\nAttempting to cap outlier values.")
            # Cap outlier values
            cap_value = df.mean() + 3 * df.std()
            capped_df = df.clip(lower=df.min(), upper=cap_value, axis=1)
            if not capped_df.empty:
                print("\nCapping successful. Updated dataset:")
                print(capped_df)
                return capped_df
            else:
                print("\nCapping failed to handle outliers effectively. Proceeding to other methods.")

        if method == 'impute':
            print("\nAttempting to impute outlier values.")
            # Impute outlier values with mean
            imputed_df = df.mask(z_scores.abs() > 3, df.mean(), axis=1)
            if not imputed_df.empty:
                print("\nImputation successful. Updated dataset:")
                print(imputed_df)
                return imputed_df
            else:
                print("\nImputation failed to handle outliers effectively. Proceeding to other methods.")

        if method == 'drop':
            max_rows_to_drop = min(max_rows_to_drop, len(outlier_rows))
            if max_rows_to_drop > 0:
                print(f"\nPerforming drop operation on {max_rows_to_drop} outlier rows.")
                # Drop outlier rows
                df.drop(outlier_rows.head(max_rows_to_drop).index, inplace=True)
                print("\nDropping outlier rows. Updated dataset:")
                print(df)
                return df
            else:
                print("\nNumber of outlier rows exceeds the threshold. No rows dropped.")

        print("\nNo effective method found to handle outliers. No action taken.")
    else:
        print("\nNo outlier rows found.")


# Example usage:
# handle_outliers(df, method='drop')


def find_and_fill_null_values(dataset):
    # Read the dataset using pandas
    df = pd.read_csv(dataset) if dataset.endswith('.csv') else pd.read_json(dataset)

    # Check for null values in the dataset
    null_values=['NaN','NA','NULL','N/A','Na','null','na','nul','']
    df.replace(null_values, np.nan, inplace=True)
    
    null_values_total = df.isnull().sum().sum()

    # Print the columns with null values and their count
    print("Null values in the dataset:", null_values_total)

    # Print statistical information
    print("\nStatistical Information:")
    print(df.describe())

    # Print rows with null values and the corresponding values
    null_rows = df[df.isnull().any(axis=1)]
    if not null_rows.empty:
        print("\nRows with null values:")
        print(null_rows)

        # Get the initial number of rows
        initial_rows = df.shape[0]

        # Drop rows with all-null values
        print("\nDropping rows with all-null values:")
        df.dropna(how='all', inplace=True)
        
        # Get the number of rows after dropping
        remaining_rows = df.shape[0]

        # Calculate the number of rows deleted
        rows_deleted = initial_rows - remaining_rows

        # Print the number of rows deleted
        print(f"Number of rows deleted: {rows_deleted}")

        # Get the initial number of columns
        initial_columns = df.shape[1]
        
        # Drop columns with all-null values
        print("\nDropping columns with all-null values:")
        df.dropna(axis='columns', how='all', inplace=True)
        
        # Get the number of columns after dropping
        remaining_columns = df.shape[1]

        # Calculate the number of columns deleted
        columns_deleted = initial_columns - remaining_columns

        # Print the number of columns deleted
        print(f"Number of columns deleted: {columns_deleted}")

        # Fill null values
        print("\nFilling null values:")
        fill_null_values(df)

        # Display the updated dataset after dropping and filling null values
        print("\nUpdated dataset after dropping and filling null values:")
        print(df)

    # Identify and drop duplicate rows
    duplicate_rows = df[df.duplicated()]
    if not duplicate_rows.empty:
        print("\nDuplicate rows:")
        print(duplicate_rows)

        # Drop duplicate rows
        df.drop_duplicates(inplace=True)
        print("\nDropping duplicate rows. Updated dataset:")
        print(df)

    # Handle outliers
    handle_outliers(df)
    
    # Convert data types after cleaning
    df = convert_data_types(df)
    
    # Print data types after conversion
    print("\nData Types After Conversion:")
    print(df.dtypes)
    
    # Return the cleaned dataset
    return df




# Example usage
updated_dataset = find_and_fill_null_values(r"D:\Data Processing App\test files\height-weight.csv")



updated_dataset.to_csv('updated_dataset.csv', index=False)

# Visualize statistical data
#visualize_statistical_data('updated_dataset.csv')





AV=AutoViz_Class()

dfte=AV.AutoViz('updated_dataset.csv',sep=",")