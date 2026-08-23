# EVALUASI SISTEM PENYIMPANAN DATA ADAPTIF DALAM ANALISIS DATA KOMPLEKS

## HALAMAN SAMPUL

**TUGAS EVALUASI SISTEM PENYIMPANAN DATA ADAPTIF**

Mata Kuliah: Sistem Basis Data Modern  
Pertemuan: 11  
Capaian Pembelajaran: Sub-CPMK-2.5 (C4 - Mengevaluasi)

Nama Mahasiswa: **[Isi nama mahasiswa]**  
NIM: **[Isi NIM]**  
Program Studi: **[Isi program studi]**  
Institusi: **[Isi nama institusi]**

Tahun: **2026**

---

## ABSTRAK

Sistem penyimpanan data adaptif dirancang untuk menyesuaikan strategi penyimpanan terhadap perubahan volume data, pola akses, dan beban kerja. Tugas ini mengevaluasi tiga pendekatan, yaitu penyimpanan relasional dengan indexing, caching dinamis menggunakan Redis, dan basis data NoSQL terdistribusi seperti Cassandra. Evaluasi dilakukan melalui analisis karakteristik workload, perbandingan performa, konsistensi, skalabilitas, kompleksitas operasional, serta biaya. Hasil analisis menunjukkan bahwa tidak ada satu teknologi yang unggul untuk seluruh kondisi. PostgreSQL sesuai untuk transaksi relasional yang memerlukan konsistensi kuat, Redis efektif untuk data panas dengan kebutuhan latency rendah, sedangkan Cassandra sesuai untuk penulisan besar yang tersebar dan ketersediaan tinggi. Rekomendasi utama adalah polyglot persistence dengan aturan adaptasi berbasis telemetry, bukan perpindahan storage secara sembarangan.

**Kata kunci:** adaptive storage, NoSQL, caching dinamis, workload, polyglot persistence.

## 1. PENDAHULUAN

### 1.1 Latar Belakang

Aplikasi modern harus memproses data dengan volume besar, pola akses yang berubah, dan kebutuhan layanan yang berbeda. Pada jam normal, sebagian besar request dapat berupa pembacaan data historis. Pada periode puncak, request dapat berubah menjadi penulisan event secara masif. Sistem penyimpanan statis sering tidak efisien karena konfigurasi yang baik untuk satu workload belum tentu baik untuk workload lain.

Sistem penyimpanan data adaptif menyelesaikan masalah tersebut dengan menyesuaikan penempatan data, cache, partisi, atau engine penyimpanan berdasarkan telemetry seperti latency, throughput, cache hit ratio, ukuran data, dan tingkat kegagalan. Pendekatan ini relevan untuk analisis data kompleks karena data dapat memiliki struktur, frekuensi akses, dan kebutuhan konsistensi yang berbeda.

### 1.2 Rumusan Masalah

1. Apa prinsip dan mekanisme sistem penyimpanan data adaptif?
2. Bagaimana kelebihan dan kekurangan PostgreSQL, Redis, dan Cassandra pada workload yang berbeda?
3. Strategi apa yang paling tepat untuk aplikasi analisis data kompleks?
4. Risiko apa yang muncul saat sistem mengadaptasi storage secara otomatis?

### 1.3 Tujuan

1. Menjelaskan prinsip dasar penyimpanan data adaptif.
2. Mengevaluasi beberapa teknologi penyimpanan berdasarkan kriteria yang terukur.
3. Menganalisis studi kasus perubahan workload.
4. Memberikan rekomendasi arsitektur yang dapat dipertanggungjawabkan.

## 2. LANDASAN TEORI

### 2.1 Sistem Penyimpanan Data Adaptif

Sistem adaptif mengamati kondisi operasi, membandingkannya dengan target, kemudian menjalankan tindakan perubahan. Siklusnya dapat dirumuskan sebagai:

`telemetry -> decision policy -> storage action -> measurement`

