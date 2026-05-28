# Rancangan Laporan Proyek: Intelligent Buffer Wizard

## Format Laporan

Laporan ditulis dengan gaya **IEEE**. Struktur penulisan mengikuti pola ilmiah-teknis: ringkas, sistematis, berbasis referensi, dan berfokus pada masalah, metode, implementasi, hasil, serta evaluasi.

---

## Judul yang Disarankan

**Perancangan Intelligent Buffer Wizard Berbasis Chemistry Engine, Expert System, dan AI/ML untuk Formulasi Larutan Buffer**

Alternatif judul:

1. **Intelligent Buffer Wizard: Sistem Pakar dan Prediktor Risiko Presipitasi untuk Formulasi Buffer Kimia**
2. **Pengembangan Sistem Cerdas untuk Perhitungan, Validasi, dan Rekomendasi Formulasi Buffer**
3. **Implementasi Rule-Based Expert System dan Fuzzy Risk Classifier pada Aplikasi Formulasi Buffer**

---

# Struktur Laporan Format IEEE

## Abstrak

Bagian ini menjelaskan ringkasan proyek secara singkat, meliputi latar belakang, tujuan, metode, fitur utama, dan hasil yang diharapkan.

Hal yang dibahas:

- Masalah umum dalam formulasi buffer kimia.
- Keterbatasan kalkulator buffer sederhana.
- Solusi yang ditawarkan oleh Intelligent Buffer Wizard.
- Komponen utama: chemistry engine, expert system, Ksp predictor, AI/ML layer, dan report generator.
- Manfaat sistem bagi pengguna laboratorium, peneliti, atau mahasiswa.

Contoh arah pembahasan:

> Intelligent Buffer Wizard dikembangkan untuk membantu pengguna merancang formulasi buffer secara lebih akurat dengan mempertimbangkan pH, kekuatan ionik, risiko presipitasi, kompatibilitas ion, dan rekomendasi formulasi berbasis sistem cerdas.

---

## Kata Kunci

Contoh kata kunci:

- Buffer solution
- Expert system
- Chemistry engine
- Precipitation prediction
- Fuzzy logic
- Ksp
- Ionic strength
- Intelligent formulation

---

# I. Pendahuluan

## 1.1 Latar Belakang

Bagian ini menjelaskan alasan proyek dibuat.

Hal yang dapat dibahas:

- Larutan buffer penting dalam eksperimen kimia, biologi, farmasi, dan kultur sel.
- Perhitungan buffer tidak cukup hanya menggunakan persamaan Henderson-Hasselbalch sederhana.
- Dalam kondisi nyata, pH dipengaruhi oleh aktivitas ion, kekuatan ionik, suhu, kompatibilitas ion, dan kemungkinan presipitasi.
- Banyak pengguna membutuhkan alat bantu yang tidak hanya menghitung pH, tetapi juga memberi peringatan risiko dan rekomendasi.
- Intelligent Buffer Wizard dirancang sebagai sistem cerdas untuk membantu proses formulasi buffer secara interaktif.

## 1.2 Rumusan Masalah

Contoh rumusan masalah:

1. Bagaimana merancang sistem yang dapat membantu pengguna menghitung pH buffer secara lebih realistis?
2. Bagaimana sistem dapat mendeteksi konflik kimia seperti presipitasi antar ion?
3. Bagaimana sistem pakar dapat digunakan untuk memberikan rekomendasi buffer alternatif?
4. Bagaimana AI/ML dapat digunakan untuk mengklasifikasikan risiko dan merekomendasikan formulasi?
5. Bagaimana hasil analisis dapat disajikan dalam bentuk laporan yang mudah dipahami pengguna?

## 1.3 Tujuan Penelitian/Proyek

Tujuan proyek:

1. Merancang aplikasi Intelligent Buffer Wizard untuk formulasi larutan buffer.
2. Mengembangkan konsep chemistry engine untuk perhitungan pH, kekuatan ionik, dan aktivitas ion.
3. Mengintegrasikan sistem pakar berbasis aturan untuk mendeteksi konflik kimia.
4. Menyediakan prediksi risiko presipitasi berdasarkan Ksp dan saturation index.
5. Menyediakan fitur rekomendasi, simulasi, visualisasi, dan pembuatan laporan.

## 1.4 Batasan Masalah

Batasan yang dapat digunakan:

