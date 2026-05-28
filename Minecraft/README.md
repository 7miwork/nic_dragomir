# Minecraft Clone - Python Edition

Ein funktionsfähiger Minecraft-Klon in Python mit PyGame und OpenGL.

## Features

✨ **Implementierte Features:**
- 🎮 First-Person-Steuerung mit Maus und Tastatur
- 🌍 Prozedurale Terrain-Generierung mit Simplex Noise
- 🧱 Mehrere Blocktypen (Gras, Erde, Stein, Holz, Sand, Wasser, Blätter)
- 🌲 Automatische Baum-Generierung
- ⛏️ Blöcke abbauen und platzieren
- ✈️ Flugmodus
- 🎯 Crosshair für Block-Auswahl
- 🌫️ Nebel-Effekte für Render-Distanz
- ⚡ Optimiertes Rendering mit Face Culling und Display Lists
- 🗺️ Chunk-basiertes Weltmanagement

## Installation

### Voraussetzungen
- Python 3.8 oder höher
- pip (Python Package Manager)

### Schritt 1: Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

Oder manuell:
```bash
pip install pygame PyOpenGL PyOpenGL-accelerate numpy
```

### Schritt 2: Spiel starten

```bash
python minecraft_clone.py
```

## Steuerung

### Bewegung
- **W** - Vorwärts
- **A** - Links
- **S** - Rückwärts
- **D** - Rechts
- **Maus** - Umschauen
- **Leertaste** - Springen (oder nach oben im Flugmodus)
- **Shift** - Nach unten (nur im Flugmodus)

### Interaktion
- **Linke Maustaste** - Block zerstören
- **Rechte Maustaste** - Block platzieren
- **F** - Flugmodus ein/aus

### Block-Auswahl
- **1** - Gras
- **2** - Erde
- **3** - Stein
- **4** - Holz
- **5** - Sand

### Sonstiges
- **ESC** - Spiel beenden

## Technische Details

### Architektur
- **Chunk-System**: Die Welt ist in 16x16x64 Chunks aufgeteilt für effizientes Rendering
- **Terrain-Generierung**: Verwendet Simplex Noise für realistische Landschaften
- **Face Culling**: Nur sichtbare Blockflächen werden gerendert
- **Display Lists**: OpenGL Display Lists für bessere Performance

### Performance-Tipps
- Render-Distanz kann in `RENDER_DISTANCE` angepasst werden (Standard: 8 Chunks)
- Bei langsamer Performance `RENDER_DISTANCE` reduzieren
- Face Culling und Display Lists sind bereits implementiert für optimale Performance

### Erweiterungsmöglichkeiten

Das Projekt kann einfach erweitert werden:
1. **Mehr Blocktypen**: Einfach neue Einträge zu `BLOCK_COLORS` hinzufügen
2. **Texturen**: Aktuell verwendet das Spiel Farben - kann auf Texturen erweitert werden
3. **Biome**: Verschiedene Terraintypen basierend auf Position
4. **Mobs/Kreaturen**: NPCs und Feinde hinzufügen
5. **Crafting-System**: Rezepte und Inventar implementieren
6. **Tag/Nacht-Zyklus**: Beleuchtung und Zeitwechsel
7. **Multiplayer**: Netzwerk-Funktionalität

## Bekannte Limitierungen

- Keine Texturen (nur Farben)
- Vereinfachte Physik
- Keine Speicher-/Ladefunktion
- Begrenzte Welthöhe (64 Blöcke)

## Fehlerbehebung

**Problem: "ModuleNotFoundError: No module named 'OpenGL'"**
Lösung: `pip install PyOpenGL PyOpenGL-accelerate`

**Problem: Spiel läuft langsam**
Lösung: Reduziere `RENDER_DISTANCE` in der minecraft_clone.py (Zeile 13)

**Problem: Schwarzer Bildschirm**
Lösung: Stelle sicher, dass deine Grafikkarte OpenGL unterstützt

## Lizenz

Dieses Projekt ist ein Lern- und Demo-Projekt. Frei verwendbar für Bildungszwecke.

## Credits

Erstellt mit Python, PyGame und PyOpenGL
Inspiriert von Minecraft (Mojang Studios)
