# Test Case Video Demonstrasi

Dokumen ini dipakai sebagai panduan rekaman video demonstrasi sistem Intelligent Buffer Wizard.

## 1. Tujuan Demonstrasi

Menunjukkan bahwa sistem dapat:

- Menghitung formulasi buffer berdasarkan pH target, konsentrasi, volume, dan garam tambahan.
- Menampilkan protokol persiapan laboratorium dalam Bahasa Indonesia.
- Menampilkan tab hasil dengan indikator tab aktif yang jelas.
- Menampilkan spesiasi kimia, grafik simulasi, diagnostik ahli, dan rekomendasi media referensi.

## 2. Prasyarat

Pastikan dependensi sudah terpasang:

```bash
pip install -r requirements.txt
```

Jalankan test sebelum rekaman:

```bash
pytest -q
python -m compileall core ui models
```

Jalankan dashboard:

```bash
uvicorn ui.dashboard:app --reload
```

Buka browser:

```text
http://127.0.0.1:8000
```

## 3. Data Input Demo Utama

Gunakan skenario formulasi Tris buffer:

| Parameter | Nilai |
|---|---:|
| Buffer System | Tris |
| Target pH | 8.06 |
| Concentration | 0.05 M |
| Temperature | 25 °C |
| Salt tambahan | NaCl 0.15 M |
| Environment | closed |
| Application | biochemistry |
| Exposure | dark |

## 4. Test Case 1 — Membuka Dashboard

**Langkah:**

1. Buka `http://127.0.0.1:8000`.
2. Tampilkan halaman utama dashboard.
3. Sorot area input formulasi dan area output.

**Expected Result:**

- Dashboard tampil tanpa error.
- Dropdown buffer terisi data.
- Tab output tersedia:
  - 📋 Preparation Protocols
  - 🧪 Chemical Speciation
  - 📊 Simulation Plots
  - ⚠️ Expert Diagnostics
  - 🤖 AI Media Similarity

## 5. Test Case 2 — Mengisi Parameter Formulasi

**Langkah:**

1. Pilih `Tris` pada Buffer System.
2. Isi target pH `8.06`.
3. Isi konsentrasi `0.05`.
4. Isi suhu `25`.
5. Tambahkan garam `NaCl` dengan konsentrasi `0.15`.
6. Klik tombol solve/formulate.

**Expected Result:**

- Sistem mengembalikan hasil formulasi.
- Ringkasan metrik terisi:
  - Ionic Strength
  - Buffer Capacity
  - Safety Rating
- Tidak ada crash pada browser atau server.

## 6. Test Case 3 — Output Protokol Persiapan Bahasa Indonesia

**Langkah:**

1. Buka tab `📋 Preparation Protocols`.
2. Tampilkan resep/protokol yang muncul.
3. Zoom bagian instruksi persiapan.

**Expected Result:**

Output resep menggunakan Bahasa Indonesia, misalnya:

```text
1. Timbang/ukur ...
2. Larutkan keduanya dalam ... air deionisasi ...
3. Tambahkan semua garam lain yang ditentukan ...
4. Tambahkan air deionisasi hingga volume akhir ... Verifikasi pH ...
```

Tidak ada output utama seperti `Measure`, `Dissolve`, atau `Add all other specified salts` pada protokol persiapan.

## 7. Test Case 4 — Indikator Tab Aktif

**Langkah:**

1. Klik setiap tab output secara berurutan:
   - 📋 Preparation Protocols
   - 🧪 Chemical Speciation
   - 📊 Simulation Plots
   - ⚠️ Expert Diagnostics
   - 🤖 AI Media Similarity
2. Perhatikan perubahan visual pada tab yang sedang dipilih.

**Expected Result:**

- Indikator tab aktif terlihat jelas.
- Tab aktif berubah warna/background.
- Tab aktif memiliki border/glow/garis bawah.
- Hanya satu tab yang aktif pada satu waktu.
- Konten yang tampil sesuai dengan tab yang dipilih.

## 8. Test Case 5 — Chemical Speciation

**Langkah:**

1. Klik tab `🧪 Chemical Speciation`.
2. Tampilkan tabel species concentration dan activity coefficients.

**Expected Result:**

- Tabel spesies buffer terisi.
- Nilai charge, concentration, dan fraction tampil.
- Activity coefficient tampil berdasarkan magnitude muatan ion.

## 9. Test Case 6 — Simulation Plots

**Langkah:**

1. Klik tab `📊 Simulation Plots`.
2. Tampilkan semua grafik simulasi.

**Expected Result:**

- Grafik titration curve tampil.
- Grafik species distribution tampil.
- Heatmap risiko presipitasi tampil atau pesan informatif muncul jika tidak ada kombinasi ion berisiko.

## 10. Test Case 7 — Expert Diagnostics

**Langkah:**

1. Klik tab `⚠️ Expert Diagnostics`.
2. Tampilkan tabel precipitation saturation checks.
3. Tampilkan warning dari expert rule jika ada.

**Expected Result:**

- Sistem menampilkan prediksi risiko presipitasi.
- Sistem menampilkan diagnostic warning atau pesan bahwa tidak ada warning.
- Severity/risk terbaca dengan jelas.

## 11. Test Case 8 — AI Media Similarity

**Langkah:**

1. Klik tab `🤖 AI Media Similarity`.
2. Tampilkan daftar media referensi paling mirip.

**Expected Result:**

- Tabel rekomendasi media tampil.
- Similarity index tampil dalam persen.
- Buffer referensi dan konsentrasi garam referensi tampil.

## 12. Checklist Rekaman Video

- [ ] Terminal menunjukkan server berjalan tanpa error.
- [ ] Browser menampilkan dashboard utama.
- [ ] Input formulasi Tris dimasukkan dengan jelas.
- [ ] Hasil formulasi muncul.
- [ ] Protokol persiapan Bahasa Indonesia terlihat.
- [ ] Indikator tab aktif terlihat saat setiap tab diklik.
- [ ] Semua tab output ditampilkan minimal sekali.
- [ ] Video menutup dengan ringkasan bahwa sistem berhasil menghitung, mendiagnosis, dan merekomendasikan formulasi buffer.