- Sistem berfokus pada formulasi buffer kimia dan media berbasis buffer.
- Perhitungan utama mencakup pH, pKa, ionic strength, activity coefficient, dan risiko presipitasi.
- Database kimia dapat berupa JSON, YAML, atau SQLite.
- AI/ML digunakan sebagai lapisan rekomendasi dan klasifikasi risiko, bukan sebagai pengganti validasi laboratorium.
- Sistem tidak menggantikan eksperimen aktual di laboratorium.

## 1.5 Manfaat

Manfaat proyek:

- Membantu pengguna memilih buffer yang sesuai.
- Mengurangi kesalahan formulasi.
- Memberikan peringatan dini terhadap risiko presipitasi.
- Mempermudah analisis formulasi buffer kompleks.
- Menyediakan dokumentasi formulasi dalam bentuk laporan PDF/HTML.

---

# II. Studi Literatur

## 2.1 Larutan Buffer

Hal yang dibahas:

- Definisi larutan buffer.
- Fungsi buffer dalam menjaga kestabilan pH.
- Contoh buffer: phosphate, acetate, Tris, HEPES, bicarbonate.
- Penerapan buffer pada kimia analitik, biokimia, kultur sel, dan farmasi.

## 2.2 Persamaan Henderson-Hasselbalch

Hal yang dibahas:

- Bentuk dasar persamaan:

```text
pH = pKa + log([A-]/[HA])
```

- Kelebihan persamaan ini untuk estimasi cepat.
- Keterbatasannya pada larutan nyata.
- Perlunya koreksi aktivitas ion.

## 2.3 Ionic Strength dan Activity Coefficient

Hal yang dibahas:

- Konsep kekuatan ionik.
- Pengaruh ion terhadap aktivitas spesies kimia.
- Debye-Hückel dan Davies Equation.
- Alasan sistem perlu menghitung pH nyata, bukan hanya pH ideal.

## 2.4 Kelarutan dan Ksp

Hal yang dibahas:

- Definisi Ksp.
- Ion product Q.
- Perbandingan Q dan Ksp.
- Saturation Index.
- Risiko presipitasi pada kombinasi ion tertentu, misalnya kalsium dengan fosfat.

## 2.5 Sistem Pakar

Hal yang dibahas:

- Definisi expert system.
- Rule-based reasoning.
- Knowledge base.
- Inference engine.
- Contoh aturan: konflik phosphate-calcium, bicarbonate-CO2 equilibrium, toksisitas buffer.

## 2.6 Fuzzy Logic dan Machine Learning

Hal yang dibahas:

- Fuzzy logic untuk klasifikasi risiko rendah, sedang, tinggi, dan kritis.
- Machine learning untuk rekomendasi formulasi berbasis data historis.
- Similarity-based recommender untuk membandingkan formulasi pengguna dengan template seperti PBS, HBSS, MEM, dan DMEM.

---

# III. Analisis Kebutuhan Sistem

## 3.1 Kebutuhan Fungsional

Sistem diharapkan memiliki fungsi:

1. Input kebutuhan buffer, seperti target pH, volume, konsentrasi, dan jenis buffer.
2. Perhitungan pH menggunakan chemistry engine.
3. Koreksi aktivitas ion berdasarkan ionic strength.
4. Deteksi risiko presipitasi multi-ion.
5. Deteksi konflik kimia menggunakan rule-based expert system.
6. Klasifikasi risiko menggunakan fuzzy logic.
7. Rekomendasi formulasi alternatif.
8. Simulasi what-if, misalnya perubahan suhu atau konsentrasi.
9. Visualisasi kurva titrasi dan heatmap risiko.
10. Penyimpanan riwayat sesi.
11. Pembuatan laporan PDF/HTML.

## 3.2 Kebutuhan Non-Fungsional

Sistem sebaiknya memenuhi:

- Akurasi perhitungan yang dapat diverifikasi.
- Antarmuka mudah digunakan.
- Struktur modular.
- Database mudah diperbarui.
- Hasil analisis dapat ditelusuri.
- Sistem dapat dikembangkan menjadi CLI, TUI, maupun web dashboard.

## 3.3 Kebutuhan Data

Data yang diperlukan:

- Data pKa buffer.
- Data Ksp garam.
- Data kompatibilitas ion.
- Template media biologis.
- Aturan sistem pakar.
- Riwayat formulasi pengguna.

