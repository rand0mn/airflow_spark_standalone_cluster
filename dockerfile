FROM apache/airflow:2.4.1

# USER root
# RUN chown -R airflow: /usr/bin/

# USER airflow

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         openjdk-11-jre-headless \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

EXPOSE 8080 5555 8793

USER airflow

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

RUN pip install --no-cache-dir pyspark=3.0.0 apache-airflow-providers-apache-spark==3.0.0 SQLAlchemy
