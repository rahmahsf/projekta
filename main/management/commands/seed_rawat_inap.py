from django.core.management.base import BaseCommand
from main.models import Kasus, Rekomendasi, KasusRekomendasi, RawatInap
from django.utils import timezone
from datetime import timedelta
import pandas as pd


class Command(BaseCommand):
    help = 'Seed relasi kasus dan rekomendasi'

    def handle(self, *args, **kwargs):
        # Read CSV with proper parsing
        df = pd.read_csv('dataset/df_merge.csv')
        
        # Parse the first row to get column names properly
        header_row = df.iloc[0]
        actual_columns = ['bulan', 'tahun', 'BOR', 'LOS', 'GDR'] + list(header_row[5:].values)
        
        # Re-read with proper column names
        df = pd.read_csv('dataset/df_merge.csv', names=actual_columns, skiprows=1)
        
        kolom_rekomendasi = df.columns.difference([
            'bulan', 'tahun', 'BOR', 'LOS', 'GDR'
        ])

        for _, row in df.iterrows():
            try:
                kasus = Kasus.objects.get(
                    bulan=str(int(row['bulan'])),
                    tahun=str(int(row['tahun']))
                )
            except Kasus.DoesNotExist:
                # Create kasus if not exists
                kasus = Kasus.objects.create(
                    bulan=str(int(row['bulan'])),
                    tahun=str(int(row['tahun'])),
                    bor=float(row['BOR']),
                    los=float(row['LOS']),
                    gdr=float(row['GDR'])
                )

            for kolom in kolom_rekomendasi:
                if str(row.get(kolom)).lower() in ['true', '1']:

                    try:
                        rekom = Rekomendasi.objects.get(rekomendasi=kolom)
                    except Rekomendasi.DoesNotExist:
                        continue

                    KasusRekomendasi.objects.get_or_create(
                        kasus=kasus,
                        rekomendasi=rekom
                    )

        # Seed RawatInap data from dataset.csv to database2 (rs_rekom)
        self.stdout.write("\n=== Seeding Data RawatInap dari dataset.csv ke rs_rekom ===")
        
        try:
            df_rawat = pd.read_csv('dataset/dataset.csv')
            created_count = 0
            updated_count = 0
            error_count = 0
            
            for index, row in df_rawat.iterrows():
                try:
                    # Parse tanggal dan jam
                    tgl_masuk = row['tgl_masuk']
                    jam_masuk = row['jam_masuk']
                    tgl_keluar = row['tgl_keluar'] if pd.notna(row['tgl_keluar']) else None
                    jam_keluar = row['jam_keluar'] if pd.notna(row['jam_keluar']) else None
                    
                    # Format datetime untuk masuk
                    if pd.notna(tgl_masuk) and pd.notna(jam_masuk):
                        datetime_masuk = pd.to_datetime(f"{tgl_masuk} {jam_masuk}")
                    else:
                        continue
                    
                    # Format datetime untuk keluar
                    datetime_keluar = None
                    if tgl_keluar and jam_keluar:
                        datetime_keluar = pd.to_datetime(f"{tgl_keluar} {jam_keluar}")
                    
                    # Mapping status pulang
                    stts_pulang_mapping = {
                        'Atas Persetujuan Dokter': RawatInap.StatusPulang.ATAS_PERSETUJUAN_DOKTER,
                        'Membaik': RawatInap.StatusPulang.MEMBAIK,
                        'Sembuh': RawatInap.StatusPulang.SEMBUH,
                        'Pindah Kamar': RawatInap.StatusPulang.PINDAH_KAMAR,
                        'Atas Permintaan Sendiri': RawatInap.StatusPulang.ATAS_PERMINTAAN_SENDIRI,
                        'Meninggal': RawatInap.StatusPulang.MENINGGAL
                    }
                    
                    stts_pulang = stts_pulang_mapping.get(row['stts_pulang'], None)
                    
                    rawat_inap_data = {
                        'no_rawat': row['no_rawat'],
                        'tgl_masuk': datetime_masuk,
                        'tgl_keluar': datetime_keluar,
                        'stts_pulang': stts_pulang
                    }
                    
                    # Insert ke database2 (rs_rekom)
                    rawat_inap, created = RawatInap.objects.using('database2').update_or_create(
                        no_rawat=row['no_rawat'],
                        defaults=rawat_inap_data
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(f"✅ Created: {row['no_rawat']}")
                    else:
                        updated_count += 1
                        self.stdout.write(f"🔄 Updated: {row['no_rawat']}")
                        
                except Exception as e:
                    error_count += 1
                    self.stdout.write(f"❌ Error processing row {index}: {str(e)}")
                    continue
            
            total_rawat_inap = RawatInap.objects.using('database2').count()
            self.stdout.write(f"\n=== Summary RawatInap ===")
            self.stdout.write(f"📝 Created: {created_count} records")
            self.stdout.write(f"🔄 Updated: {updated_count} records")
            self.stdout.write(f"❌ Errors: {error_count} records")
            self.stdout.write(f"📊 Total RawatInap di rs_rekom: {total_rawat_inap}")
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('❌ File dataset.csv tidak ditemukan di dataset/'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error reading dataset.csv: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('✨ Seeder relasi Kasus-Rekomendasi dan RawatInap dari dataset.csv berhasil!'))