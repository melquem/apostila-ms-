# Exercício 1.3 — Decisões de arquitetura com CAP

Em partição de rede a escolha real é entre CP e AP (P é obrigatório).

| Cenário | CP/AP | Justificativa |
|---|---|---|
| 1. Saldo bancário de clientes | **CP** | Saldo errado ou divergente entre nós gera perda financeira. Melhor recusar a operação durante a partição do que aceitar um saldo inconsistente. |
| 2. Ingestão de 500 mil eventos de firewall/min | **AP** | Parar de aceitar logs durante um ataque é pior do que ter consistência eventual. Perder ou atrasar alguns segundos de telemetria é tolerável. |
| 3. Cache de tokens de sessão | **AP** (CP para sessões críticas) | Cache é descartável: se um nó cai, o usuário refaz o login. Para sessões de alto risco (admin, pagamentos) a revogação precisa ser consistente, e aí se prefere CP. |
| 4. Registro de quem autorizou cada transferência (auditoria) | **CP** | A trilha de auditoria precisa ser única, completa e sem divergência. Um registro faltando ou duplicado invalida a auditoria. |
| 5. Feed de IOCs replicado em 5 regiões | **AP** | Cada região deve continuar consultando IOCs mesmo isolada. Um IOC que chega alguns segundos depois (consistência eventual) é aceitável. |