Contoh tindakan adalah menaikkan kapasitas cache, membuat index, memindahkan data panas ke Redis, menambah replica, atau mengubah jumlah partisi. Adaptasi harus memiliki batas, cooldown, dan mekanisme rollback agar perubahan tidak menimbulkan flapping.

### 2.2 Skalabilitas

Skalabilitas vertikal menambah CPU, RAM, atau storage pada satu node. Skalabilitas horizontal menambah node dan membagi data melalui partisi atau shard. Horizontal scaling lebih sesuai untuk pertumbuhan besar, tetapi meningkatkan kompleksitas routing, replikasi, konsistensi, dan observability.

### 2.3 NoSQL dan Polyglot Persistence

NoSQL mencakup key-value, document, wide-column, dan graph database. Pemilihannya harus mengikuti pola akses, bukan sekadar popularitas teknologi. Polyglot persistence menggunakan lebih dari satu jenis storage: misalnya PostgreSQL untuk transaksi, Redis untuk cache, dan Cassandra untuk event ber-volume tinggi. Kelemahannya adalah sinkronisasi, duplikasi data, dan operasi yang lebih kompleks.

### 2.4 Caching Dinamis

Cache menyimpan data yang sering digunakan pada media berlatensi rendah. Parameter penting meliputi hit ratio, miss ratio, eviction policy, TTL, ukuran cache, dan invalidasi. Cache tidak boleh dianggap sebagai sumber kebenaran utama kecuali desain konsistensinya memang mendukung hal tersebut.

### 2.5 Replikasi dan Partisi

Replikasi membuat salinan data untuk meningkatkan ketersediaan dan kapasitas baca. Partisi membagi data berdasarkan kunci tertentu, misalnya tenant, waktu, atau hash. Kunci partisi yang buruk dapat menimbulkan hot partition. Replikasi juga memiliki trade-off antara konsistensi, latency, dan ketersediaan.

## 3. METODE ANALISIS

### 3.1 Pendekatan

Analisis menggunakan studi komparatif dan skenario workload. Setiap teknologi dinilai pada tujuh kriteria: latency baca/tulis, throughput, skalabilitas, konsistensi, fleksibilitas model data, kompleksitas operasional, dan efisiensi biaya.

### 3.2 Skenario Workload

- **W1 - Transaksi:** 70% read dan 30% write, membutuhkan transaksi dan konsistensi kuat.
- **W2 - Data panas:** 95% read terhadap 5% data paling sering diakses.
- **W3 - Ingest analitik:** penulisan event sangat tinggi, append-heavy, dan dibaca berdasarkan rentang waktu.
- **W4 - Beban campuran:** pola akses berubah antara jam normal dan periode puncak.

### 3.3 Metrik Evaluasi

- **Latency:** waktu respons rata-rata dan p95.
- **Throughput:** operasi per detik.
- **Cache hit ratio:** persentase request yang dilayani cache.
- **Availability:** kemampuan sistem tetap melayani request saat node bermasalah.
- **Consistency:** kesesuaian data antar replica dan sumber kebenaran.
- **Resource efficiency:** pemakaian CPU, RAM, disk, dan network.
- **Operational complexity:** usaha konfigurasi, monitoring, backup, dan pemulihan.

### 3.4 Prosedur

1. Definisikan workload dan target SLO.
2. Siapkan dataset dengan ukuran dan distribusi akses yang sama.
3. Jalankan workload dengan concurrency yang terkontrol.
4. Catat latency p50/p95, throughput, error rate, hit ratio, dan resource usage.
5. Ulangi pengujian minimal tiga kali dan gunakan median.
6. Bandingkan hasil dengan bobot kebutuhan aplikasi.
7. Evaluasi risiko dan tentukan kebijakan adaptasi.

## 4. HASIL DAN PEMBAHASAN

### 4.1 Perbandingan Teknologi

