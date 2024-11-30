FROM apache/airflow:2.9.2

USER root


ENV PATH=/root/.local/bin:$PATH

RUN getent group airflow &>/dev/null || groupadd -r airflow
RUN id -u airflow &>/dev/null || useradd -r -m airflow
RUN mkdir -p /usr/local/airflow/dags /usr/local/opt/airflow/logs
RUN chown -R airflow:airflow /usr/local/airflow


USER airflow


RUN pip install airflow-clickhouse-plugin



RUN airflow db init && echo "DB initialised at $(date)"

RUN airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin && echo "User created at $(date)"


COPY yurii_nitochkin_lab02.py /usr/local/airflow/dags/yurii_nitochkin_lab02.py

WORKDIR /usr/local/airflow
