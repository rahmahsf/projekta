import numpy as np
from sklearn.preprocessing import MinMaxScaler
from main.models import Kasus, KasusRekomendasi


def proses_cbr(bor_input, los_input, gdr_input):
    # Ambil semua kasus dari database
    kasus_qs = Kasus.objects.all()

    if not kasus_qs.exists():
        return None

    #  Bentuk array data historis
    data_kasus = []
    daftar_kasus = []

    for k in kasus_qs:
        data_kasus.append([k.bor, k.los, k.gdr])
        daftar_kasus.append(k)

    data_kasus = np.array(data_kasus)

    # Normalisasi
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data_kasus)

    input_scaled = scaler.transform([[bor_input, los_input, gdr_input]])

    # Hitung Euclidean Distance
    distances = np.sqrt(np.sum((data_scaled - input_scaled) ** 2, axis=1))

    #Ambil index jarak terkecil
    idx_terdekat = np.argmin(distances)
    kasus_terdekat = daftar_kasus[idx_terdekat]
    jarak = float(distances[idx_terdekat])

    # Ambil rekomendasi dari kasus tersebut
    rekom_relasi = KasusRekomendasi.objects.filter(
        kasus=kasus_terdekat
    ).select_related('rekomendasi')

    rekom_list = [
        {
            "nama": r.rekomendasi.rekomendasi,
            "jenis": r.rekomendasi.jenis_rekomendasi
        }
        for r in rekom_relasi
    ]

    return {
        "kasus": kasus_terdekat,
        "distance": jarak,
        "rekomendasi": rekom_list
    }