Contoh file data:

```text
data/ksp_database.json
data/buffer_catalog.json
data/media_templates.json
data/rules/compatibility.yaml
data/rules/precipitation.yaml
data/rules/toxicity.yaml
```

## 3.4 Profil Pengguna

Target pengguna:

- Mahasiswa kimia, biologi, farmasi, atau bioteknologi.
- Peneliti laboratorium.
- Teknisi laboratorium.
- Pengembang sistem edukasi kimia.

---

# IV. Perancangan Sistem

## 4.1 Arsitektur Sistem

Arsitektur sistem terdiri dari beberapa lapisan:

1. **Presentation Layer**  
   Menyediakan antarmuka CLI, TUI, atau web dashboard.

2. **Application Layer**  
   Mengatur alur wizard, koordinasi engine, dan pembuatan laporan.

3. **Domain Knowledge Base**  
   Menyimpan aturan, katalog buffer, data Ksp, dan template media.

4. **Chemistry Engine**  
   Melakukan perhitungan pH, ionic strength, activity coefficient, spesiasi, dan risiko presipitasi.

5. **AI/ML Layer**  
   Menyediakan fuzzy risk classifier, recommender, dan optimizer.

6. **Data Layer**  
   Menyimpan database kimia, riwayat sesi, dan hasil analisis.

## 4.2 Diagram Arsitektur

Diagram yang dapat dimasukkan ke laporan:

```text
┌─────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                  │
│         CLI/TUI                 Web UI               │
├─────────────────────────────────────────────────────┤
│                APPLICATION LAYER                     │
│    Wizard Flow │ Expert Engine │ Reporter            │
├──────────────┬──────────────────────┬───────────────┤
│  KNOWLEDGE   │   CHEMISTRY ENGINE   │  AI/ML LAYER  │
│  BASE        │   Buffer, Ksp,       │  Fuzzy Logic  │
│  JSON/YAML   │   Ionic Strength     │  Recommender  │
├──────────────┴──────────────────────┴───────────────┤
│                   DATA LAYER                         │
│      SQLite / JSON DB │ History │ Sessions           │
└─────────────────────────────────────────────────────┘
```

## 4.3 Modul Chemistry Engine

Hal yang dibahas:

- Perhitungan pH buffer.
- Henderson-Hasselbalch sebagai dasar.
- Koreksi aktivitas ion dengan Davies Equation.
- Perhitungan ionic strength.
- Iterative solver karena pH dan spesiasi saling memengaruhi.

Submodul:

```text
core/chemistry/buffer_engine.py
core/chemistry/ksp_predictor.py
core/chemistry/speciation.py
core/chemistry/ionic_strength.py
```

## 4.4 Modul Expert System

Hal yang dibahas:

- Knowledge base berbasis YAML/JSON.
- Aturan kompatibilitas buffer.
- Aturan presipitasi.
- Aturan toksisitas.
- Inference engine untuk menjalankan aturan.
- Conflict resolver untuk menentukan prioritas peringatan.

Contoh aturan:

```yaml
rules:
  - id: R001
    name: Phosphate-Calcium Conflict
    condition:
      ions_present: [Ca2+, Mg2+]
      buffer_type: phosphate
    consequence:
      risk: HIGH_PRECIPITATION
      action: SUGGEST_HEPES_OR_TRIS
```

## 4.5 Modul Ksp Precipitation Predictor

Hal yang dibahas:

- Sistem mengecek semua pasangan ion secara simultan.
- Menghitung ion product Q.
- Membandingkan Q dengan Ksp.
- Menghasilkan saturation index.
- Mengklasifikasikan status aman, waspada, berisiko, atau kritis.

## 4.6 Modul AI/ML

Hal yang dibahas:

- Fuzzy Risk Classifier untuk risiko non-biner.
- Formulation Recommender untuk memberi rekomendasi berbasis similarity.
- Constraint Optimizer untuk optimasi multi-objektif.

Kriteria optimasi:

- Memaksimalkan kapasitas buffer.
- Meminimalkan toksisitas.
- Meminimalkan biaya reagen.
- Menghindari zona presipitasi.

## 4.7 Modul UI dan Reporter

Hal yang dibahas:

- Wizard mode untuk input bertahap.
- Dashboard untuk visualisasi.
- Reporter untuk ekspor PDF/HTML.
- Riwayat sesi dan perbandingan formulasi.

