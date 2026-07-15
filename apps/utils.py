def extract_post_data(request, fields=None, ignore_fields=None) -> dict:
    """
    Extract POST and FILE data from request.
    - Normalizes text fields (lower + strip).
    - Leaves password fields untouched.
    - Allows optional field filtering and ignoring.
    """
    data = {}
    fields = fields or list(request.POST.keys()) + list(request.FILES.keys())
    ignore_fields = set(ignore_fields or [])

    for field in fields:
        if field in request.FILES:
            data[field] = request.FILES.get(field)
        elif field in request.POST:
            value = request.POST.get(field, "")
            if field in ignore_fields or "password" in field.lower():
                data[field] = value
            else:
                data[field] = value.lower().strip()

    return data