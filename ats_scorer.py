def calculate_ats_score(skills, target_role):
    score = 0

    role_keywords = target_role.lower().split()

    for skill in skills["primary"]:
        if any(word in skill for word in role_keywords):
            score += 3
        else:
            score += 1

    score += len(skills["secondary"]) * 0.5

    return min(10, round(score, 1))
