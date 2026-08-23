import argparse
import json
import sqlite3
import statistics
import time
from pathlib import Path

try:
    import redis
except ImportError:  # pragma: no cover
    redis = None


def benchmark_sqlite(total_records: int):
    db_path = Path("sqlite_benchmark.db")
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, city TEXT, age INTEGER)")
    cur.execute("CREATE INDEX idx_users_city ON users(city)")

    insert_times = []
    read_times = []
    update_times = []
    delete_times = []

    for i in range(total_records):
        start = time.perf_counter()
        cur.execute(
            "INSERT INTO users (name, email, city, age) VALUES (?, ?, ?, ?)",
            (f"user_{i}", f"user_{i}@example.com", f"city_{i % 10}", 20 + (i % 50)),
        )
        insert_times.append(time.perf_counter() - start)

    conn.commit()

    for i in range(0, total_records, 10):
        start = time.perf_counter()
        cur.execute("SELECT * FROM users WHERE id = ?", (i + 1,))
        cur.fetchall()
        read_times.append(time.perf_counter() - start)

    for i in range(0, total_records, 10):
        start = time.perf_counter()
        cur.execute("UPDATE users SET city = ? WHERE id = ?", ("updated_city", i + 1))
        update_times.append(time.perf_counter() - start)

    conn.commit()

    for i in range(0, total_records, 10):
        start = time.perf_counter()
        cur.execute("DELETE FROM users WHERE id = ?", (i + 1,))
        delete_times.append(time.perf_counter() - start)

    conn.commit()
    conn.close()

    return {
        "database": "SQLite",
        "records": total_records,
        "insert_avg_ms": round(statistics.mean(insert_times) * 1000, 4),
        "read_avg_ms": round(statistics.mean(read_times) * 1000, 4),
        "update_avg_ms": round(statistics.mean(update_times) * 1000, 4),
        "delete_avg_ms": round(statistics.mean(delete_times) * 1000, 4),
    }


def benchmark_redis(total_records: int):
    if redis is None:
        return {"database": "Redis", "status": "skipped", "reason": "redis package not installed"}

    try:
        client = redis.Redis(host="localhost", port=6379, decode_responses=True, socket_connect_timeout=1)
        client.ping()
    except Exception:
        return {"database": "Redis", "status": "skipped", "reason": "Redis server not running on localhost:6379"}

    client.flushdb()

    insert_times = []
    read_times = []
    update_times = []
    delete_times = []

    for i in range(total_records):
        payload = {
            "name": f"user_{i}",
            "email": f"user_{i}@example.com",
            "city": f"city_{i % 10}",
            "age": 20 + (i % 50),
        }
        start = time.perf_counter()
        client.set(f"user:{i}", json.dumps(payload))
        insert_times.append(time.perf_counter() - start)

    for i in range(0, total_records, 10):
        start = time.perf_counter()
        client.get(f"user:{i}")
        read_times.append(time.perf_counter() - start)

    for i in range(0, total_records, 10):
        start = time.perf_counter()
        client.set(f"user:{i}", json.dumps({"city": "updated_city"}))
        update_times.append(time.perf_counter() - start)

    for i in range(0, total_records, 10):
        start = time.perf_counter()
        client.delete(f"user:{i}")
        delete_times.append(time.perf_counter() - start)

    return {
        "database": "Redis",
        "records": total_records,
        "insert_avg_ms": round(statistics.mean(insert_times) * 1000, 4),
        "read_avg_ms": round(statistics.mean(read_times) * 1000, 4),
        "update_avg_ms": round(statistics.mean(update_times) * 1000, 4),
        "delete_avg_ms": round(statistics.mean(delete_times) * 1000, 4),
    }


def main():
    parser = argparse.ArgumentParser(description="Benchmark performa basis data modern")
    parser.add_argument("--records", type=int, default=2000, help="Jumlah record yang akan dibenchmark")
    parser.add_argument("--skip-redis", action="store_true", help="Lewati benchmark Redis")
    args = parser.parse_args()

    sqlite_result = benchmark_sqlite(args.records)
    redis_result = {"database": "Redis", "status": "skipped", "reason": "disabled by user"} if args.skip_redis else benchmark_redis(args.records)

    print("\n=== Hasil Benchmark Basis Data ===")
    print(json.dumps({"sqlite": sqlite_result, "redis": redis_result}, indent=2))

    print("\nInterpretasi singkat:")
    print("- SQLite cocok untuk transaksi kecil dan data relasional dengan kebutuhan konsistensi tinggi.")
    print("- Redis sangat cepat untuk workload read/write in-memory, cocok untuk cache dan data session.")
    print("- Pilihan database sebaiknya disesuaikan dengan kebutuhan throughput, latency, dan skala sistem.")


if __name__ == "__main__":
    main()
