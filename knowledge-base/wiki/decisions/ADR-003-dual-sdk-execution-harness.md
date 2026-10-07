---
okf_version: "1.0"
node_type: decision
id: "ADR-003-dual-sdk-execution-harness"
status: active
domain: "agentic-execution-harness"
governed_by: ["[[ADR-001-karpathy-3-layer-architecture]]"]
dependencies: []
supersedes: null
superseded_by: null
updated_at: "2026-10-07"
---

# ADR-003: Arnés de Ejecución Desacoplado con Soporte Dual para Google Antigravity y GitHub Copilot SDK

## Contexto y Problema
En el desarrollo de software agéntico con Karpathy SDLC (`k-method`), los modelos de lenguaje ligeros o de alta eficiencia (como OpenAI GPT-6 Luna) pueden sufrir de degradación de contexto, omisión de puertas de parada humana (*sycophancy*) o bucles infinitos en fallos de tests si se les otorga el control total de la máquina de estados. Asimismo, conviven dos entornos de uso principales: pruebas y desarrollo local personal mediante Google Antigravity SDK, y despliegues corporativos profesionales mediante GitHub Copilot SDK.

## Decisión
Se implementa un arnés de ejecución externo basado en el principio **"Code > Prompt"**:
1. **Patrón Adaptador (*Provider Pattern*):** El arnés abstrae los proveedores en `BaseAgentProvider`, soportando llamadas atómicas e independientes (*Zero-History Context*) con `CopilotProvider` y `AntigravityProvider`.
2. **Máquina de Estados en Código Determinista:** El arnés gobierna las fases del SDLC, valida el límite duro de 6 Criterios de Aceptación, ejecuta el *Stash Shield* de Git, y activa el *Deadlock Circuit Breaker* al segundo fallo idéntico en TDD.
3. **Invariante de Inmutabilidad de Skills:** Las directivas y scripts de `.agents/skills/` permanecen inmutables y de solo lectura. El arnés las consume como referencias sin modificarlas.

## Consecuencias
- **Positivas:** 
  - Permite ejecutar modelos de alta eficiencia y bajo coste (como GPT-6 Luna) con fiabilidad de grado enterprise.
  - Alternancia transparente entre Antigravity SDK y Copilot SDK sin alterar las directivas de las skills.
  - Redacción automática de credenciales sensibles en logs y excepciones.
- **Negativas / Costes:** Mantenimiento de la capa de adaptación y pruebas de contrato cuando los SDKs de terceros introduzcan cambios de versión.

## Enlaces Relacionados
- [[ADR-001-karpathy-3-layer-architecture]]
- [[ADR-002-multi-platform-ci-pr-strategy]]
- [[antigravity-skills-engine]]
- [[environment-governor]]
- [[verifier-driven-development]]
- [[index]]
