import random
from datetime import datetime, timedelta
from sqlalchemy import text
from db import engine

servers = ["server1", "server2", "server3"]
processes = ["auth", "payment", "orders"]

for i in range(100):

    status = random.choice(["SUCCESS", "ERROR"])

    query = text("""
    INSERT INTO server_logs
    (timestamp, server_name, process_name, status, response_time)
    VALUES (:timestamp,:server,:process,:status,:response)
    """)

    with engine.connect() as conn:
        conn.execute(query,{
            "timestamp":datetime.now() - timedelta(hours=random.randint(0,24)),
            "server":random.choice(servers),
            "process":random.choice(processes),
            "status":status,
            "response":random.randint(10,300)
        })
        conn.commit()