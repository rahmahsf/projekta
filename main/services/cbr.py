import numpy as np
from sklearn.preprocessing import MinMaxScaler
from main.models import Kasus, KasusRekomendasi


def proses_cbr(bor_input, los_input, gdr_input):

    kasus_qs = Kasus.objects.all()

    # kalau belum ada data kasus
    if not kasus_qs.exists():
        return {
            "top_kasus": [],
            "kasus_utama": None,
            "rekomendasi": [],
            "rekomendasi_ids": []
        }

    data_kasus = []
    daftar_kasus = []

    for k in kasus_qs:
        data_kasus.append([k.bor, k.los, k.gdr])
        daftar_kasus.append(k)

    data_kasus = np.array(data_kasus)

    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data_kasus)
    input_scaled = scaler.transform([[bor_input, los_input, gdr_input]])

    distances = np.sqrt(np.sum((data_scaled - input_scaled) ** 2, axis=1))

   
    # Ambil 3 kasus terdekat
   
    idx_sorted = np.argsort(distances)[:3]

    hasil_kasus = []

    for i in idx_sorted:
        hasil_kasus.append({
            "kasus": daftar_kasus[i],
            "distance": float(distances[i])
        })

    # Ambil rekomendasi dari kasus paling mirip (index 0)

    kasus_utama = hasil_kasus[0]["kasus"]

    rekom_relasi = KasusRekomendasi.objects.filter(
        kasus=kasus_utama
    ).select_related("rekomendasi")

    rekom_list = []
    rekom_ids = []

    for r in rekom_relasi:
        rekom_list.append({
            "id": r.rekomendasi.id,
            "nama": r.rekomendasi.rekomendasi,
            "jenis": r.rekomendasi.jenis_rekomendasi
        })
        rekom_ids.append(r.rekomendasi.id)

    return {
        "top_kasus": hasil_kasus,
        "kasus_utama": kasus_utama,
        "rekomendasi": rekom_list,
        "rekomendasi_ids": rekom_ids
    }