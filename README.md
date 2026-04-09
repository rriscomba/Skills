# Skills para Claude Code

Colección de skills reutilizables para [Claude Code](https://claude.ai/code), organizadas para instalación sencilla y mantenimiento escalable.

## Skills disponibles

| Skill | Descripción | Dominio | Descargar |
|---|---|---|---|
| [bpmn-process-designer](skills/bpmn-process-designer/) | Convierte documentos narrativos o procedimentales en especificaciones intermedias BPMN 2.0 validadas, listas para diagramar o exportar a XML | Modelado de procesos | [bpmn-process-designer.zip](dist/bpmn-process-designer.zip) |

---

## Instalación

### Opción A — Desde el zip (recomendado)

1. Descarga el `.zip` del skill desde la tabla de arriba
2. Ejecuta:

```bash
./install.sh bpmn-process-designer.zip
```

Listo. El skill queda disponible en todas las sesiones de Claude Code.

---

### Opción B — Desde el repositorio

```bash
# Clonar el repositorio
git clone https://github.com/rriscomba/Skills.git
cd Skills

# Instalar un skill específico
./install.sh bpmn-process-designer

# Instalar todos los skills
./install.sh
```

---

### Opción C — Manual (sin script)

```bash
unzip bpmn-process-designer.zip -d ~/.claude/skills/
```

---

## Estructura del repositorio

```
dist/                              # Zips listos para descargar e instalar
skills/
└── <nombre-del-skill>/
    ├── SKILL.md                   # Definición del skill
    └── references/                # Archivos de referencia opcionales
        └── *.md
install.sh                         # Script de instalación
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
4. Empaquetar: `cd skills && zip -r ../dist/<nombre-del-skill>.zip <nombre-del-skill>/`
5. Actualizar la tabla de skills en este README
6. Abrir un Pull Request

---

## Licencia

[Apache 2.0](LICENSE)
