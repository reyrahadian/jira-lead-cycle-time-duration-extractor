import boto3
import os
from src.config.app_settings import AppSettings

def download_csv_from_s3():
    """Downloads the CSV file from S3 if bucket name is set."""
    app_settings = AppSettings()
    bucket_name = app_settings.S3_BUCKET_NAME
    csv_path = app_settings.REPORTING_CSV_PATH

    if not bucket_name:
        print("S3 bucket name not set, skipping S3 download")
        return

    if not csv_path:
        print("CSV path not set, skipping S3 download")
        return

    try:
        s3_client = boto3.client('s3')

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        # Download the file
        print(f"Downloading CSV from S3 bucket {bucket_name} to {csv_path}")
        s3_client.download_file(
            bucket_name,
            os.path.basename(csv_path),  # Use filename as S3 key
            csv_path
        )
        print("Successfully downloaded CSV from S3")

    except Exception as e:
        print(f"Error downloading from S3: {str(e)}")