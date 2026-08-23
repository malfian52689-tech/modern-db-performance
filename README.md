# Evaluasi Kinerja Sistem Basis Data Modern

## Deskripsi Proyek
Proyek ini bertujuan untuk mengevaluasi kinerja sistem basis data modern dalam konteks solusi industri. Fokus utama dari proyek ini adalah membandingkan performa sistem yang umum digunakan dalam aplikasi modern, terutama basis data relasional dan basis data NoSQL/in-memory.

Mahasiswa akan melakukan analisis terhadap beberapa aspek performa seperti:

- Throughput
- Latency
- Scalability
- Konsistensi data
- Efisiensi penggunaan resource

Selain itu, proyek ini juga mengkaji masalah yang sering muncul pada sistem basis data, seperti bottleneck, overload, dan kebutuhan optimasi melalui indexing, caching, serta partisi data.

## Tujuan Pembelajaran
Proyek ini sesuai dengan Sub-CPMK-3.4, yaitu mahasiswa mampu:

1. Mengevaluasi kinerja sistem basis data secara kritis.
2. Menggunakan metode dan metrik evaluasi yang tepat.
3. Menentukan bottleneck yang memengaruhi performa.
4. Mengusulkan strategi optimasi yang relevan.
5. Menerapkan konsep evaluasi performa pada skenario industri nyata.

## Ruang Lingkup
Proyek ini mencakup:

- Pengukuran performa basis data relasional (SQLite)
- Evaluasi performa basis data in-memory (Redis)
- Analisis benchmarking berdasarkan jumlah data dan operasi CRUD
- Identifikasi bottleneck dan rekomendasi optimasi
- Dokumentasi hasil pengukuran dalam bentuk laporan dan ringkasan analisis

## Teknologi yang Digunakan
- Python
- SQLite
- Redis (opsional)
- GitHub untuk repository proyek

## Struktur Proyek

```text
modern-db-performance/
├── README.md
├── benchmark.py
├── requirements.txt
└── results/
    └── benchmark_report.md
```

## Cara Menjalankan
1. Pastikan Python sudah terinstal.
2. Instal dependency:

```bash
pip install -r requirements.txt
```

3. Jalankan benchmark:

```bash
python benchmark.py --records 5000
```

4. Jika Redis tersedia di lokal, skrip akan membandingkan performa SQLite dan Redis. Jika tidak tersedia, program tetap berjalan dengan SQLite sebagai data utama.

## Hasil yang Diharapkan
Proyek ini diharapkan menghasilkan:

- Analisis performa basis data yang komprehensif
- Perbandingan kinerja antar tipe database
- Kesimpulan mengenai sistem yang paling efisien untuk beban kerja tertentu
- Rekomendasi optimasi berdasarkan hasil evaluasi

## Link Repository GitHub
Link repository akan diberikan setelah akun GitHub Anda tersedia dan repo dipush ke GitHub.

---

## Catatan
Proyek ini dibuat sebagai bentuk implementasi tugas capstone/asesmen pada mata kuliah Sistem Basis Data Modern. Tujuan utamanya adalah untuk melatih keterampilan analisis, evaluasi, dan optimasi performa basis data dalam konteks teknologi industri.