---

# V. Implementasi Sistem

## 5.1 Stack Teknologi

Tabel yang dapat digunakan:

| Layer | Teknologi | Fungsi |
|---|---|---|
| Chemistry | chempy, sympy | Spesiasi dan persamaan kimia |
| Numerik | scipy, numpy | Solver dan optimasi |
| Expert System | experta/custom | Rule engine |
| Fuzzy Logic | scikit-fuzzy | Klasifikasi risiko |
| ML | scikit-learn | Rekomendasi dan clustering |
| Database | SQLite, SQLAlchemy | Penyimpanan data |
| Visualisasi | matplotlib, plotly | Kurva dan heatmap |
| UI Terminal | rich, textual | TUI interaktif |
| Web UI | streamlit | Dashboard web |
| Validasi | pydantic | Validasi input |
| Report | reportlab, jinja2 | PDF/HTML report |

## 5.2 Struktur Direktori

Struktur proyek yang dapat dijelaskan:

```text
intelligent_buffer_wizard/
├── core/
│   ├── chemistry/
│   ├── expert/
│   └── ai/
├── data/
│   ├── ksp_database.json
│   ├── buffer_catalog.json
│   ├── media_templates.json
│   └── rules/
├── ui/
├── models/
└── tests/
```

## 5.3 Alur Kerja Sistem

Alur sistem:

1. Pengguna memasukkan target pH, volume, konsentrasi, dan jenis buffer.
2. Sistem mengambil data pKa, kompatibilitas, dan Ksp dari database.
3. Chemistry engine menghitung pH dan ionic strength.
4. Ksp predictor mengevaluasi risiko presipitasi.
5. Expert engine menjalankan aturan konflik.
6. AI/ML layer mengklasifikasikan risiko dan memberi rekomendasi.
7. Sistem menampilkan hasil dalam wizard/dashboard.
8. Reporter menghasilkan laporan formulasi.

## 5.4 Contoh Skenario Penggunaan

Skenario:

- Pengguna ingin membuat buffer fosfat dengan target pH 7,4.
- Pengguna menambahkan ion Ca2+ atau Mg2+.
- Sistem mendeteksi risiko presipitasi calcium phosphate.
- Sistem memberi peringatan risiko tinggi.
- Sistem menyarankan buffer alternatif seperti HEPES atau Tris.
- Sistem membuat laporan hasil analisis.

---

# VI. Pengujian dan Evaluasi

## 6.1 Strategi Pengujian

Jenis pengujian:

1. **Unit Testing**  
   Menguji fungsi individual seperti perhitungan pH, ionic strength, dan saturation index.

2. **Integration Testing**  
   Menguji integrasi antara chemistry engine, expert system, dan AI/ML layer.

3. **Validation Testing**  
   Membandingkan hasil sistem dengan literatur atau kalkulasi manual.

4. **User Testing**  
   Menguji kemudahan penggunaan wizard dan dashboard.

## 6.2 Parameter Evaluasi

Parameter yang dapat digunakan:

- Akurasi pH.
- Ketepatan deteksi presipitasi.
- Kejelasan rekomendasi.
- Kecepatan proses analisis.
- Kemudahan penggunaan antarmuka.
- Kelengkapan laporan hasil.

## 6.3 Contoh Kasus Uji

Contoh test case:

| No | Kasus Uji | Input | Output yang Diharapkan |
|---|---|---|---|
| 1 | Buffer sederhana | pH target 7,4 phosphate | Komposisi buffer muncul |
| 2 | Konflik ion | Phosphate + Ca2+ | Peringatan presipitasi |
| 3 | Open system | Bicarbonate | Peringatan drift CO2 |
| 4 | Risiko fuzzy | SI mendekati nol | Risiko sedang/tinggi |
| 5 | Rekomendasi | Buffer tidak kompatibel | Saran HEPES/Tris |

---

# VII. Kesimpulan dan Saran

## 7.1 Kesimpulan

Hal yang dapat disimpulkan:

- Intelligent Buffer Wizard bukan hanya kalkulator buffer sederhana.
- Sistem menggabungkan chemistry engine, expert system, Ksp predictor, dan AI/ML.
- Sistem dapat membantu pengguna memahami risiko formulasi buffer.
- Sistem memiliki potensi digunakan sebagai alat bantu edukasi dan laboratorium.

