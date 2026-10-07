---
okf_version: "1.0"
node_type: concept
id: "environment-governor"
status: active
domain: "layer-3-environment"
governed_by: ["[[ADR-001-karpathy-3-layer-architecture]]"]
dependencies: []
supersedes: null
superseded_by: null
updated_at: "2026-10-07"
---

# [[environment-governor]]

## Resumen
La Capa 3 (Environment) de Karpathy gobierna la constitución del proyecto (`AGENTS.md`), la higiene del espacio de trabajo Git, la prevención de deriva ambiental y el aislamiento de ramas para permitir retrocesos atómicos sin pérdida de datos.

## Principios Clave y Contratos
- **Constitución del Proyecto (`AGENTS.md`):** Reglas inviolables, taxonomía de permisos operacionales y comandos CLI autorizados.
- **Stash Shield:** Prohibición estricta de iniciar ramas o tareas si el árbol de trabajo Git presenta modificaciones sin confirmar (`git status --porcelain`).
- **Aislamiento de Ramas y Aborto Atómico (`/task-abort`):** Todo trabajo se ejecuta en ramas de ciclo corto (`feat/`, `fix/`, `chore/`). El aborto atómico limpia artefactos sin ensuciar la rama principal.
- **Sincronización IaC y Deriva de Configuración:** Cualquier modificación de variables de entorno debe propagarse a manifiestos de Docker, Helm o Terraform.
- **Protección de Herramientas (Anti-Sabotage):** Prohibición terminante de modificar scripts del sistema y skills sin autorización humana explícita.

## Relaciones Arquitectónicas
- Gobernado por: [[ADR-001-karpathy-3-layer-architecture]]
- Conecta con: [[spec-driven-development]], [[open-knowledge-format]]
- Índice global: [[index]]
