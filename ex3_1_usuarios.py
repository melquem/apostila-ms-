"""Exercício 3.1 — CRUD de usuários no MySQL (menu, tudo parametrizado).
Variáveis: MYSQL_PASSWORD (obrigatória), MYSQL_HOST, MYSQL_USER, MYSQL_DATABASE.
"""
import comum

USUARIOS_INICIAIS = [("Carlos Silva", "carlos@empresa.com", 3),
                     ("Ana Costa", "ana@empresa.com", 5),
                     ("Bruno Lima", "bruno@empresa.com", 1)]


def criar_tabela(con):
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(150) NOT NULL UNIQUE,
        nivel_acesso INT NOT NULL DEFAULT 1,
        CONSTRAINT chk_nivel CHECK (nivel_acesso BETWEEN 1 AND 5))""")
    con.commit()


def validar_nivel(nivel):
    try:
        n = int(nivel)
    except (TypeError, ValueError):
        return None
    return n if 1 <= n <= 5 else None


def cadastrar(con, nome, email, nivel):
    from mysql.connector import IntegrityError
    n = validar_nivel(nivel)
    if n is None:
        return "Erro: nível deve estar entre 1 e 5"
    try:
        cur = con.cursor()
        cur.execute("INSERT INTO usuarios (nome, email, nivel_acesso) VALUES (%s, %s, %s)", (nome, email, n))
        con.commit()
        return "Usuário cadastrado!"
    except IntegrityError:
        con.rollback()
        return "Erro: email já existe"


def listar(con):
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT nome, email, nivel_acesso FROM usuarios ORDER BY id")
    for u in cur.fetchall():
        print(f"{u['nome']:13s}| {u['email']:19s}| nível {u['nivel_acesso']}")


def buscar_por_email(con, email):
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT nome, email, nivel_acesso FROM usuarios WHERE email = %s", (email,))
    return cur.fetchone()


def alterar_nivel(con, email, nivel):
    n = validar_nivel(nivel)
    if n is None:
        return "Erro: nível deve estar entre 1 e 5"
    cur = con.cursor()
    cur.execute("UPDATE usuarios SET nivel_acesso = %s WHERE email = %s", (n, email))
    con.commit()
    return "Nível atualizado!" if cur.rowcount else "Erro: usuário não encontrado"


def remover(con, email):
    cur = con.cursor()
    cur.execute("DELETE FROM usuarios WHERE email = %s", (email,))
    con.commit()
    return "Usuário removido!" if cur.rowcount else "Erro: usuário não encontrado"


def menu(con):
    while True:
        print("\n[1] Cadastrar [2] Listar [3] Buscar [4] Promover/rebaixar [5] Remover [6] Sair")
        op = input("Opção: ").strip()
        if op == "1":
            print(cadastrar(con, input("Nome: "), input("Email: ").strip(), input("Nível (1-5): ")))
        elif op == "2":
            listar(con)
        elif op == "3":
            print(buscar_por_email(con, input("Email: ").strip()) or "Não encontrado")
        elif op == "4":
            print(alterar_nivel(con, input("Email: ").strip(), input("Novo nível (1-5): ")))
        elif op == "5":
            print(remover(con, input("Email: ").strip()))
        elif op == "6":
            break
        else:
            print("Opção inválida")


if __name__ == "__main__":
    conexao = comum.mysql_conn()
    criar_tabela(conexao)
    for n, e, nv in USUARIOS_INICIAIS:
        cadastrar(conexao, n, e, nv)
    print(cadastrar(conexao, "Outro", "carlos@empresa.com", 2))  # duplicado -> erro
    menu(conexao)
    conexao.close()
