"""Exercício 3.3 — Relatório de alertas (MySQL): por severidade, por tipo e top IPs."""
import comum

ALERTAS = [
    ("BRUTE_FORCE", "10 falhas", "185.220.101.1", "critica"),
    ("BRUTE_FORCE", "8 falhas", "185.220.101.1", "critica"),
    ("BRUTE_FORCE", "6 falhas", "91.240.118.172", "alta"),
    ("BRUTE_FORCE", "5 falhas", "185.220.101.1", "alta"),
    ("PORT_SCAN", "7 portas", "45.33.32.156", "alta"),
    ("PORT_SCAN", "5 portas", "45.33.32.156", "media"),
    ("PORT_SCAN", "9 portas", "45.33.32.156", "critica"),
    ("XSS", "script na URL", "91.240.118.172", "alta"),
    ("XSS", "onerror", "192.168.1.50", "media"),
    ("SQLI", "' OR 1=1", "185.220.101.1", "baixa"),
]


def popular(con):
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS alertas (
        id INT AUTO_INCREMENT PRIMARY KEY, tipo VARCHAR(50), descricao TEXT, ip_origem VARCHAR(45),
        severidade ENUM('baixa','media','alta','critica'), criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    cur.execute("DELETE FROM alertas")
    cur.executemany("INSERT INTO alertas (tipo, descricao, ip_origem, severidade) VALUES (%s, %s, %s, %s)", ALERTAS)
    con.commit()


def consulta(con, sql):
    cur = con.cursor()
    cur.execute(sql)  # SQL fixo, sem entrada do usuário
    return cur.fetchall()


if __name__ == "__main__":
    con = comum.mysql_conn()
    popular(con)
    print("=== Por severidade ===")
    print(" | ".join(f"{s}: {n}" for s, n in consulta(con, "SELECT severidade, COUNT(*) FROM alertas GROUP BY severidade ORDER BY COUNT(*) DESC")))
    print("=== Por tipo ===")
    print(" | ".join(f"{t}: {n}" for t, n in consulta(con, "SELECT tipo, COUNT(*) FROM alertas GROUP BY tipo ORDER BY COUNT(*) DESC")))
    print("=== Top IPs de origem ===")
    for ip, n in consulta(con, "SELECT ip_origem, COUNT(*) FROM alertas GROUP BY ip_origem ORDER BY COUNT(*) DESC LIMIT 5"):
        print(f"{ip} -> {n} alertas")
    con.close()