## 7.2 Saran Pengembangan

Saran lanjutan:

- Menambah database buffer dan Ksp.
- Melakukan validasi dengan data eksperimen laboratorium.
- Menambahkan model machine learning dari dataset formulasi nyata.
- Mengembangkan dashboard web yang lebih interaktif.
- Menambahkan fitur ekspor protokol laboratorium otomatis.

---

# Daftar Pustaka

Referensi ditulis dengan format IEEE.

Contoh format:

```text
[1] D. C. Harris, Quantitative Chemical Analysis, 9th ed. New York, NY, USA: W. H. Freeman, 2016.
[2] A. J. Bard and L. R. Faulkner, Electrochemical Methods: Fundamentals and Applications, 2nd ed. New York, NY, USA: Wiley, 2001.
[3] P. Atkins and J. de Paula, Physical Chemistry, 10th ed. Oxford, U.K.: Oxford University Press, 2014.
[4] G. Svehla, Vogel's Qualitative Inorganic Analysis, 7th ed. London, U.K.: Pearson, 1996.
```

Referensi yang dapat dicari:

- Buku kimia analitik.
- Buku kimia fisik.
- Literatur buffer biologis.
- Dokumentasi scikit-fuzzy, scipy, scikit-learn.
- Paper tentang expert system dan chemical compatibility.

---

# Lampiran

Lampiran yang dapat ditambahkan:

1. Source code utama.
2. Contoh file aturan YAML.
3. Contoh database Ksp.
4. Screenshot antarmuka CLI/Web.
5. Contoh output laporan PDF/HTML.
6. Hasil pengujian.
7. Diagram arsitektur lengkap.

---

# Pembagian Tugas Laporan untuk 4 Orang

Pembagian berikut khusus untuk **penulisan laporan**, bukan pembagian implementasi program.

## Anggota 1 — Pendahuluan dan Studi Literatur Dasar

Tanggung jawab:

- Abstrak awal.
- Kata kunci.
- Bab I Pendahuluan.
- Bab II bagian dasar teori buffer.

Bagian yang dikerjakan:

1. Abstrak
2. Kata Kunci
3. I. Pendahuluan
   - 1.1 Latar Belakang
   - 1.2 Rumusan Masalah
   - 1.3 Tujuan
   - 1.4 Batasan Masalah
   - 1.5 Manfaat
4. II. Studi Literatur
   - 2.1 Larutan Buffer
   - 2.2 Persamaan Henderson-Hasselbalch

Output anggota 1:

- Narasi latar belakang yang kuat.
- Rumusan masalah dan tujuan yang jelas.
- Dasar teori buffer dan Henderson-Hasselbalch.
- Minimal 2 referensi IEEE.

---

## Anggota 2 — Studi Literatur Lanjutan dan Analisis Kebutuhan

Tanggung jawab:

- Menjelaskan teori kimia lanjutan.
- Menyusun analisis kebutuhan sistem.
- Menghubungkan teori dengan kebutuhan proyek.

Bagian yang dikerjakan:

1. II. Studi Literatur
   - 2.3 Ionic Strength dan Activity Coefficient
   - 2.4 Kelarutan dan Ksp
   - 2.5 Sistem Pakar
   - 2.6 Fuzzy Logic dan Machine Learning
2. III. Analisis Kebutuhan Sistem
   - 3.1 Kebutuhan Fungsional
   - 3.2 Kebutuhan Non-Fungsional
   - 3.3 Kebutuhan Data
   - 3.4 Profil Pengguna

Output anggota 2:

- Penjelasan teori ionic strength, Ksp, expert system, fuzzy logic, dan ML.
- Daftar kebutuhan fungsional dan non-fungsional.
- Minimal 3 referensi IEEE.

---

## Anggota 3 — Perancangan Sistem

Tanggung jawab:

- Menjelaskan desain arsitektur proyek.
- Membuat diagram sistem.
- Menjelaskan modul utama.

Bagian yang dikerjakan:

1. IV. Perancangan Sistem
   - 4.1 Arsitektur Sistem
   - 4.2 Diagram Arsitektur
   - 4.3 Modul Chemistry Engine
   - 4.4 Modul Expert System
   - 4.5 Modul Ksp Precipitation Predictor
   - 4.6 Modul AI/ML
   - 4.7 Modul UI dan Reporter

Output anggota 3:

