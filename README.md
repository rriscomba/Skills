# Skills para Claude Code

Colección de skills reutilizables para Claude, organizadas para instalación sencilla y mantenimiento escalable. El repositorio incluye también herramientas complementarias, como el [Visualizador BPMN](tools/BPMN%20Viewer/), una aplicación HTML standalone para visualizar y editar diagramas BPMN 2.0 directamente en el navegador.

## Skills disponibles

| Skill | Descripción | Dominio | Descargar |
|---|---|---|---|
| [bpmn-process-designer](skills/bpmn-process-designer/) | Convierte documentos narrativos o procedimentales en especificaciones intermedias BPMN 2.0 validadas, listas para diagramar o exportar a XML | Modelado de procesos | [bpmn-process-designer.zip](dist/bpmn-process-designer.zip) |

## Herramientas disponibles

| Herramienta | Descripción | Usar |
|---|---|---|
| [BPMN Viewer](tools/BPMN%20Viewer/) | Aplicación HTML standalone para visualizar y editar diagramas BPMN 2.0 en el navegador, sin dependencias externas | [Abrir BPMN Viewer](tools/BPMN%20Viewer/BPMN%20Modeler.html) |

---

## Instalación

### Opción A — Claude Code Web (sin comandos)

1. Descarga el `.zip` del skill desde la tabla de arriba
2. En Claude Code web, ve a **Personalizar → Habilidades → Crear habilidad → Subir una habilidad**
3. Selecciona el `.zip` descargado
4. Listo — el skill queda activo en tu sesión

---

### Opción B — Terminal (desde el zip)

```bash
./install.sh bpmn-process-designer.zip
```

---

### Opción C — Terminal (manual, sin script)

```bash
unzip bpmn-process-designer.zip -d ~/.claude/skills/
```

---

### Opción D — Terminal (desde el repositorio)

```bash
git clone https://github.com/rriscomba/Skills.git
cd Skills
./install.sh bpmn-process-designer   # un skill
./install.sh                          # todos los skills
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
install.sh                         # Script de instalación por terminal
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
