FROM tiangolo/uvicorn-gunicorn-fastapi

# For reading parquet file
RUN pip install pandas
RUN pip install pyarrow

# Create main folder for attached storage
RUN mkdir /storage
WORKDIR /App
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]