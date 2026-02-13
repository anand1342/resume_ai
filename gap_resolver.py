def resolve_gaps(gaps):
    additional = []

    if not gaps:
        print("\n✅ No significant gaps detected.")
        return additional

    print("\n⚠️ GAP RESOLUTION (LATEST FIRST)\n")

    for gap in gaps:
        print(f"\nGap: {gap['from']} → {gap['to']} ({gap['duration_years']} years)")
        print(f"Between: {gap['between']}")

        choice = input("Fill this gap? (yes/no): ").strip().lower()
        if choice != "yes":
            continue

        exp_type = input("Type (Project/Contract/Training/Internship): ")
        company = input("Company/Project Name: ")
        role = input("Role: ")
        start = input("Start Date: ")
        end = input("End Date: ")
        desc = input("Short Description (optional): ")

        additional.append({
            "type": exp_type,
            "company": company,
            "role": role,
            "start": start,
            "end": end,
            "description": desc
        })

    return additional
