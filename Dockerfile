# To install packages including opendp_polars and opendp_logger 
FROM dtlam/sdd_server_opendp_polars:1.2 as sdd_server

# To install missing packages
RUN pip install smartnoise-sql==1.0.0
RUN pip install boto3

FROM sdd_server AS sdd_server_prod
COPY ./src/ /code/
# run as local server
# Disable this for now, as we do not run a mongodb instance
COPY ./configs/example_config.yaml /usr/sdd_poc_server/runtime.yaml
CMD ["python", "uvicorn_serve.py"]

FROM sdd_server AS sdd_server_dev
ENV PYTHONDONTWRITEBYTECODE 1
CMD ["python", "uvicorn_serve.py"]
# Empty, used for development.