# **Mixamo-Blender-4-Plugin erweitern**  

## **So einfach geht's:**  

1. **Original-Plugin herunterladen**  
   - Von [GitLab](https://gitlab.com/x190/mixamo_blender4).  

2. **Dateien ersetzen**  
   - Füge die modifizierte [`__init__.py`](#) in den Plugin-Ordner.  
   - Lege die neue Datei `mixamo_rename_opensim.py` daneben.  

3. **Fertig!**  
   - Starte Blender neu – die OpenSim-Funktion ist jetzt aktiv.  

## **Für Entwickler:**  

- Die Änderung ist nur in `__init__.py` und betrifft:  

  ```python
  # Neu hinzugefügt:
  if "mixamo_rename_opensim" in locals():
      importlib.reload(mixamo_rename_opensim)
  from . import mixamo_rename_opensim
  ```

  ... plus `register()`/`unregister()`.  

---

**Warum das funktioniert:**  

- Deine Änderungen sind **minimal** und bleiben nah am Original.  
- Keine komplexen Anpassungen nötig – nur Austausch + eine neue Datei.


Based on: https://www.adobe.com/products/substance3d/plugins/mixamo-in-blender.html

Download the version from that link for Blender versions older than 4.0

