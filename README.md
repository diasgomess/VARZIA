# VARZIA — Plataforma SaaS de Análise de Desempenho para Futebol de Várzea

Versão: 1.0

Uma plataforma SaaS que transforma gravações de partidas em dados táticos e estatísticas acionáveis para técnicos e times amadores.

## Visão geral

O VARZIA processa vídeos (upload ou transmissão ao vivo) para detectar jogadores, bola e eventos, gerar estatísticas, notas individuais, alertas táticos e recomendações por IA.

Principais capacidades:

- Processamento de vídeo e visão computacional (detecção, tracking, mapa de calor)
- Registro de eventos (passes, finalizações, recuperações, etc.)
- Engine de analytics para métricas e indicadores táticos
- Motor de recomendações + LLM para explicações e sugestões
- Dashboard em tempo real via WebSockets

## Tecnologias sugeridas

Frontend
- React / Next.js
- TypeScript
- Tailwind CSS
- Recharts

Backend
- Python + FastAPI
- PostgreSQL
- Redis
- Docker

Computer Vision
- Python, OpenCV, YOLO
- Tracker: ByteTrack ou DeepSORT

IA
- Pipeline de eventos estruturados → LLM para recomendações

## Estrutura inicial (MVP)

MVP em fases:

- Fase 1 — Gestão: cadastro, login, criação de time, cadastro de jogadores, criação de partida, escalação.
- Fase 2 — Estatísticas: registro manual de eventos, estatísticas individuais/coletivas, cálculo de notas.
- Fase 3 — IA: geração de insights, recomendações, chat com IA, relatório pós-jogo.
- Fase 4 — CV offline: upload de vídeo e processamento batch.
- Fase 5 — Tempo real: transmissão, processamento contínuo e alertas.

## Quickstart (desenvolvimento)

1. Clone o repositório
2. Crie um virtualenv Python e instale dependências (FastAPI, SQLAlchemy etc.)
3. Configure PostgreSQL e Redis
4. Inicie os serviços via docker-compose (a ser adicionado)

## API & WebSocket

A API principal será em FastAPI, expondo endpoints REST para autenticação, times, jogadores, partidas e eventos. O frontend receberá atualizações em tempo real por WebSocket para alerts e mapa de calor.

Endpoint MVP já disponível para estatísticas por jogador:
- `POST /matches/{match_id}/player-stats/recalculate`
- Payload: lista de `events` (`pass`, `shot`, `goal`, `tackle`, `distance`) e `player_positions`
- Retorno: estatísticas agregadas por `match/player` com `passes`, `shots`, `goals`, `tackles`, `distance` e `rating`

## Banco de dados (esboço)

Tabelas principais:
- users
- teams
- players
- matches
- events
- player_stats
- ai_insights

## Roadmap curto (prioridades)

1. MVP Fase 1: autenticação, times, jogadores, partidas
2. MVP Fase 2: registro manual de eventos + cálculo de métricas e notas
3. MVP Fase 3: motor de recomendações + integração com LLM

## Como contribuir

- Abra issues para features ou bugs
- Fork & PR: forneça testes e descrição clara das mudanças

## Licença

A definir (ex.: MIT)
