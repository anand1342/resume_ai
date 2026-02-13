def resolve_gaps(gaps):
    additional = []

    if not gaps:
        print("\n✅ No significant gaps detected.")
        return additional

    print("\n⚠️ GAP RESOLUTION (LATEST FIRST)\n")

    for gap in gaps:
        print(f"\nGap: {gap.get('from')} → {gap.get('to')} ({gap.get('duration_years')} years)")
        print(f"Between: {gap.get('between')}")

        choice = input("Fill this gap? (yes/no): ").strip().lower()
        if choice != "yes":
            continue

        exp_type = input("Type (Project/Contract/Training/Internship): ").strip()
        company = input("Company/Project Name: ").strip()
        role = input("Role: ").strip()
        start = input("Start Date: ").strip()
        end = input("End Date: ").strip()
        desc = input("Short Description (optional): ").strip()

        additional.append({
            "type": exp_type,
            "company": company,
            "role": role,
            "start": start,
            "end": end,
            "description": desc
        })

    return additional
