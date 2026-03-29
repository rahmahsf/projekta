from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtract two numbers"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def bulan_nama(value):
    """Konversi angka bulan (int atau str) ke nama bulan Indonesia."""
    NAMA_BULAN = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember",
    }
    try:
        return NAMA_BULAN.get(int(value), str(value))
    except (ValueError, TypeError):
        return str(value)