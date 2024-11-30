from airflow.models import DAG
from airflow_clickhouse_plugin.hooks.clickhouse import ClickHouseHook
from airflow.decorators import task
from datetime import datetime, timedelta

description='Даг трансфера агрегата'
table_from = 'yurii_nitochkin.yurii_nitochkin_lab02_rt'
table_to = 'yurii_nitochkin.yurii_nitochkin_lab02_agg_hourly'

@task(execution_timeout=timedelta(seconds=30))
def transfer_ch_to_ch(**context):
    ch_hook = ClickHouseHook(clickhouse_conn_id="local_click")
    with ch_hook.get_conn() as conn:
        query = f"""Select date_trunc('hour', timestamp) ts_start, 
                            date_trunc('hour', timestamp) + interval '1 hour' ts_end, 
                            sumIf(item_price, eventType = 'itemBuyEvent') revenue,
                            uniqIf(partyId, eventType = 'itemBuyEvent') buyers,
                            uniq(partyId) visitors,
                            uniqIf(sessionId, eventType = 'itemBuyEvent') purchases,
                            revenue / purchases aov
                        from yurii_nitochkin.yurii_nitochkin_lab02_rt
                        where detectedDuplicate = 0
                        and detectedCorruption = 0
			and ts_start < (Select date_trunc('hour', (MAX(`timestamp`))) from yurii_nitochkin.yurii_nitochkin_lab02_rt)
                        group by ts_start, ts_end"""
        
        aggr_data = conn.execute(query)
        conn.execute(f"truncate table {table_to}")
        conn.execute(f"INSERT INTO {table_to} VALUES", aggr_data)

default_args = {
    "owner": '@nitochkin_yury',
    "start_date": datetime(2024, 10, 27, 0, 0),
    "retries": 3,
    "retry_delay": timedelta(seconds=2),
    "depends_on_past": False,
               }

with DAG(
    dag_id = 'yurii_nitochkin_lab02',
    description=description,
    schedule_interval=None,
    max_active_runs=1,
    max_active_tasks=1,
    catchup=False,
    default_args=default_args
         ) as dag:

    transfer = transfer_ch_to_ch()
