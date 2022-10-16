from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from datetime import datetime, timedelta
import sys, os, re, pprint, subprocess

###############################################
# Parameters
###############################################
spark_master = "spark://spark:7077"
spark_app_name = "Spark Hello World"
file_path = "/usr/local/spark/resources/data/airflow.cfg"

ETH0_IP = subprocess.check_output(["hostname", "-i"]).decode(encoding='utf-8').strip()
ETH0_IP = re.sub(fr'\s*127.0.0.1\s*', '', ETH0_IP) # Remove alias to 127.0.0.1, if present.
SPARK_DRIVER_HOST = ETH0_IP
os.environ["SPARK_LOCAL_IP"] = ETH0_IP
print(os.uname()[1])
print(SPARK_DRIVER_HOST)

###############################################
# DAG Definition
###############################################
now = datetime.now()

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(now.year, now.month, now.day),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1)
}

dag = DAG(
        dag_id="spark-test", 
        description="This DAG runs a simple Pyspark app.",
        default_args=default_args, 
        schedule_interval=timedelta(1)
    )

start = DummyOperator(task_id="start", dag=dag)

spark_job = SparkSubmitOperator(
    task_id="spark_job",
    application="/usr/local/spark/app/hello-world.py", # Spark application path created in airflow and spark cluster
    name=spark_app_name,
    conn_id="spark_default",
    verbose=1,
    conf={
        'spark.master': spark_master,
        'spark.driver.bindAddress': '0.0.0.0',
        'spark.driver.host': SPARK_DRIVER_HOST,
        'spark.dynamicAllocation.enabled': 'false',
        'spark.shuffle.service.enabled': 'false',
        # 'spark.driver.port': 7000,
        'spark.submit.deployMode': 'client',
        'spark.ui.showConsoleProgress': 'true'
    },
    application_args=[file_path],
    dag=dag)

end = DummyOperator(task_id="end", dag=dag)

start >> spark_job >> end