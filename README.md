# Exercícios do 2º semestre — Coding for Security

Todos os exercícios das Aulas 1, 2, 3, 4, 6, 7, 8, 10, 11, 12 e 13 (as Aulas 5, 9 e 14 são check points e revisão, sem exercícios).

## Preparação

```bash
pip install -r requirements.txt
# MySQL: crie o banco uma vez ->  CREATE DATABASE seguranca;
export MYSQL_PASSWORD=...          # obrigatório nos exercícios com MySQL (nunca no código)
export MONGO_URI=mongodb://localhost:27017/   # opcional (este é o padrão)
export OPENAI_API_KEY=...          # opcional: sem chave, a aula 13 roda em modo mock/regras
```

Rode sempre da raiz desta pasta, com `python -m aulaNN.arquivo`. Contêineres do lab: `mongo-lab` e `mysql-lab`.

## Mapa

| Exercício | Arquivo | Precisa de |
|---|---|---|
| 1.1 | `aula01/ex1_1_vulnerabilidades.sql` | MySQL |
| 1.2 | `aula01/ex1_2_crud_alertas.sql` | MySQL |
| 1.3 | `aula01/decisoes_cap.md` | — |
| 2.1 | `aula02/ex2_1_inventario.py` | MongoDB |
| 2.2 | `aula02/ex2_2_ingestao_auth.py` (+ `dados/auth.log`, 23 linhas) | MongoDB |
| 2.3 | `aula02/ex2_3_consulta.py` (rode depois do 2.2) | MongoDB |
| 3.1 | `aula03/ex3_1_usuarios.py` | MySQL |
| 3.2 | `aula03/ex3_2_sql_injection.py` (`USE_SQLITE=1` roda offline) | MySQL ou sqlite |
| 3.3 | `aula03/ex3_3_relatorio_alertas.py` | MySQL |
| 4.1 a 4.3 | `aula04/ex4_*.py` | — |
| 6.1 a 6.3 | `aula06/ex6_*.py` | — |
| 7.1 e 7.2 | `aula07/ex7_1_7_2_incidentes_mongo.py` (um só app: CRUD + paginação/filtros) | MongoDB |
| 7.3 | `aula07/ex7_3_usuarios_mysql_api.py` | MySQL |
| 8.1, 8.2 | `aula08/ex8_1_dashboard_xss.py`, `ex8_2_login.py` | 8.2: MySQL |
| 8.3 | `aula08/auditoria.md` | — |
| 10.1 a 10.3 | `aula10/ex10_*.py` | internet |
| 11.1 a 11.3 | `aula11/ex11_*.py` | Docker |
| 12.1 a 12.3 | `aula12/ex12_*.py` | — |
| 13.1 a 13.3 | `aula13/ex13_*.py` (+ `llm_comum.py`) | OpenAI opcional |

## O que foi testado

`python testes_offline.py` roda sem bancos, Docker nem internet e passa em tudo. Ele cobre a lógica das aulas 2, 3.2 (com sqlite), 4, 6, 8, 10 (com respostas simuladas), 11.3 (contêiner falso), 12 e 13.
Todos os arquivos compilam, mas **não foram executados contra MongoDB, MySQL, Docker real, GitHub/NVD/ipinfo ou a API da OpenAI**: 1.1, 1.2, 2.1, 3.1, 3.3, 7.1 a 7.3, 8.2 (parte do banco), 11.1, 11.2 e as chamadas reais de rede. Rode esses no seu laboratório antes de entregar.

## Observações

- 12.1 e 12.2: com este dataset pequeno e bem separável, todos os modelos dão ~1,00 na validação cruzada, então o "torneio" empata e o vencedor sai pela ordem (RandomForest). A apostila mostra notas diferentes porque compara SVM e KNN sem escalar.
- 13.3: sem chave, a versão ingênua é um modelo **simulado** que obedece à injeção; com chave, o resultado depende do modelo real.
- Chaves e senhas só via variável de ambiente; em todo exercício com `app.run`, `debug=False`.
