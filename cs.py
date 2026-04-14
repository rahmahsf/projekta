@login_required(login_url="login")
def dashboard(request):
    latest_kasus_overall = Kasus.objects.all().order_by("-tahun", "-bulan").first()

    selected_year = request.GET.get("year", None)
    kasus_list = Kasus.objects.all().order_by("-tahun", "-bulan")

    if selected_year:
        kasus_list = kasus_list.filter(tahun=selected_year)

    kasus_list = kasus_list[:12]
    kasus_list = list(kasus_list)
    kasus_list.reverse()

    latest_indikator = None
    indikator_changes = None

    if latest_kasus_overall:
        latest_indikator = {
            "bor": latest_kasus_overall.bor,
            "los": latest_kasus_overall.los,
            "gdr": latest_kasus_overall.gdr,
        }

        all_kasus_for_change = Kasus.objects.all().order_by("-tahun", "-bulan")[:2]
        if len(all_kasus_for_change) > 1:
            prev_kasus = all_kasus_for_change[1]
            indikator_changes = {
                "bor": float(latest_kasus_overall.bor) - float(prev_kasus.bor),
                "los": float(latest_kasus_overall.los) - float(prev_kasus.los),
                "gdr": float(latest_kasus_overall.gdr) - float(prev_kasus.gdr),
            }

    chart_data = {"labels": [], "bor": [], "los": [], "gdr": []}

    for kasus in kasus_list:
        chart_data["labels"].append(f"{kasus.bulan}-{kasus.tahun}")
        chart_data["bor"].append(kasus.bor)
        chart_data["los"].append(kasus.los)
        chart_data["gdr"].append(kasus.gdr)

    context = {
        "latest_indikator": latest_indikator,
        "indikator_changes": indikator_changes,
        "chart_data": chart_data,
    }

    return render(request, "main/dashboard.html", context)