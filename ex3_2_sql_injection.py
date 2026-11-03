"""Exercício 3.2 — PoC DEFENSIVA de SQL Injection (somente banco local de laboratório).

Com MySQL:  MYSQL_PASSWORD=... python -m aula03.ex3_2_sql_injection
Offline:    USE_SQLITE=1 python -m aula03.ex3_2_sql_injection   (mesma lógica, sqlite em memória)
"""
import os
import sqlite3

USAR_SQLITE = os.environ.get("USE_SQLITE") == "1"
PH = "?" if USAR_SQLITE else "%s"  # placeholder do driver


def conectar():
    if USAR_SQLITE:
        return sqlite3.connect(":memory:")
    import comum
    return comum.mysql_conn()


def preparar(con):
    cur = con.cursor()
    if USAR_SQLITE:
        cur.execute("CREATE TABLE usuarios (id INTEGER PRIMARY KEY, nome TEXT, email TEXT, nivel_acesso INT)")
    else:
        cur.execute("DROP TABLE IF EXISTS usuarios_poc")
        cur.execute("CREATE TABLE usuarios_poc (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(100), email VARCHAR(150), nivel_acesso INT)")
    tabela = "usuarios" if USAR_SQLITE else "usuarios_poc"
    cur.executemany(f"INSERT INTO {tabela} (nome, email, nivel_acesso) VALUES ({PH}, {PH}, {PH})",
                    [("Carlos Silva", "carlos@empresa.com", 3), ("Ana Costa", "ana@empresa.com", 5),
                     ("Bruno Lima", "bruno@empresa.com", 1)])
    con.commit()
    return tabela


def buscar_inseguro(con, tabela, nome):
    """❌ VULNERÁVEL: concatena a entrada na query."""
    cur = con.cursor()
    cur.execute("SELECT * FROM " + tabela + " WHERE nome = '" + nome + "'")
    return cur.fetchall()


def buscar_seguro(con, tabela, nome):
    """✅ Parametrizada: a entrada é sempre tratada como dado."""
    cur = con.cursor()
    cur.execute(f"SELECT * FROM {tabela} WHERE nome = {PH}", (nome,))
    return cur.fetchall()


if __name__ == "__main__":
    con = conectar()
    tab = preparar(con)
    entrada = "' OR '1'='1"
    n1 = len(buscar_inseguro(con, tab, entrada))
    n2 = len(buscar_seguro(con, tab, entrada))
    print(f"[INSEGURO] entrada: {entrada}  -> {n1} usuários retornados (VAZAMENTO!)")
    print(f"[SEGURO]   entrada: {entrada}  -> {n2} usuários retornados (defesa OK)")
    print("Conclusão: a query parametrizada tratou a entrada como texto literal.")
    con.close()
