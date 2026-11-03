-- Exercício 1.2 — CRUD SQL completo
CREATE DATABASE IF NOT EXISTS seguranca;
USE seguranca;
DROP TABLE IF EXISTS alertas;
CREATE TABLE alertas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(50), ip_origem VARCHAR(45),
    severidade ENUM('baixa','media','alta','critica'),
    status VARCHAR(20) DEFAULT 'aberto',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- (a) inserir 3 alertas (+1 para bater a saída esperada do item d)
INSERT INTO alertas (tipo, ip_origem, severidade) VALUES
    ('BRUTE_FORCE', '185.220.101.1', 'critica'),
    ('PORT_SCAN',   '45.33.32.156',  'alta'),
    ('XSS',         '91.240.118.172','alta'),
    ('SQLI',        '192.168.1.50',  'media');

-- (b) apenas severidade 'alta'
SELECT * FROM alertas WHERE severidade = 'alta';

-- (c) atualizar um alerta para 'resolvido'
UPDATE alertas SET status = 'resolvido' WHERE id = 2;

-- (d) contagem por severidade
SELECT severidade, COUNT(*) AS total
FROM alertas
GROUP BY severidade
ORDER BY FIELD(severidade, 'critica', 'alta', 'media', 'baixa');
-- critica 1 | alta 2 | media 1

-- (e) apagar alertas com mais de 90 dias
DELETE FROM alertas WHERE criado_em < NOW() - INTERVAL 90 DAY;
