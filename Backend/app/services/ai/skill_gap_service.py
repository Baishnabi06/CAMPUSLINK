"""
Skill Gap Analysis Service
Analyzes student skills vs role requirements.
Returns missing skills with FREE online learning resources.
"""

from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class SkillResource:
    name: str
    url: str
    type: str   # "tutorial" | "video" | "practice" | "course" | "docs"
    free: bool = True

@dataclass
class SkillInfo:
    name: str
    category: str
    learning_hours: int
    resources: List[Dict[str, str]] = field(default_factory=list)

# ===========================================================
# SKILL DATABASE  —  each skill has 3-5 free resource links
# ===========================================================
SKILL_DATABASE: Dict[str, SkillInfo] = {

    # ── Programming Languages ──────────────────────────────
    "python": SkillInfo(
        name="Python", category="Programming Language", learning_hours=80,
        resources=[
            {"name": "W3Schools Python",      "url": "https://www.w3schools.com/python/",                    "type": "tutorial"},
            {"name": "GeeksforGeeks Python",  "url": "https://www.geeksforgeeks.org/python-programming-language/", "type": "tutorial"},
            {"name": "Python Official Docs",  "url": "https://docs.python.org/3/tutorial/",                  "type": "docs"},
            {"name": "freeCodeCamp Python",   "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "type": "course"},
            {"name": "Python on YouTube",     "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",         "type": "video"},
        ]
    ),
    "java": SkillInfo(
        name="Java", category="Programming Language", learning_hours=100,
        resources=[
            {"name": "W3Schools Java",        "url": "https://www.w3schools.com/java/",                      "type": "tutorial"},
            {"name": "GeeksforGeeks Java",    "url": "https://www.geeksforgeeks.org/java/",                  "type": "tutorial"},
            {"name": "Java Official Tutorials","url": "https://docs.oracle.com/javase/tutorial/",            "type": "docs"},
            {"name": "Java on YouTube (Telusko)", "url": "https://www.youtube.com/watch?v=BGTx91t8q50",      "type": "video"},
            {"name": "Programiz Java",        "url": "https://www.programiz.com/java-programming",           "type": "tutorial"},
        ]
    ),
    "c++": SkillInfo(
        name="C++", category="Programming Language", learning_hours=100,
        resources=[
            {"name": "W3Schools C++",         "url": "https://www.w3schools.com/cpp/",                       "type": "tutorial"},
            {"name": "GeeksforGeeks C++",     "url": "https://www.geeksforgeeks.org/c-plus-plus/",           "type": "tutorial"},
            {"name": "cppreference",          "url": "https://en.cppreference.com/w/",                       "type": "docs"},
            {"name": "LearnCpp",              "url": "https://www.learncpp.com/",                            "type": "tutorial"},
            {"name": "C++ on YouTube",        "url": "https://www.youtube.com/watch?v=vLnPwxZdW4Y",          "type": "video"},
        ]
    ),
    "c": SkillInfo(
        name="C", category="Programming Language", learning_hours=80,
        resources=[
            {"name": "W3Schools C",           "url": "https://www.w3schools.com/c/",                         "type": "tutorial"},
            {"name": "GeeksforGeeks C",       "url": "https://www.geeksforgeeks.org/c-programming-language/","type": "tutorial"},
            {"name": "Programiz C",           "url": "https://www.programiz.com/c-programming",              "type": "tutorial"},
            {"name": "C on YouTube",          "url": "https://www.youtube.com/watch?v=KJgsSFOSQv0",          "type": "video"},
        ]
    ),
    "javascript": SkillInfo(
        name="JavaScript", category="Programming Language", learning_hours=80,
        resources=[
            {"name": "W3Schools JavaScript",  "url": "https://www.w3schools.com/js/",                        "type": "tutorial"},
            {"name": "GeeksforGeeks JS",      "url": "https://www.geeksforgeeks.org/javascript/",            "type": "tutorial"},
            {"name": "JavaScript.info",       "url": "https://javascript.info/",                             "type": "tutorial"},
            {"name": "freeCodeCamp JS",       "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "type": "course"},
            {"name": "MDN JavaScript",        "url": "https://developer.mozilla.org/en-US/docs/Learn/JavaScript", "type": "docs"},
        ]
    ),
    "typescript": SkillInfo(
        name="TypeScript", category="Programming Language", learning_hours=60,
        resources=[
            {"name": "TypeScript Official Docs","url": "https://www.typescriptlang.org/docs/",               "type": "docs"},
            {"name": "W3Schools TypeScript",  "url": "https://www.w3schools.com/typescript/",                "type": "tutorial"},
            {"name": "GeeksforGeeks TypeScript","url": "https://www.geeksforgeeks.org/typescript/",          "type": "tutorial"},
            {"name": "TypeScript on YouTube", "url": "https://www.youtube.com/watch?v=BwuLxPH8IDs",          "type": "video"},
        ]
    ),
    "kotlin": SkillInfo(
        name="Kotlin", category="Programming Language", learning_hours=80,
        resources=[
            {"name": "Kotlin Official Docs",  "url": "https://kotlinlang.org/docs/home.html",                "type": "docs"},
            {"name": "GeeksforGeeks Kotlin",  "url": "https://www.geeksforgeeks.org/kotlin-programming-language/", "type": "tutorial"},
            {"name": "Kotlin on YouTube",     "url": "https://www.youtube.com/watch?v=F9UC9DY-vIU",          "type": "video"},
        ]
    ),
    "golang": SkillInfo(
        name="Go (Golang)", category="Programming Language", learning_hours=80,
        resources=[
            {"name": "Go Official Tour",      "url": "https://tour.golang.org/",                             "type": "tutorial"},
            {"name": "GeeksforGeeks Go",      "url": "https://www.geeksforgeeks.org/golang/",                "type": "tutorial"},
            {"name": "Go on YouTube",         "url": "https://www.youtube.com/watch?v=yyUHQIec83I",          "type": "video"},
        ]
    ),

    # ── Web Frontend ───────────────────────────────────────
    "html": SkillInfo(
        name="HTML", category="Frontend", learning_hours=30,
        resources=[
            {"name": "W3Schools HTML",        "url": "https://www.w3schools.com/html/",                      "type": "tutorial"},
            {"name": "GeeksforGeeks HTML",    "url": "https://www.geeksforgeeks.org/html-tutorial/",         "type": "tutorial"},
            {"name": "MDN HTML",              "url": "https://developer.mozilla.org/en-US/docs/Learn/HTML",  "type": "docs"},
            {"name": "freeCodeCamp HTML",     "url": "https://www.freecodecamp.org/learn/responsive-web-design/", "type": "course"},
        ]
    ),
    "css": SkillInfo(
        name="CSS", category="Frontend", learning_hours=40,
        resources=[
            {"name": "W3Schools CSS",         "url": "https://www.w3schools.com/css/",                       "type": "tutorial"},
            {"name": "GeeksforGeeks CSS",     "url": "https://www.geeksforgeeks.org/css-tutorial/",          "type": "tutorial"},
            {"name": "MDN CSS",               "url": "https://developer.mozilla.org/en-US/docs/Learn/CSS",   "type": "docs"},
            {"name": "CSS Tricks",            "url": "https://css-tricks.com/",                              "type": "tutorial"},
        ]
    ),
    "react": SkillInfo(
        name="React", category="Frontend Framework", learning_hours=70,
        resources=[
            {"name": "React Official Docs",   "url": "https://react.dev/learn",                              "type": "docs"},
            {"name": "W3Schools React",       "url": "https://www.w3schools.com/react/",                     "type": "tutorial"},
            {"name": "GeeksforGeeks React",   "url": "https://www.geeksforgeeks.org/reactjs/",               "type": "tutorial"},
            {"name": "freeCodeCamp React",    "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/", "type": "course"},
            {"name": "React on YouTube",      "url": "https://www.youtube.com/watch?v=bMknfKXIFA8",          "type": "video"},
        ]
    ),
    "angular": SkillInfo(
        name="Angular", category="Frontend Framework", learning_hours=80,
        resources=[
            {"name": "Angular Official Docs", "url": "https://angular.io/tutorial",                          "type": "docs"},
            {"name": "W3Schools Angular",     "url": "https://www.w3schools.com/angular/",                   "type": "tutorial"},
            {"name": "GeeksforGeeks Angular", "url": "https://www.geeksforgeeks.org/angularjs-tutorials/",   "type": "tutorial"},
            {"name": "Angular on YouTube",    "url": "https://www.youtube.com/watch?v=3qBXWUpoPHo",          "type": "video"},
        ]
    ),
    "vue.js": SkillInfo(
        name="Vue.js", category="Frontend Framework", learning_hours=60,
        resources=[
            {"name": "Vue Official Docs",     "url": "https://vuejs.org/guide/introduction.html",            "type": "docs"},
            {"name": "W3Schools Vue",         "url": "https://www.w3schools.com/vue/",                       "type": "tutorial"},
            {"name": "Vue on YouTube",        "url": "https://www.youtube.com/watch?v=FXpIoQ_rT_c",          "type": "video"},
        ]
    ),
    "bootstrap": SkillInfo(
        name="Bootstrap", category="Frontend", learning_hours=25,
        resources=[
            {"name": "W3Schools Bootstrap",   "url": "https://www.w3schools.com/bootstrap5/",                "type": "tutorial"},
            {"name": "Bootstrap Official Docs","url": "https://getbootstrap.com/docs/",                      "type": "docs"},
            {"name": "GeeksforGeeks Bootstrap","url": "https://www.geeksforgeeks.org/bootstrap/",            "type": "tutorial"},
        ]
    ),
    "responsive design": SkillInfo(
        name="Responsive Design", category="Frontend", learning_hours=30,
        resources=[
            {"name": "W3Schools Responsive",  "url": "https://www.w3schools.com/css/css_rwd_intro.asp",      "type": "tutorial"},
            {"name": "MDN Responsive Design", "url": "https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design", "type": "docs"},
            {"name": "freeCodeCamp Responsive","url": "https://www.freecodecamp.org/learn/responsive-web-design/", "type": "course"},
        ]
    ),

    # ── Backend ────────────────────────────────────────────
    "node.js": SkillInfo(
        name="Node.js", category="Backend", learning_hours=60,
        resources=[
            {"name": "W3Schools Node.js",     "url": "https://www.w3schools.com/nodejs/",                    "type": "tutorial"},
            {"name": "GeeksforGeeks Node.js", "url": "https://www.geeksforgeeks.org/nodejs/",                "type": "tutorial"},
            {"name": "Node.js Official Docs", "url": "https://nodejs.org/en/docs/",                          "type": "docs"},
            {"name": "Node.js on YouTube",    "url": "https://www.youtube.com/watch?v=TlB_eWDSMt4",          "type": "video"},
        ]
    ),
    "express": SkillInfo(
        name="Express.js", category="Backend", learning_hours=40,
        resources=[
            {"name": "Express Official Docs", "url": "https://expressjs.com/en/starter/installing.html",     "type": "docs"},
            {"name": "W3Schools Express",     "url": "https://www.w3schools.com/nodejs/nodejs_express.asp",  "type": "tutorial"},
            {"name": "GeeksforGeeks Express", "url": "https://www.geeksforgeeks.org/express-js/",            "type": "tutorial"},
            {"name": "Express on YouTube",    "url": "https://www.youtube.com/watch?v=SccSCuHhOw0",          "type": "video"},
        ]
    ),
    "django": SkillInfo(
        name="Django", category="Backend", learning_hours=70,
        resources=[
            {"name": "Django Official Docs",  "url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/", "type": "docs"},
            {"name": "GeeksforGeeks Django",  "url": "https://www.geeksforgeeks.org/django-tutorial/",       "type": "tutorial"},
            {"name": "W3Schools Django",      "url": "https://www.w3schools.com/django/",                    "type": "tutorial"},
            {"name": "Django on YouTube",     "url": "https://www.youtube.com/watch?v=PtQiiknWUcI",          "type": "video"},
        ]
    ),
    "fastapi": SkillInfo(
        name="FastAPI", category="Backend", learning_hours=50,
        resources=[
            {"name": "FastAPI Official Docs", "url": "https://fastapi.tiangolo.com/tutorial/",               "type": "docs"},
            {"name": "GeeksforGeeks FastAPI", "url": "https://www.geeksforgeeks.org/fastapi/",               "type": "tutorial"},
            {"name": "FastAPI on YouTube",    "url": "https://www.youtube.com/watch?v=7t2alSnE2-I",          "type": "video"},
        ]
    ),
    "flask": SkillInfo(
        name="Flask", category="Backend", learning_hours=50,
        resources=[
            {"name": "Flask Official Docs",   "url": "https://flask.palletsprojects.com/en/latest/tutorial/","type": "docs"},
            {"name": "GeeksforGeeks Flask",   "url": "https://www.geeksforgeeks.org/flask-tutorial/",        "type": "tutorial"},
            {"name": "W3Schools Flask",       "url": "https://www.w3schools.com/python/python_flask.asp",    "type": "tutorial"},
            {"name": "Flask on YouTube",      "url": "https://www.youtube.com/watch?v=Z1RJmh_OqeA",          "type": "video"},
        ]
    ),
    "spring boot": SkillInfo(
        name="Spring Boot", category="Backend", learning_hours=90,
        resources=[
            {"name": "Spring Official Docs",  "url": "https://spring.io/guides",                             "type": "docs"},
            {"name": "GeeksforGeeks Spring",  "url": "https://www.geeksforgeeks.org/spring-boot/",           "type": "tutorial"},
            {"name": "Spring Boot YouTube",   "url": "https://www.youtube.com/watch?v=9SGDpanrc8U",          "type": "video"},
        ]
    ),
    "rest api": SkillInfo(
        name="REST API", category="Backend", learning_hours=40,
        resources=[
            {"name": "GeeksforGeeks REST",    "url": "https://www.geeksforgeeks.org/rest-api-introduction/", "type": "tutorial"},
            {"name": "RESTful API Guide",     "url": "https://restfulapi.net/",                              "type": "tutorial"},
            {"name": "MDN HTTP",              "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP",    "type": "docs"},
            {"name": "REST API YouTube",      "url": "https://www.youtube.com/watch?v=lsMQRaeKNDk",          "type": "video"},
        ]
    ),

    # ── Databases ──────────────────────────────────────────
    "sql": SkillInfo(
        name="SQL", category="Database", learning_hours=60,
        resources=[
            {"name": "W3Schools SQL",         "url": "https://www.w3schools.com/sql/",                       "type": "tutorial"},
            {"name": "GeeksforGeeks SQL",     "url": "https://www.geeksforgeeks.org/sql-tutorial/",          "type": "tutorial"},
            {"name": "SQLZoo Practice",       "url": "https://sqlzoo.net/",                                  "type": "practice"},
            {"name": "Mode SQL Tutorial",     "url": "https://mode.com/sql-tutorial/",                       "type": "tutorial"},
            {"name": "SQL on YouTube",        "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY",          "type": "video"},
        ]
    ),
    "mysql": SkillInfo(
        name="MySQL", category="Database", learning_hours=50,
        resources=[
            {"name": "W3Schools MySQL",       "url": "https://www.w3schools.com/mysql/",                     "type": "tutorial"},
            {"name": "GeeksforGeeks MySQL",   "url": "https://www.geeksforgeeks.org/mysql-tutorial/",        "type": "tutorial"},
            {"name": "MySQL Official Docs",   "url": "https://dev.mysql.com/doc/refman/8.0/en/tutorial.html","type": "docs"},
        ]
    ),
    "mongodb": SkillInfo(
        name="MongoDB", category="Database", learning_hours=50,
        resources=[
            {"name": "MongoDB Official Docs", "url": "https://www.mongodb.com/docs/manual/tutorial/",        "type": "docs"},
            {"name": "W3Schools MongoDB",     "url": "https://www.w3schools.com/mongodb/",                   "type": "tutorial"},
            {"name": "GeeksforGeeks MongoDB", "url": "https://www.geeksforgeeks.org/mongodb-tutorial/",      "type": "tutorial"},
            {"name": "MongoDB University",    "url": "https://university.mongodb.com/",                      "type": "course"},
            {"name": "MongoDB YouTube",       "url": "https://www.youtube.com/watch?v=ofme2o29ngU",          "type": "video"},
        ]
    ),
    "postgresql": SkillInfo(
        name="PostgreSQL", category="Database", learning_hours=60,
        resources=[
            {"name": "PostgreSQL Official",   "url": "https://www.postgresql.org/docs/current/tutorial.html","type": "docs"},
            {"name": "W3Schools PostgreSQL",  "url": "https://www.w3schools.com/postgresql/",                "type": "tutorial"},
            {"name": "GeeksforGeeks PostgreSQL","url": "https://www.geeksforgeeks.org/postgresql-tutorial/", "type": "tutorial"},
        ]
    ),
    "database design": SkillInfo(
        name="Database Design", category="Database", learning_hours=60,
        resources=[
            {"name": "GeeksforGeeks DB Design","url": "https://www.geeksforgeeks.org/database-management-system/", "type": "tutorial"},
            {"name": "W3Schools DB",          "url": "https://www.w3schools.com/sql/sql_create_db.asp",      "type": "tutorial"},
            {"name": "DB Design YouTube",     "url": "https://www.youtube.com/watch?v=ztHopE5Wnpc",          "type": "video"},
        ]
    ),

    # ── DSA & CS Fundamentals ──────────────────────────────
    "dsa": SkillInfo(
        name="Data Structures & Algorithms", category="CS Fundamentals", learning_hours=150,
        resources=[
            {"name": "GeeksforGeeks DSA",     "url": "https://www.geeksforgeeks.org/data-structures/",       "type": "tutorial"},
            {"name": "W3Schools DSA",         "url": "https://www.w3schools.com/dsa/",                       "type": "tutorial"},
            {"name": "LeetCode Practice",     "url": "https://leetcode.com/",                                "type": "practice"},
            {"name": "freeCodeCamp Algorithms","url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "type": "course"},
            {"name": "DSA on YouTube",        "url": "https://www.youtube.com/watch?v=8hly31xKli0",          "type": "video"},
        ]
    ),
    "data structures": SkillInfo(
        name="Data Structures", category="CS Fundamentals", learning_hours=100,
        resources=[
            {"name": "GeeksforGeeks DS",      "url": "https://www.geeksforgeeks.org/data-structures/",       "type": "tutorial"},
            {"name": "W3Schools DSA",         "url": "https://www.w3schools.com/dsa/",                       "type": "tutorial"},
            {"name": "Visualgo (Visualize DS)","url": "https://visualgo.net/",                               "type": "tutorial"},
            {"name": "DS YouTube",            "url": "https://www.youtube.com/watch?v=RBSGKlAvoiM",          "type": "video"},
        ]
    ),
    "algorithms": SkillInfo(
        name="Algorithms", category="CS Fundamentals", learning_hours=100,
        resources=[
            {"name": "GeeksforGeeks Algorithms","url": "https://www.geeksforgeeks.org/fundamentals-of-algorithms/", "type": "tutorial"},
            {"name": "LeetCode Practice",     "url": "https://leetcode.com/",                                "type": "practice"},
            {"name": "HackerRank",            "url": "https://www.hackerrank.com/domains/algorithms",        "type": "practice"},
            {"name": "Algorithms YouTube",    "url": "https://www.youtube.com/watch?v=0IAPZzGSbME",          "type": "video"},
        ]
    ),
    "oops": SkillInfo(
        name="Object-Oriented Programming", category="CS Fundamentals", learning_hours=60,
        resources=[
            {"name": "GeeksforGeeks OOP",     "url": "https://www.geeksforgeeks.org/object-oriented-programming-oops-concept-in-java/", "type": "tutorial"},
            {"name": "W3Schools OOP (Python)","url": "https://www.w3schools.com/python/python_classes.asp",  "type": "tutorial"},
            {"name": "OOP YouTube",           "url": "https://www.youtube.com/watch?v=SiBw7os-_zI",          "type": "video"},
        ]
    ),
    "system design": SkillInfo(
        name="System Design", category="CS Fundamentals", learning_hours=120,
        resources=[
            {"name": "System Design Primer",  "url": "https://github.com/donnemartin/system-design-primer", "type": "tutorial"},
            {"name": "GeeksforGeeks System Design","url": "https://www.geeksforgeeks.org/system-design-tutorial/", "type": "tutorial"},
            {"name": "System Design YouTube", "url": "https://www.youtube.com/watch?v=xpDnVSmNFX0",          "type": "video"},
        ]
    ),
    "operating systems": SkillInfo(
        name="Operating Systems", category="CS Fundamentals", learning_hours=80,
        resources=[
            {"name": "GeeksforGeeks OS",      "url": "https://www.geeksforgeeks.org/operating-systems/",     "type": "tutorial"},
            {"name": "OS YouTube",            "url": "https://www.youtube.com/watch?v=vBURTt97EkA",          "type": "video"},
        ]
    ),
    "computer networks": SkillInfo(
        name="Computer Networks", category="CS Fundamentals", learning_hours=70,
        resources=[
            {"name": "GeeksforGeeks Networks","url": "https://www.geeksforgeeks.org/computer-network-tutorials/", "type": "tutorial"},
            {"name": "W3Schools Networking",  "url": "https://www.w3schools.com/whatis/whatis_protocol.asp", "type": "tutorial"},
            {"name": "Networks YouTube",      "url": "https://www.youtube.com/watch?v=qiQR5rTSshw",          "type": "video"},
        ]
    ),
    "computer networking": SkillInfo(
        name="Computer Networking", category="Networking", learning_hours=70,
        resources=[
            {"name": "GeeksforGeeks Networks","url": "https://www.geeksforgeeks.org/computer-network-tutorials/", "type": "tutorial"},
            {"name": "Cisco Networking Basics","url": "https://www.netacad.com/courses/networking/networking-basics", "type": "course"},
            {"name": "Networks YouTube",      "url": "https://www.youtube.com/watch?v=qiQR5rTSshw",          "type": "video"},
        ]
    ),
    "tcp/ip": SkillInfo(
        name="TCP/IP", category="Networking", learning_hours=30,
        resources=[
            {"name": "GeeksforGeeks TCP/IP",  "url": "https://www.geeksforgeeks.org/tcp-ip-model/",          "type": "tutorial"},
            {"name": "W3Schools TCP/IP",      "url": "https://www.w3schools.com/whatis/whatis_tcpip.asp",    "type": "tutorial"},
            {"name": "TCP/IP YouTube",        "url": "https://www.youtube.com/watch?v=2QGgEk20RXg",          "type": "video"},
        ]
    ),
    "lan/wan": SkillInfo(
        name="LAN/WAN", category="Networking", learning_hours=30,
        resources=[
            {"name": "GeeksforGeeks LAN/WAN", "url": "https://www.geeksforgeeks.org/difference-between-lan-and-wan/", "type": "tutorial"},
            {"name": "W3Schools LAN",         "url": "https://www.w3schools.com/whatis/whatis_lan.asp",      "type": "tutorial"},
            {"name": "LAN/WAN YouTube",       "url": "https://www.youtube.com/watch?v=R0kCBmrAnhk",          "type": "video"},
        ]
    ),
    "network security": SkillInfo(
        name="Network Security", category="Networking", learning_hours=80,
        resources=[
            {"name": "GeeksforGeeks Network Security","url": "https://www.geeksforgeeks.org/network-security/", "type": "tutorial"},
            {"name": "Cybersecurity on Coursera","url": "https://www.coursera.org/learn/ibm-cybersecurity-analyst", "type": "course"},
            {"name": "Network Security YouTube","url": "https://www.youtube.com/watch?v=inWWhr5tnEA",         "type": "video"},
        ]
    ),
    "routing & switching": SkillInfo(
        name="Routing & Switching", category="Networking", learning_hours=60,
        resources=[
            {"name": "GeeksforGeeks Routing", "url": "https://www.geeksforgeeks.org/types-of-routing/",      "type": "tutorial"},
            {"name": "Cisco NetAcad",         "url": "https://www.netacad.com/",                             "type": "course"},
            {"name": "Routing YouTube",       "url": "https://www.youtube.com/watch?v=AzXys5kxpAM",          "type": "video"},
        ]
    ),
    "dns": SkillInfo(
        name="DNS", category="Networking", learning_hours=20,
        resources=[
            {"name": "GeeksforGeeks DNS",     "url": "https://www.geeksforgeeks.org/domain-name-system-dns-in-application-layer/", "type": "tutorial"},
            {"name": "W3Schools DNS",         "url": "https://www.w3schools.com/whatis/whatis_dns.asp",      "type": "tutorial"},
            {"name": "DNS YouTube",           "url": "https://www.youtube.com/watch?v=mpQZVYPuDGU",          "type": "video"},
        ]
    ),
    "dhcp": SkillInfo(
        name="DHCP", category="Networking", learning_hours=20,
        resources=[
            {"name": "GeeksforGeeks DHCP",    "url": "https://www.geeksforgeeks.org/dynamic-host-configuration-protocol-dhcp/", "type": "tutorial"},
            {"name": "DHCP YouTube",          "url": "https://www.youtube.com/watch?v=S43CFcpOZSI",          "type": "video"},
        ]
    ),

    # ── Data Science & ML ──────────────────────────────────
    "machine learning": SkillInfo(
        name="Machine Learning", category="Data Science", learning_hours=120,
        resources=[
            {"name": "GeeksforGeeks ML",      "url": "https://www.geeksforgeeks.org/machine-learning/",      "type": "tutorial"},
            {"name": "Kaggle Learn ML",       "url": "https://www.kaggle.com/learn/intro-to-machine-learning","type": "course"},
            {"name": "ML on YouTube (Sentdex)","url": "https://www.youtube.com/watch?v=OGxgnH8y2NM",         "type": "video"},
            {"name": "Google ML Crash Course","url": "https://developers.google.com/machine-learning/crash-course", "type": "course"},
        ]
    ),
    "deep learning": SkillInfo(
        name="Deep Learning", category="Data Science", learning_hours=150,
        resources=[
            {"name": "GeeksforGeeks Deep Learning","url": "https://www.geeksforgeeks.org/deep-learning-tutorial/", "type": "tutorial"},
            {"name": "DeepLearning.AI",       "url": "https://www.deeplearning.ai/",                         "type": "course"},
            {"name": "Deep Learning YouTube", "url": "https://www.youtube.com/watch?v=aircAruvnKk",           "type": "video"},
        ]
    ),
    "pandas": SkillInfo(
        name="Pandas", category="Data Science", learning_hours=50,
        resources=[
            {"name": "Pandas Official Docs",  "url": "https://pandas.pydata.org/docs/getting_started/",      "type": "docs"},
            {"name": "GeeksforGeeks Pandas",  "url": "https://www.geeksforgeeks.org/pandas-tutorial/",       "type": "tutorial"},
            {"name": "W3Schools Pandas",      "url": "https://www.w3schools.com/python/pandas/",             "type": "tutorial"},
            {"name": "Kaggle Pandas",         "url": "https://www.kaggle.com/learn/pandas",                  "type": "course"},
        ]
    ),
    "numpy": SkillInfo(
        name="NumPy", category="Data Science", learning_hours=40,
        resources=[
            {"name": "NumPy Official Docs",   "url": "https://numpy.org/doc/stable/user/quickstart.html",    "type": "docs"},
            {"name": "GeeksforGeeks NumPy",   "url": "https://www.geeksforgeeks.org/numpy-tutorial/",        "type": "tutorial"},
            {"name": "W3Schools NumPy",       "url": "https://www.w3schools.com/python/numpy/",              "type": "tutorial"},
        ]
    ),
    "scikit-learn": SkillInfo(
        name="Scikit-learn", category="Data Science", learning_hours=60,
        resources=[
            {"name": "Scikit-learn Docs",     "url": "https://scikit-learn.org/stable/getting_started.html", "type": "docs"},
            {"name": "GeeksforGeeks Sklearn", "url": "https://www.geeksforgeeks.org/learning-model-building-scikit-learn-python-machine-learning-library/", "type": "tutorial"},
            {"name": "Kaggle ML",             "url": "https://www.kaggle.com/learn/intro-to-machine-learning","type": "course"},
        ]
    ),
    "tensorflow": SkillInfo(
        name="TensorFlow", category="Data Science", learning_hours=80,
        resources=[
            {"name": "TensorFlow Tutorials",  "url": "https://www.tensorflow.org/tutorials",                 "type": "docs"},
            {"name": "GeeksforGeeks TF",      "url": "https://www.geeksforgeeks.org/introduction-to-tensorflow/", "type": "tutorial"},
            {"name": "TensorFlow YouTube",    "url": "https://www.youtube.com/watch?v=tPYj3fFJGjk",          "type": "video"},
        ]
    ),
    "statistics": SkillInfo(
        name="Statistics", category="Mathematics", learning_hours=80,
        resources=[
            {"name": "Khan Academy Statistics","url": "https://www.khanacademy.org/math/statistics-probability", "type": "course"},
            {"name": "GeeksforGeeks Statistics","url": "https://www.geeksforgeeks.org/statistics/",          "type": "tutorial"},
            {"name": "W3Schools Statistics",  "url": "https://www.w3schools.com/statistics/",                "type": "tutorial"},
        ]
    ),
    "data visualization": SkillInfo(
        name="Data Visualization", category="Data Science", learning_hours=50,
        resources=[
            {"name": "GeeksforGeeks Data Viz","url": "https://www.geeksforgeeks.org/data-visualization-using-matplotlib/", "type": "tutorial"},
            {"name": "Kaggle Data Viz",       "url": "https://www.kaggle.com/learn/data-visualization",      "type": "course"},
            {"name": "Matplotlib Tutorials",  "url": "https://matplotlib.org/stable/tutorials/index.html",   "type": "docs"},
        ]
    ),
    "power bi": SkillInfo(
        name="Power BI", category="Data Analytics", learning_hours=60,
        resources=[
            {"name": "Microsoft Power BI Docs","url": "https://learn.microsoft.com/en-us/power-bi/fundamentals/power-bi-overview", "type": "docs"},
            {"name": "GeeksforGeeks Power BI","url": "https://www.geeksforgeeks.org/power-bi/",              "type": "tutorial"},
            {"name": "Power BI YouTube",      "url": "https://www.youtube.com/watch?v=fnA454XdCl0",          "type": "video"},
        ]
    ),
    "excel": SkillInfo(
        name="Excel", category="Data Analytics", learning_hours=40,
        resources=[
            {"name": "W3Schools Excel",       "url": "https://www.w3schools.com/excel/",                     "type": "tutorial"},
            {"name": "GeeksforGeeks Excel",   "url": "https://www.geeksforgeeks.org/ms-excel-tutorial/",     "type": "tutorial"},
            {"name": "Excel YouTube",         "url": "https://www.youtube.com/watch?v=rwbho0CgEAI",          "type": "video"},
        ]
    ),
    "yolov8": SkillInfo(
        name="YOLOv8", category="Computer Vision", learning_hours=60,
        resources=[
            {"name": "Ultralytics YOLOv8 Docs","url": "https://docs.ultralytics.com/",                      "type": "docs"},
            {"name": "GeeksforGeeks YOLO",    "url": "https://www.geeksforgeeks.org/yolo-you-only-look-once-real-time-object-detection/", "type": "tutorial"},
            {"name": "YOLOv8 YouTube",        "url": "https://www.youtube.com/watch?v=m9fH9OWn8YM",          "type": "video"},
        ]
    ),

    # ── DevOps & Tools ─────────────────────────────────────
    "git": SkillInfo(
        name="Git & GitHub", category="DevOps", learning_hours=25,
        resources=[
            {"name": "W3Schools Git",         "url": "https://www.w3schools.com/git/",                       "type": "tutorial"},
            {"name": "GeeksforGeeks Git",     "url": "https://www.geeksforgeeks.org/git-lets-get-into-it/",  "type": "tutorial"},
            {"name": "GitHub Skills",         "url": "https://skills.github.com/",                           "type": "course"},
            {"name": "Git on YouTube",        "url": "https://www.youtube.com/watch?v=RGOj5yH7evk",          "type": "video"},
        ]
    ),
    "docker": SkillInfo(
        name="Docker", category="DevOps", learning_hours=50,
        resources=[
            {"name": "Docker Official Docs",  "url": "https://docs.docker.com/get-started/",                 "type": "docs"},
            {"name": "GeeksforGeeks Docker",  "url": "https://www.geeksforgeeks.org/docker-tutorial/",       "type": "tutorial"},
            {"name": "Docker on YouTube",     "url": "https://www.youtube.com/watch?v=fqMOX6JJhGo",          "type": "video"},
            {"name": "Play With Docker",      "url": "https://labs.play-with-docker.com/",                   "type": "practice"},
        ]
    ),
    "kubernetes": SkillInfo(
        name="Kubernetes", category="DevOps", learning_hours=80,
        resources=[
            {"name": "Kubernetes Official Docs","url": "https://kubernetes.io/docs/tutorials/",              "type": "docs"},
            {"name": "GeeksforGeeks K8s",     "url": "https://www.geeksforgeeks.org/kubernetes-tutorial/",   "type": "tutorial"},
            {"name": "Kubernetes YouTube",    "url": "https://www.youtube.com/watch?v=X48VuDVv0do",          "type": "video"},
        ]
    ),
    "linux": SkillInfo(
        name="Linux", category="DevOps", learning_hours=60,
        resources=[
            {"name": "GeeksforGeeks Linux",   "url": "https://www.geeksforgeeks.org/linux-tutorial/",        "type": "tutorial"},
            {"name": "Linux Journey",         "url": "https://linuxjourney.com/",                            "type": "tutorial"},
            {"name": "freeCodeCamp Linux",    "url": "https://www.freecodecamp.org/news/the-linux-commands-handbook/", "type": "tutorial"},
            {"name": "Linux YouTube",         "url": "https://www.youtube.com/watch?v=sWbUDq4S6Y8",          "type": "video"},
        ]
    ),
    "aws": SkillInfo(
        name="AWS", category="Cloud", learning_hours=100,
        resources=[
            {"name": "AWS Official Docs",     "url": "https://aws.amazon.com/getting-started/",              "type": "docs"},
            {"name": "GeeksforGeeks AWS",     "url": "https://www.geeksforgeeks.org/aws-tutorial/",          "type": "tutorial"},
            {"name": "AWS on YouTube",        "url": "https://www.youtube.com/watch?v=k1RI5locZE4",          "type": "video"},
            {"name": "AWS Free Tier",         "url": "https://aws.amazon.com/free/",                         "type": "practice"},
        ]
    ),
    "azure": SkillInfo(
        name="Azure", category="Cloud", learning_hours=100,
        resources=[
            {"name": "Microsoft Azure Docs",  "url": "https://learn.microsoft.com/en-us/azure/",             "type": "docs"},
            {"name": "GeeksforGeeks Azure",   "url": "https://www.geeksforgeeks.org/microsoft-azure/",       "type": "tutorial"},
            {"name": "Azure YouTube",         "url": "https://www.youtube.com/watch?v=NKEFWyqJ5XA",          "type": "video"},
        ]
    ),
}

# ===========================================================
# ROLE → REQUIRED SKILLS MAP
# ===========================================================
ROLE_SKILLS: Dict[str, List[str]] = {
    "software engineer":     ["dsa", "python", "java", "sql", "git", "oops", "system design", "rest api"],
    "data scientist":        ["python", "machine learning", "statistics", "pandas", "numpy", "scikit-learn", "sql", "data visualization"],
    "web developer":         ["html", "css", "javascript", "react", "node.js", "sql", "git", "rest api"],
    "frontend developer":    ["html", "css", "javascript", "react", "bootstrap", "responsive design", "git"],
    "backend developer":     ["python", "django", "fastapi", "sql", "mongodb", "rest api", "git", "docker"],
    "data analyst":          ["python", "sql", "excel", "power bi", "statistics", "pandas", "data visualization"],
    "devops engineer":       ["linux", "docker", "kubernetes", "git", "aws", "python"],
    "network engineer":      ["computer networking", "tcp/ip", "lan/wan", "routing & switching", "dns", "dhcp", "network security"],
    "android developer":     ["java", "kotlin", "git", "rest api", "sql"],
    "full stack developer":  ["html", "css", "javascript", "react", "node.js", "express", "sql", "mongodb", "git", "rest api"],
    "ml engineer":           ["python", "machine learning", "deep learning", "tensorflow", "scikit-learn", "pandas", "numpy", "sql"],
}


# ===========================================================
# TYPE ICONS & LABELS for UI
# ===========================================================
RESOURCE_META = {
    "tutorial":  {"icon": "📖", "label": "Tutorial"},
    "video":     {"icon": "▶️", "label": "Video"},
    "practice":  {"icon": "💻", "label": "Practice"},
    "course":    {"icon": "🎓", "label": "Course"},
    "docs":      {"icon": "📄", "label": "Docs"},
}


def normalize(s: str) -> str:
    return s.strip().lower()


def calculate_skill_gap(student_skills: List[str], target_role: str) -> dict:
    """
    Core analysis function.
    Returns matched/missing skills + resources for missing ones.
    """
    role_key = normalize(target_role)
    if role_key not in ROLE_SKILLS:
        return {"error": f"Role '{target_role}' not found", "available_roles": list(ROLE_SKILLS.keys())}

    # Normalize student skills
    student_set = {normalize(s) for s in student_skills if s}

    required = ROLE_SKILLS[role_key]
    required_set = set(required)

    matched = sorted(s for s in required_set if s in student_set)
    missing = sorted(s for s in required_set if s not in student_set)

    match_pct = round(len(matched) / len(required_set) * 100) if required_set else 0

    # Severity
    if match_pct >= 80:
        severity, severity_label = "low",      "Well Prepared"
    elif match_pct >= 60:
        severity, severity_label = "medium",   "Almost There"
    elif match_pct >= 40:
        severity, severity_label = "high",     "Needs Work"
    else:
        severity, severity_label = "critical", "Major Gap"

    # Build matched skill details
    matched_details = []
    for s in matched:
        info = SKILL_DATABASE.get(s)
        matched_details.append({
            "key":      s,
            "name":     info.name if info else s.title(),
            "category": info.category if info else "General",
        })

    # Build missing skill details WITH resources
    missing_details = []
    for s in missing:
        info = SKILL_DATABASE.get(s)
        if info:
            resources = []
            for r in info.resources:
                meta = RESOURCE_META.get(r.get("type", "tutorial"), RESOURCE_META["tutorial"])
                resources.append({
                    "name":  r["name"],
                    "url":   r["url"],
                    "type":  r.get("type", "tutorial"),
                    "icon":  meta["icon"],
                    "label": meta["label"],
                })
            missing_details.append({
                "key":           s,
                "name":          info.name,
                "category":      info.category,
                "learning_hours": info.learning_hours,
                "learning_weeks": max(1, round(info.learning_hours / 20)),
                "resources":     resources,
            })
        else:
            missing_details.append({
                "key":           s,
                "name":          s.title(),
                "category":      "General",
                "learning_hours": 40,
                "learning_weeks": 2,
                "resources": [
                    {"name": f"GeeksforGeeks — {s.title()}", "url": f"https://www.geeksforgeeks.org/{s.replace(' ','-')}/", "type": "tutorial", "icon": "📖", "label": "Tutorial"},
                    {"name": f"W3Schools — {s.title()}",     "url": f"https://www.w3schools.com/{s.replace(' ','_')}/",     "type": "tutorial", "icon": "📖", "label": "Tutorial"},
                    {"name": f"YouTube — {s.title()}",       "url": f"https://www.youtube.com/results?search_query={s.replace(' ','+')}+tutorial", "type": "video", "icon": "▶️", "label": "Video"},
                ],
            })

    total_hours = sum(s["learning_hours"] for s in missing_details)

    return {
        "target_role":          target_role,
        "match_percentage":     match_pct,
        "severity":             severity,
        "severity_label":       severity_label,
        "total_required_skills": len(required_set),
        "matched_count":        len(matched),
        "missing_count":        len(missing),
        "matched_skills":       matched_details,
        "missing_skills":       missing_details,
        "total_learning_hours": total_hours,
        "estimated_weeks":      max(1, round(total_hours / 20)),
    }