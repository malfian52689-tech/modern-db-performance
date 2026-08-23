# Proyek Pengembangan Sistem Penyimpanan Data Skalabel

## Deskripsi
Proyek ini merupakan prototipe sistem penyimpanan data yang dirancang untuk menangani pertumbuhan volume data dan perubahan beban kerja. Sistem menggunakan pendekatan polyglot persistence sederhana: data panas (hot data) disimpan pada cache in-memory, sedangkan seluruh data tetap disimpan secara persisten pada storage berbasis file.

Prototipe ini menerapkan:

- **Sharding**: data dibagi ke beberapa shard berdasarkan hash key.
- **Replication**: setiap data disalin ke replica shard untuk meningkatkan ketersediaan.
- **Adaptive storage**: key yang sering dibaca dipromosikan ke cache in-memory.
- **Partition-aware routing**: request diarahkan ke shard utama dan replica yang sesuai.
- **Atomic file replacement**: perubahan shard ditulis melalui file sementara sebelum menggantikan file utama.

## Kesesuaian Asesmen
Project ini mendukung Sub-CPMK-3.2 level C4 karena mahasiswa merancang dan membangun prototipe sistem penyimpanan data yang skalabel dan adaptif. Implementasi menggabungkan desain arsitektur, partisi data, replikasi, caching, dan pemrosesan adaptif.

## Arsitektur

```text
Client
  |
  v
AdaptiveStore
  |-- hash(key) -> primary shard
  |-- replica shard -> salinan data
  |-- hot cache -> key dengan akses tinggi
  `-- storage/shard-*.json -> penyimpanan persisten
```

Dengan `N` shard dan faktor replikasi `R`, satu key ditulis ke satu primary shard dan `R - 1` replica shard. Routing menggunakan hash stabil sehingga key yang sama selalu diarahkan ke shard yang sama.

## Teknologi
- Python 3.10+
- JSON untuk prototipe storage persisten
- `hashlib` untuk routing shard yang stabil
- `threading.Lock` untuk menjaga konsistensi operasi dalam satu proses

## Cara Menjalankan

Dari folder project ini jalankan:

```powershell
python scalable_storage.py --demo
```

Untuk simulasi beban kerja:

```powershell
python scalable_storage.py --load 1000 --shards 4 --replicas 2
```

File data dibuat pada folder `storage/`. Folder ini merupakan hasil runtime dan tidak perlu diunggah ke GitHub.

## Contoh Hasil
Program akan menampilkan jumlah write/read, cache hit, distribusi data antar shard, dan status konsistensi replica. Angka waktu dapat berbeda bergantung pada perangkat.

## Keterbatasan dan Pengembangan
Prototipe ini berjalan pada satu komputer dan menggunakan file JSON, sehingga belum ditujukan untuk produksi. Pengembangan berikutnya dapat menggunakan Redis untuk hot cache, MongoDB/Cassandra untuk distributed NoSQL storage, replication protocol, monitoring, dan container orchestration.

## Struktur Project

```text
proyek-penyimpanan-data-skalabel/
├── README.md
├── scalable_storage.py
├── report.md
└── .gitignore
```