| Kriteria | PostgreSQL | Redis | Cassandra |
|---|---|---|---|
| Model | Relasional | Key-value/in-memory | Wide-column NoSQL |
| Kekuatan utama | Transaksi dan query kompleks | Latency sangat rendah untuk data panas | Write scale dan availability |
| Konsistensi | Kuat dengan transaksi | Dapat dikonfigurasi sesuai fitur | Tunable consistency |
| Skalabilitas | Vertikal dan read replica | Cluster dan sharding | Horizontal native |
| Kelemahan | Scaling write lebih kompleks | RAM mahal dan invalidasi cache | Query harus mengikuti partition key |
| Workload cocok | W1 | W2 | W3 |

Tabel tersebut merupakan analisis karakteristik, bukan klaim hasil benchmark universal. Nilai aktual tetap harus diukur pada hardware, dataset, dan konfigurasi target.

### 4.2 Evaluasi Berdasarkan Workload

**W1 - Transaksi.** PostgreSQL menjadi pilihan utama karena foreign key, transaksi ACID, dan query relasional. Redis dapat digunakan sebagai cache, tetapi data transaksi tetap harus berasal dari database utama. Cassandra kurang ideal jika aplikasi memerlukan join dan transaksi lintas banyak entitas.

**W2 - Data panas.** Redis efektif karena data yang sering dibaca berada di memori. Risiko utamanya adalah cache stampede, stale data, eviction, dan biaya RAM. Strategi TTL, cache-aside, single-flight request, dan invalidasi berbasis event perlu diterapkan.

**W3 - Ingest analitik.** Cassandra sesuai bila partition key dan clustering key dirancang mengikuti query. Data dapat dipartisi berdasarkan waktu dan tenant. Kelemahannya adalah duplikasi model tabel untuk query berbeda dan biaya operasional cluster.

**W4 - Beban campuran.** Arsitektur polyglot dapat mengarahkan data berdasarkan karakteristiknya. Namun, perpindahan data otomatis sebaiknya hanya dilakukan setelah beberapa periode observasi, bukan karena satu lonjakan singkat.

### 4.3 Mekanisme Adaptasi yang Direkomendasikan

Controller adaptif mengumpulkan telemetry setiap interval. Contoh kebijakan:

- Jika p95 read latency melewati SLO selama lima interval dan hit ratio rendah, naikkan kapasitas cache atau ubah TTL secara bertahap.
- Jika satu partition memiliki beban jauh di atas median, lakukan repartitioning terencana.
- Jika disk utilization melewati threshold, tambah kapasitas atau lakukan lifecycle policy pada data lama.
- Jika error rate meningkat setelah perubahan, rollback konfigurasi terakhir.
- Terapkan cooldown agar controller tidak mengubah konfigurasi berulang-ulang.

Kebijakan harus dicatat sebagai audit log sehingga keputusan adaptasi dapat ditelusuri.

### 4.4 Kelebihan dan Kekurangan Sistem Adaptif

**Kelebihan:**

- Menyesuaikan resource dengan kebutuhan aktual.
- Mempertahankan latency saat pola akses berubah.
- Mengurangi pemborosan resource pada periode beban rendah.
- Memungkinkan pemanfaatan beberapa engine penyimpanan.

**Kekurangan:**

- Arsitektur dan debugging lebih kompleks.
- Keputusan adaptasi yang salah dapat memperburuk performa.
- Duplikasi data meningkatkan risiko inkonsistensi.
- Monitoring dan pengujian harus lebih matang.
- Migrasi atau repartitioning dapat menimbulkan beban tambahan.

### 4.5 Studi Kasus: Platform Analisis Penjualan

Platform memiliki data transaksi, katalog produk, dan event klik pengguna. Transaksi memerlukan konsistensi kuat, katalog sering dibaca, sedangkan event klik bertambah sangat cepat dan dianalisis berdasarkan waktu.

Arsitektur yang direkomendasikan:

