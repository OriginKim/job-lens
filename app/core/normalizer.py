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
    "js": "JavaScript",
    "typescript": "TypeScript",
    "Typescript": "TypeScript",
    "ts": "TypeScript",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "Node": "Node.js",
    "react": "React",
    "ReactJS": "React",
    "vue": "Vue",
    "Vue.js": "Vue",
    "vuejs": "Vue",
    "mysql": "MySQL",
    "MYSQL": "MySQL",
    "postgresql": "PostgreSQL",
    "Postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "MongoDB": "MongoDB",
    "redis": "Redis",
    "REDIS": "Redis",
    "git": "Git",
    "GIT": "Git",
    "github": "GitHub",
    "Github": "GitHub",
    "docker": "Docker",
    "DOCKER": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "K8S": "Kubernetes",
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "linux": "Linux",
    "LINUX": "Linux",
    "selenium": "Selenium",
    "SELENIUM": "Selenium",
    "jira": "Jira",
    "JIRA": "Jira",
    "pytest": "Pytest",
    "PyTest": "Pytest",
    "junit": "JUnit",
    "Junit": "JUnit",
    "tensorflow": "TensorFlow",
    "Tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "pytorch": "PyTorch",
    "Pytorch": "PyTorch",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "jenkins": "Jenkins",
    "JENKINS": "Jenkins",
    "kafka": "Kafka",
    "KAFKA": "Kafka",
    "sql": "SQL",
    "SQL": "SQL",
    "rest": "REST",
    "REST API": "REST",
    "restapi": "REST",
    "graphql": "GraphQL",
    "GraphQL": "GraphQL",
}


def normalize_skill(skill: str) -> str:
    stripped = skill.strip()
    return SKILL_ALIASES.get(stripped, SKILL_ALIASES.get(stripped.lower(), stripped))


def normalize_skills(raw_skills: list[str]) -> list[str]:
    normalized = [normalize_skill(s) for s in raw_skills if s.strip()]
    return list(dict.fromkeys(normalized))


def skills_to_str(skills: list[str]) -> str:
    return ",".join(skills)


def str_to_skills(skills_str: str) -> list[str]:
    return [s.strip() for s in skills_str.split(",") if s.strip()]
