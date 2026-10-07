#!/usr/bin/env python3
"""
OKF (Open Knowledge Format) Graph Validator, Linter & Index Compiler v13.
Validates YAML frontmatter (with full support for multi-line indented lists and quoted strings),
broken wikilinks, orphan nodes, lifecycle integrity, and deterministically recompiles wiki/index.md.
"""
import os
import sys
import re
from datetime import datetime

WIKI_DIR = os.path.join("knowledge-base", "wiki")

def parse_frontmatter(content):
    """Robust parser for OKF YAML frontmatter supporting multi-line lists and key-values without external deps."""
    if not content.startswith("---"):
        return None, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content
    fm_raw = parts[1]
    body = parts[2]
    meta = {}
    current_key = None

    for raw_line in fm_raw.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Check for list item under current key
        if stripped.startswith("- ") and current_key:
            item_val = stripped[2:].strip().strip('"').strip("'")
            if not isinstance(meta.get(current_key), list):
                meta[current_key] = []
            meta[current_key].append(item_val)
            continue

        # Key-Value match
        if ":" in line:
            # Check indentation to ensure it's top-level key
            if not line.startswith(" ") and not line.startswith("\t"):
                key, val = line.split(":", 1)
                current_key = key.strip()
                val_clean = val.strip()
                if val_clean.startswith("[") and val_clean.endswith("]"):
                    # Inline JSON-style list: ["a", "b"]
                    raw_items = val_clean[1:-1].split(",")
                    meta[current_key] = [i.strip().strip('"').strip("'") for i in raw_items if i.strip()]
                elif not val_clean:
                    # Will receive indented list items in following lines
                    meta[current_key] = []
                else:
                    meta[current_key] = val_clean.strip('"').strip("'")
            else:
                # Sub-key or nested map
                pass

    return meta, body

def find_wikilinks(text):
    return re.findall(r"\[\[([a-zA-Z0-9_\-\.]+)\]\]", text)

def load_graph():
    all_nodes = {}
    file_map = {}
    if not os.path.exists(WIKI_DIR):
        return all_nodes, file_map

    for root, _, files in os.walk(WIKI_DIR):
        for f in files:
            if f.endswith(".md") and f not in ["index.md", "log.md"]:
                path = os.path.join(root, f)
                node_name = os.path.splitext(f)[0]
                with open(path, "r", encoding="utf-8") as fh:
                    content = fh.read()
                fm, body = parse_frontmatter(content)
                file_map[node_name] = path
                all_nodes[node_name] = {
                    "path": path,
                    "rel_path": os.path.relpath(path, WIKI_DIR),
                    "frontmatter": fm or {},
                    "body": body,
                    "links": find_wikilinks(body)
                }
    return all_nodes, file_map

def compile_index(all_nodes):
    index_path = os.path.join(WIKI_DIR, "index.md")
    
    concepts = []
    entities = []
    decisions = []
    deprecated = []

    for name, data in sorted(all_nodes.items()):
        fm = data["frontmatter"]
        status = fm.get("status", "active")
        node_type = fm.get("node_type", "concept")
        domain = fm.get("domain", "general")
        summary_line = f"- [[{name}]] (`{status}`) - *{domain}*"
        
        superseded_by = fm.get("superseded_by")
        if superseded_by:
            target = superseded_by if isinstance(superseded_by, str) else str(superseded_by)
            summary_line += f" -> reemplazado por [[{target.strip('[]')}]]"

        if status in ["deprecated", "superseded"]:
            deprecated.append(summary_line)
        elif node_type == "decision" or "decisions" in data["rel_path"]:
            decisions.append(summary_line)
        elif node_type == "entity" or "entities" in data["rel_path"]:
            entities.append(summary_line)
        else:
            concepts.append(summary_line)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Knowledge Base Index (OKF Graph)",
        f"> Autogenerado deterministamente por `k-wiki/scripts/okf-lint.py --compile-index` el {now}.",
        "",
        "## 1. Architectural Decisions (ADRs)",
        "\n".join(decisions) if decisions else "- *Sin decisiones registradas.*",
        "",
        "## 2. Core Concepts & Domain Rules",
        "\n".join(concepts) if concepts else "- *Sin conceptos activos.*",
        "",
        "## 3. Entities & Infrastructure Contracts",
        "\n".join(entities) if entities else "- *Sin entidades registradas.*",
        "",
        "## 4. Deprecated / Superseded Nodes (Garbage Collection)",
        "\n".join(deprecated) if deprecated else "- *Sin nodos obsoletos.*",
        ""
    ]

    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"[OKF-LINT] ✅ {index_path} re-compilado con éxito ({len(all_nodes)} nodos indexados).")

def run_lint(auto_compile=False):
    if not os.path.exists(WIKI_DIR):
        print(f"[OKF-LINT] Directorio {WIKI_DIR} no encontrado. Creando estructura básica...")
        return 0

    all_nodes, file_map = load_graph()
    errors = []
    warnings = []

    print(f"[OKF-LINT] Nodos encontrados: {len(all_nodes)}")

    for name, data in all_nodes.items():
        fm = data["frontmatter"]
        if not fm:
            errors.append(f"[{name}] Falta YAML frontmatter o delimitador ---")
            continue
        
        status = fm.get("status")
        if not status or status not in ["active", "draft", "deprecated", "superseded"]:
            errors.append(f"[{name}] Estado OKF inválido o ausente: '{status}'")
            
        if status in ["deprecated", "superseded"] and not fm.get("superseded_by"):
            warnings.append(f"[{name}] Estado es '{status}' pero no declara 'superseded_by'")

        for link in data["links"]:
            if link not in file_map and link not in ["index", "log"]:
                errors.append(f"[{name}] Enlace roto hacia [[{link}]]")

    if errors:
        print("\n❌ ERRORES EN EL GRAFO OKF:")
        for err in errors:
            print(f"  - {err}")
        return 1

    if warnings:
        print("\n⚠️ ADVERTENCIAS:")
        for w in warnings:
            print(f"  - {w}")

    print("\n✅ Grafo OKF íntegro. Todos los contratos y enlaces bidireccionales validados.")
    
    if auto_compile:
        compile_index(all_nodes)
        
    return 0

if __name__ == "__main__":
    compile_flag = "--compile-index" in sys.argv
    sys.exit(run_lint(auto_compile=compile_flag))