- PostgreSQL sebagai sumber kebenaran transaksi.
- Redis sebagai cache katalog dan hasil agregasi populer.
- Cassandra atau storage wide-column sebagai penyimpanan event berdasarkan `tenant_id` dan bucket waktu.
- Pipeline event untuk sinkronisasi perubahan katalog dan invalidasi cache.
- Dashboard telemetry untuk memantau latency, hit ratio, lag sinkronisasi, dan ukuran partition.

Solusi ini memenuhi kebutuhan berbeda tanpa memaksa satu database menangani seluruh karakteristik data. Trade-off-nya adalah kebutuhan schema versioning, observability, retry, idempotency, dan prosedur rekonsiliasi.

## 5. KESIMPULAN DAN SARAN

### 5.1 Kesimpulan

Sistem penyimpanan data adaptif dapat meningkatkan efisiensi dan skalabilitas dengan menyesuaikan storage terhadap workload. PostgreSQL unggul pada transaksi konsisten, Redis pada data panas berlatensi rendah, dan Cassandra pada ingest terdistribusi dengan volume tinggi. Polyglot persistence memberikan fleksibilitas, tetapi menambah kompleksitas sinkronisasi dan operasi.

Evaluasi yang baik harus didasarkan pada workload nyata, metrik p95, throughput, error rate, konsistensi, availability, serta konsumsi resource. Adaptasi otomatis harus dikendalikan oleh kebijakan yang memiliki threshold, cooldown, audit, dan rollback.

### 5.2 Saran

1. Mulai dari satu sumber kebenaran sebelum menambah engine kedua.
2. Uji dengan dataset dan pola akses yang mendekati produksi.
3. Gunakan p95/p99, bukan hanya rata-rata latency.
4. Tambahkan observability dan alert untuk cache, replica, partition, serta sinkronisasi.
5. Lakukan adaptasi bertahap melalui canary dan sediakan rollback.
6. Dokumentasikan pembagian tugas kelompok dan hasil pengujian aktual sebelum pengumpulan.

## 6. DAFTAR PUSTAKA

1. PostgreSQL Global Development Group. *PostgreSQL Documentation: Concurrency Control*. https://www.postgresql.org/docs/current/mvcc.html
2. Redis Ltd. *Redis Documentation: Key eviction*. https://redis.io/docs/latest/develop/reference/eviction/
3. Apache Cassandra. *Cassandra Documentation: Data Modeling*. https://cassandra.apache.org/doc/latest/cassandra/data_modeling/
4. Kleppmann, M. (2017). *Designing Data-Intensive Applications*. O'Reilly Media.
5. Amazon Web Services. *Caching Best Practices*. https://aws.amazon.com/caching/

## LAMPIRAN A - Matriks Keputusan

| Kebutuhan dominan | Pilihan utama | Alasan | Risiko |
|---|---|---|---|
| ACID dan query kompleks | PostgreSQL | Transaksi dan model relasional | Bottleneck write pada skala besar |
| Read latency sangat rendah | Redis | In-memory dan TTL | Stale data dan biaya RAM |
| Ingest terdistribusi | Cassandra | Horizontal scaling | Model query terbatas |
| Workload berubah | Polyglot + controller | Memilih storage sesuai pola akses | Kompleksitas sinkronisasi |

## LAMPIRAN B - Format Data Pengujian

| Run | Workload | Storage | Records | Concurrency | p50 ms | p95 ms | Throughput | Error rate | Cache hit |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | W1 | PostgreSQL | [isi] | [isi] | [isi] | [isi] | [isi] | [isi] | - |
| 2 | W2 | Redis | [isi] | [isi] | [isi] | [isi] | [isi] | [isi] | [isi] |
| 3 | W3 | Cassandra | [isi] | [isi] | [isi] | [isi] | [isi] | [isi] | - |

Catatan: kolom hasil pengujian harus diisi berdasarkan pengukuran nyata. Jangan mengarang angka benchmark karena hasil bergantung pada perangkat, konfigurasi, dan dataset.
