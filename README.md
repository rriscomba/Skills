# Skills para Claude Code

Colección de skills reutilizables para [Claude Code](https://claude.ai/code), organizadas para instalación sencilla y mantenimiento escalable.

## Skills disponibles

| Skill | Descripción | Activador | Dominio |
|---|---|---|---|
| [bpmn-process-designer](skills/bpmn-process-designer/) | Convierte documentos narrativos o procedimentales en especificaciones intermedias BPMN 2.0 validadas, listas para diagramar o serializar a XML | Entrega un documento de proceso, manual, procedimiento o narrativa de negocio | Modelado de procesos |

---

## Instalación

### Opción A — Script automático

```bash
# Clonar el repositorio
git clone https://github.com/rriscomba/Skills.git
cd Skills

# Instalar un skill específico
./install.sh bpmn-process-designer

# Instalar todos los skills
./install.sh
```

### Opción B — Manual

Copiar la carpeta del skill a `~/.claude/skills/`:

```bash
cp -r skills/bpmn-process-designer ~/.claude/skills/
```

Después de instalar, el skill estará disponible automáticamente en todas las sesiones de Claude Code.

---

## Estructura del repositorio

```
skills/
└── <nombre-del-skill>/
    ├── SKILL.md          # Definición del skill (frontmatter + instrucciones)
    └── references/       # Archivos de referencia opcionales citados en SKILL.md
        └── *.md
```

### Formato de SKILL.md

```yaml
---
name: nombre-del-skill
description: >
  Descripción de cuándo Claude debe activar este skill.
  Incluir casos de uso concretos.
license: MIT
compatibility: markdown-skill
metadata:
  domain: <dominio>
  language: <idioma>
---

# Título del Skill

... instrucciones para Claude ...
```

---

## Cómo contribuir un nuevo skill

1. Crear la carpeta `skills/<nombre-del-skill>/`
2. Agregar `SKILL.md` con el formato indicado arriba
3. Agregar archivos de referencia en `references/` si aplica
4. Actualizar la tabla de skills en este README
5. Abrir un Pull Request

---

## Licencia

[Apache 2.0](LICENSE)