- Diagram arsitektur sistem.
- Penjelasan tiap layer.
- Penjelasan tiap modul.
- Contoh rule YAML dan alur inferensi.
- Penjelasan data flow dari input sampai laporan.

---

## Anggota 4 — Implementasi, Pengujian, Kesimpulan, dan Finalisasi IEEE

Tanggung jawab:

- Menjelaskan implementasi teknis.
- Menyusun pengujian dan evaluasi.
- Menulis kesimpulan.
- Menyatukan dan merapikan seluruh laporan ke format IEEE.

Bagian yang dikerjakan:

1. V. Implementasi Sistem
   - 5.1 Stack Teknologi
   - 5.2 Struktur Direktori
   - 5.3 Alur Kerja Sistem
   - 5.4 Contoh Skenario Penggunaan
2. VI. Pengujian dan Evaluasi
   - 6.1 Strategi Pengujian
   - 6.2 Parameter Evaluasi
   - 6.3 Contoh Kasus Uji
3. VII. Kesimpulan dan Saran
   - 7.1 Kesimpulan
   - 7.2 Saran Pengembangan
4. Daftar Pustaka
5. Lampiran
6. Finalisasi format IEEE

Output anggota 4:

- Penjelasan implementasi dan stack teknologi.
- Tabel pengujian.
- Kesimpulan dan saran.
- Daftar pustaka rapi.
- Format akhir laporan konsisten.

---

# Tabel Ringkas Pembagian Laporan

| Anggota | Fokus | Bagian Laporan | Output Utama |
|---|---|---|---|
| Anggota 1 | Pendahuluan dan teori dasar | Abstrak, Bab I, Bab II 2.1-2.2 | Latar belakang, tujuan, teori buffer |
| Anggota 2 | Teori lanjutan dan kebutuhan | Bab II 2.3-2.6, Bab III | Teori Ksp, sistem pakar, AI/ML, kebutuhan sistem |
| Anggota 3 | Desain sistem | Bab IV | Arsitektur, modul, diagram, data flow |
| Anggota 4 | Implementasi dan evaluasi | Bab V, Bab VI, Bab VII, pustaka, lampiran | Stack teknologi, testing, kesimpulan, finalisasi IEEE |

---

# Timeline Pengerjaan Laporan

## Hari 1

- Semua anggota membaca PRD.
- Menyetujui judul dan struktur laporan.
- Membagi referensi.

## Hari 2

- Anggota 1 menyelesaikan Bab I dan teori dasar.
- Anggota 2 menyelesaikan studi literatur lanjutan.
- Anggota 3 membuat diagram arsitektur awal.
- Anggota 4 menyiapkan template IEEE dan daftar pustaka.

## Hari 3

- Anggota 2 menyelesaikan Bab III.
- Anggota 3 menyelesaikan Bab IV.
- Anggota 4 menyelesaikan Bab V dan Bab VI.

## Hari 4

- Anggota 4 menggabungkan semua bagian.
- Semua anggota melakukan review isi.
- Perbaikan konsistensi istilah, format tabel, gambar, dan sitasi.

## Hari 5

- Finalisasi laporan.
- Cek format IEEE.
- Cek daftar pustaka.
- Cek plagiarisme jika diperlukan.
- Export PDF.

---

# Checklist Final Laporan

Gunakan checklist ini sebelum laporan dikumpulkan:

- [ ] Judul sesuai topik proyek.
- [ ] Abstrak ringkas dan mencakup tujuan, metode, dan hasil.
- [ ] Kata kunci tersedia.
- [ ] Bab I menjelaskan masalah dan tujuan dengan jelas.
- [ ] Bab II memiliki dasar teori dan referensi.
- [ ] Bab III menjelaskan kebutuhan sistem.
- [ ] Bab IV menjelaskan arsitektur dan modul.
- [ ] Bab V menjelaskan implementasi teknis.
- [ ] Bab VI memiliki strategi pengujian.
- [ ] Bab VII berisi kesimpulan dan saran.
- [ ] Semua gambar dan tabel diberi nomor.
- [ ] Sitasi menggunakan format IEEE.
- [ ] Daftar pustaka sesuai urutan kemunculan.
- [ ] Format font, margin, heading, dan spacing konsisten.
- [ ] Tidak ada bagian kosong atau placeholder.
- [ ] Semua anggota sudah memeriksa bagian masing-masing.
