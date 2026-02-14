def detect_target_role(primary_skills):
    """
    Suggest a target role based on primary skills.
    """

    skills = [s.lower() for s in primary_skills]

    if any(s in skills for s in ["java", "spring", "spring boot"]):
        return "Java Developer"

    if any(s in skills for s in ["python", "pandas", "airflow", "spark"]):
        return "Data Engineer"

    if any(s in skills for s in ["aws", "docker", "kubernetes", "jenkins"]):
        return "DevOps Engineer"

    if any(s in skills for s in ["selenium", "jest", "mocha", "junit"]):
        return "QA Engineer"

    if any(s in skills for s in ["react", "angular", "vue"]):
        return "Frontend Developer"

    if any(s in skills for s in ["sql", "tableau", "power bi"]):
        return "Data Analyst"

    return "Software Engineer"
