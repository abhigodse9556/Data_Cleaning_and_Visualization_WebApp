from django.http import HttpResponseServerError
from django.shortcuts import render
from home.models import File
import pandas as pd
import warnings

def upload(request):
    cleaned_data = None
    download_link = None
    if request.method == 'POST':
        try:
            file = request.FILES['file']
            file_obj = File.objects.create(file=file)
            file_path = file_obj.file.path

            # Perform data cleaning and outlier handling
            if file.name.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file.name.lower().endswith('.json'):
                df = pd.read_json(file_path)
            else:
                return HttpResponseServerError("Unsupported file format. Only CSV and JSON formats are supported.")

            find_and_fill_null_values(df)
            handle_outliers(df)

            # Convert cleaned DataFrame to HTML for display
            cleaned_data = df.to_html()

        except pd.errors.EmptyDataError:
            cleaned_data = "Error: The file is empty."
        except (pd.errors.ParserError, Exception) as e:
            cleaned_data = f"Error during data cleaning: {e}"

    return render(request, 'upload.html', {'cleaned_data': cleaned_data, 'download_link': download_link})

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

    print("\nData Types After Filling Null Values:")
    print(df.dtypes)

def handle_outliers(df):
    # Z-score method to detect outliers
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        z_scores = (df - df.mean(numeric_only=True)) / df.std(numeric_only=True)
    outlier_rows = df[(z_scores.abs() > 3).any(axis=1)]

    if not outlier_rows.empty:
        print("\nOutlier rows:")
        print(outlier_rows)

        # Drop outlier rows
        df.drop(outlier_rows.index, inplace=True)
        print("\nDropping outlier rows. Updated dataset:")
        print(df)

def find_and_fill_null_values(df):
    # Check for null values in the dataset
    null_values = df.isnull().sum()

    # Print the columns with null values and their count
    print("Null values in the dataset:")
    print(null_values[null_values > 0])

    # Print rows with null values and the corresponding values
    null_rows = df[df.isnull().any(axis=1)]
    if not null_rows.empty:
        print("\nRows with null values:")
        print(null_rows)

        # Drop rows with all-null values
        print("\nDropping rows with all-null values:")
        df.dropna(how='all', inplace=True)

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
    handle_outliers(df)

