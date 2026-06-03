SKILL_ALIASES: dict[str, str] = {
    "java": "Java",
    "JAVA": "Java",
    "spring": "Spring Boot",
    "Spring": "Spring Boot",
    "springboot": "Spring Boot",
    "SpringBoot": "Spring Boot",
    "spring boot": "Spring Boot",
    "python": "Python",
    "PYTHON": "Python",
    "javascript": "JavaScript",
    "Javascript": "JavaScript",
    "typescript": "TypeScript",
    "Typescript": "TypeScript",
    "mysql": "MySQL",
    "MYSQL": "MySQL",
    "postgresql": "PostgreSQL",
    "Postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "git": "Git",
    "GIT": "Git",
    "docker": "Docker",
    "DOCKER": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "selenium": "Selenium",
    "SELENIUM": "Selenium",
    "jira": "Jira",
    "JIRA": "Jira",
}


def normalize_skill(skill: str) -> str:
    return SKILL_ALIASES.get(skill.strip(), skill.strip())


def normalize_skills(raw_skills: list[str]) -> list[str]:
    return list(dict.fromkeys(normalize_skill(s) for s in raw_skills if s.strip()))
