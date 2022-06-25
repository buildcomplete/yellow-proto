FROM tiangolo/uvicorn-gunicorn-fastapi


# Add testing framework, can it be made conditional?
RUN pip install py pytest-cov

# For reading parquet file
RUN pip install pandas
RUN pip install pyarrow

# Create main folder for attached storage
RUN mkdir /storage
WORKDIR /App
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]