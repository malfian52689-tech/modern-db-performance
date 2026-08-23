import argparse
import hashlib
import json
import os
import shutil
import tempfile
import time
from collections import Counter
from pathlib import Path
from threading import Lock


class AdaptiveStore:
    def __init__(self, shard_count=4, replica_count=2, cache_threshold=3, data_dir="storage"):
        if shard_count < 1 or replica_count < 1 or replica_count > shard_count:
            raise ValueError("replica_count harus antara 1 dan shard_count")
        self.shard_count = shard_count
        self.replica_count = replica_count
        self.cache_threshold = cache_threshold
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.cache = {}
        self.access_count = Counter()
        self.lock = Lock()
        self._ensure_shards()

    def _ensure_shards(self):
        for shard_id in range(self.shard_count):
            path = self._path(shard_id)
            if not path.exists():
                path.write_text("{}", encoding="utf-8")

    def _path(self, shard_id):
        return self.data_dir / f"shard-{shard_id}.json"

    def _shards_for(self, key):
        digest = hashlib.sha256(key.encode("utf-8")).digest()
        primary = int.from_bytes(digest[:8], "big") % self.shard_count
        return [(primary + offset) % self.shard_count for offset in range(self.replica_count)]

    def _read_shard(self, shard_id):
        return json.loads(self._path(shard_id).read_text(encoding="utf-8"))

    def _write_shard(self, shard_id, values):
        path = self._path(shard_id)
        file_descriptor, temporary_path = tempfile.mkstemp(dir=self.data_dir, suffix=".tmp")
        os.close(file_descriptor)
        temporary = Path(temporary_path)
        try:
            temporary.write_text(json.dumps(values, indent=2), encoding="utf-8")
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)

    def put(self, key, value):
        with self.lock:
            locations = self._shards_for(key)
            for shard_id in locations:
                values = self._read_shard(shard_id)
                values[key] = value
                self._write_shard(shard_id, values)
            self.cache.pop(key, None)
            return locations

    def get(self, key):
        with self.lock:
            self.access_count[key] += 1
            if key in self.cache:
                return self.cache[key], "cache"
            for shard_id in self._shards_for(key):
                values = self._read_shard(shard_id)
                if key in values:
                    value = values[key]
                    if self.access_count[key] >= self.cache_threshold:
                        self.cache[key] = value
                    return value, f"shard-{shard_id}"
            return None, "not-found"

    def distribution(self):
        counts = {}
        for shard_id in range(self.shard_count):
            counts[f"shard-{shard_id}"] = len(self._read_shard(shard_id))
        return counts

    def replica_consistent(self, key):
        values = []
        for shard_id in self._shards_for(key):
            values.append(self._read_shard(shard_id).get(key))
        return len(set(json.dumps(value, sort_keys=True) for value in values)) == 1


def run_demo(args):
    data_dir = Path(args.data_dir)
    if data_dir.exists():
        shutil.rmtree(data_dir)
    store = AdaptiveStore(args.shards, args.replicas, args.cache_threshold, data_dir)

    for index in range(args.load):
        store.put(f"order-{index}", {"status": "paid", "amount": index * 1000})

    start = time.perf_counter()
    cache_hits = 0
    for index in range(args.load):
        _, source = store.get(f"order-{index}")
        if source == "cache":
            cache_hits += 1
    for _ in range(args.cache_threshold + 1):
        _, source = store.get("order-0")
        if source == "cache":
            cache_hits += 1
    elapsed_ms = (time.perf_counter() - start) * 1000

    print("=== Scalable Storage Demo ===")
    print(f"records={args.load}, shards={args.shards}, replicas={args.replicas}")
    print(f"read_ms={elapsed_ms:.3f}, cache_hits={cache_hits}")
    print(f"distribution={json.dumps(store.distribution())}")
    print(f"replica_consistent_order-0={store.replica_consistent('order-0')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prototipe storage scalable dan adaptif")
    parser.add_argument("--demo", action="store_true", help="Jalankan simulasi")
    parser.add_argument("--load", type=int, default=100, help="Jumlah data simulasi")
    parser.add_argument("--shards", type=int, default=4, help="Jumlah shard")
    parser.add_argument("--replicas", type=int, default=2, help="Faktor replica")
    parser.add_argument("--cache-threshold", type=int, default=3, help="Akses sebelum masuk cache")
    parser.add_argument("--data-dir", default="storage", help="Folder data")
    arguments = parser.parse_args()
    if arguments.demo:
        run_demo(arguments)
    else:
        parser.print_help()
