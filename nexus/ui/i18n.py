"""Locale-aware UI translations selected from the system language."""

from functools import lru_cache

from PyQt5.QtCore import QLocale


_ENGLISH = {
    "Asignar a pedal": "Assign to a pedal",
    "— Ninguno —": "— None —",
    "Quitar asignación": "Clear assignment",
    "Pedal de expresión": "Expression pedal",
    "Asignar a slot": "Assign to slot",
    "Parámetro": "Parameter",
    "Asignar": "Assign",
    "Amplificadores": "Amplifiers",
    "Distorsión": "Distortion",
    "Compresor": "Compressor",
    "Modulación": "Modulation",
    "Volumen": "Volume",
    "Seleccionar efecto": "Select effect",
    "Cancelar": "Cancel",
    "Cambiar efecto...": "Change effect...",
    "Eliminar": "Delete",
    "Tempo de esta sesión; no se lee del pedal": "Session tempo; not read from the pedal",
    "Pulsa al ritmo; una pausa de 3 segundos reinicia la medición": (
        "Tap in time; a 3-second pause resets the measurement"
    ),
    "La conversión a velocidad LFO es aproximada": "LFO speed conversion is approximate",
    "Off conserva los valores del preset. "
    "La sincronización se aplica al cambiar el tempo.": (
        "Off preserves the preset values. Synchronization is applied when the tempo changes."
    ),
    "Tempo fuera del rango 20–300 BPM; vuelve a marcar": (
        "Tempo outside the 20–300 BPM range; tap again"
    ),
    "LFO: {hz:.2f} Hz fuera del rango 0.05–10 Hz": (
        "LFO: {hz:.2f} Hz is outside the 0.05–10 Hz range"
    ),
    "Clic en la placa para cambiar amplificador": "Click the panel to change amplifier",
    "Amplificador": "Amplifier",
    "Conectando...": "Connecting...",
    "Guardar": "Save",
    "Recargar": "Reload",
    "MIS TONOS": "MY TONES",
    "Buscar...": "Search...",
    "— vacío —": "— empty —",
    "Desconectado: {error}": "Disconnected: {error}",
    "Archivo": "File",
    "Importar preset...": "Import preset...",
    "Exportar preset...": "Export preset...",
    "Selección de amplificador": "Select amplifier",
    "sin asignación": "unassigned",
    "Tempo: conecta el pedal y carga un preset": "Tempo: connect the pedal and load a preset",
    "Delay sin parámetro TIME compatible": "Delay has no compatible TIME parameter",
    "Delay: {value} ms fuera del rango {low}–{high} ms": (
        "Delay: {value} ms is outside the {low}–{high} ms range"
    ),
    "Rango de delay desconocido": "Unknown delay range",
    "LFO sin asignar": "LFO is not assigned",
    "Los presets del dispositivo serán sobrescritos. ¿Continuar?": (
        "The device presets will be overwritten. Continue?"
    ),
    "Importado: {name}": "Imported: {name}",
    "Restaurados {count} presets": "Restored {count} presets",
    "Nombre del preset:": "Preset name:",
    "Guardado en User {slot}": "Saved to User {slot}",
    "Selecciona un slot de User": "Select a User slot",
    "Quick store en User {slot}": "Quick stored to User {slot}",
    "Reemplazar {label} por «Preset {slot}» con el amplificador y gabinete "
    "predeterminados, sin otros efectos? La posición no quedará vacía. "
    "El preset cargado en el editor no cambiará. Esta operación no se puede deshacer.": (
        "Replace {label} with “Preset {slot}” using the default amplifier and cabinet, "
        "with no other effects? The slot will not be empty. The preset loaded in the "
        "editor will not change. This cannot be undone."
    ),
    "Error al eliminar: {error}": "Error deleting preset: {error}",
    "el dispositivo no devolvió el preset predeterminado": (
        "the device did not return the expected default preset"
    ),
    "Preset User {slot}: escritura enviada; error al verificar: {error}": (
        "Preset User {slot}: write sent; verification error: {error}"
    ),
    "Preset User {slot} restablecido; error al actualizar: {error}": (
        "Preset User {slot} reset; update error: {error}"
    ),
    "Preset User {slot} restablecido": "Preset User {slot} reset",
    "Error al copiar: {error}": "Error copying preset: {error}",
    "Preset copiado al portapapeles interno": "Preset copied to the internal clipboard",
    "Error al reordenar: {error}": "Error reordering: {error}",
    "No hay preset cargado": "No preset loaded",
    "Cadena completa: todas las categorías están en uso": (
        "Chain is full: all categories are in use"
    ),
    "No hay posición libre en la cadena": "No free slot in the chain",
}


_CATALOGS = {
    "es": {
        "Assign to a pedal": "Asignar al pedal",
        "— None —": "— Ninguno —",
        "Clear assignment": "Quitar asignación",
        "Expression pedal": "Pedal de expresión",
        "Assign to slot": "Asignar a slot",
        "Parameter": "Parámetro",
        "Assign": "Asignar",
        "Amplifiers": "Amplificadores",
        "Distortion": "Distorsión",
        "Compressor": "Compresor",
        "Modulation": "Modulación",
        "Volume": "Volumen",
        "Select effect": "Seleccionar efecto",
        "Cancel": "Cancelar",
        "Change effect...": "Cambiar efecto...",
        "Delete": "Eliminar",
        "Session tempo; not read from the pedal": "Tempo de esta sesión; no se lee del pedal",
        "Tap in time; a 3-second pause resets the measurement": (
            "Pulsa al ritmo; una pausa de 3 segundos reinicia la medición"
        ),
        "LFO speed conversion is approximate": "La conversión a velocidad LFO es aproximada",
        "Off preserves the preset values. Synchronization is applied when the tempo changes.": (
            "Off conserva los valores del preset. La sincronización se aplica al cambiar el tempo."
        ),
        "Tempo outside the 20–300 BPM range; tap again": (
            "Tempo fuera del rango 20–300 BPM; vuelve a marcar"
        ),
        "LFO: {hz:.2f} Hz is outside the 0.05–10 Hz range": (
            "LFO: {hz:.2f} Hz fuera del rango 0.05–10 Hz"
        ),
        "Click the panel to change amplifier": "Clic en la placa para cambiar amplificador",
        "Amplifier": "Amplificador",
        "Connecting...": "Conectando...",
        "Save": "Guardar",
        "Reload": "Recargar",
        "MY TONES": "MIS TONOS",
        "Search...": "Buscar...",
        "— empty —": "— vacío —",
        "Disconnected: {error}": "Desconectado: {error}",
        "File": "Archivo",
        "Import preset...": "Importar preset...",
        "Export preset...": "Exportar preset...",
        "Select amplifier": "Selección de amplificador",
        "unassigned": "sin asignación",
        "Tempo: connect the pedal and load a preset": "Tempo: conecta el pedal y carga un preset",
        "Delay has no compatible TIME parameter": "Delay sin parámetro TIME compatible",
        "Delay: {value} ms is outside the {low}–{high} ms range": (
            "Delay: {value} ms fuera del rango {low}–{high} ms"
        ),
        "Unknown delay range": "Rango de delay desconocido",
        "LFO is not assigned": "LFO sin asignar",
        "The device presets will be overwritten. Continue?": (
            "Los presets del dispositivo serán sobrescritos. ¿Continuar?"
        ),
        "Imported: {name}": "Importado: {name}",
        "Restored {count} presets": "Restaurados {count} presets",
        "Preset name:": "Nombre del preset:",
        "Saved to User {slot}": "Guardado en User {slot}",
        "Select a User slot": "Selecciona un slot de User",
        "Quick stored to User {slot}": "Quick store en User {slot}",
        "Replace {label} with “Preset {slot}” using the default amplifier and cabinet, "
        "with no other effects? The slot will not be empty. The preset loaded in the "
        "editor will not change. This cannot be undone.": (
            "Reemplazar {label} por «Preset {slot}» con el amplificador y gabinete "
            "predeterminados, sin otros efectos? La posición no quedará vacía. "
            "El preset cargado en el editor no cambiará. Esta operación no se puede deshacer."
        ),
        "Error deleting preset: {error}": "Error al eliminar: {error}",
        "the device did not return the expected default preset": (
            "el dispositivo no devolvió el preset predeterminado"
        ),
        "Preset User {slot}: write sent; verification error: {error}": (
            "Preset User {slot}: escritura enviada; error al verificar: {error}"
        ),
        "Preset User {slot} reset; update error: {error}": (
            "Preset User {slot} restablecido; error al actualizar: {error}"
        ),
        "Preset User {slot} reset": "Preset User {slot} restablecido",
        "Error copying preset: {error}": "Error al copiar: {error}",
        "Preset copied to the internal clipboard": "Preset copiado al portapapeles interno",
        "Error reordering: {error}": "Error al reordenar: {error}",
        "No preset loaded": "No hay preset cargado",
        "Chain is full: all categories are in use": (
            "Cadena completa: todas las categorías están en uso"
        ),
        "No free slot in the chain": "No hay posición libre en la cadena",
    },
    "fr": {
        "Assign to a pedal": "Assigner à une pédale",
        "— None —": "— Aucun —",
        "Clear assignment": "Effacer l’assignation",
        "Expression pedal": "Pédale d’expression",
        "Assign to slot": "Assigner à un emplacement",
        "Parameter": "Paramètre",
        "Assign": "Assigner",
        "Amplifiers": "Amplis",
        "Distortion": "Distorsion",
        "Compressor": "Compresseur",
        "Modulation": "Modulation",
        "Volume": "Volume",
        "Select effect": "Sélectionner un effet",
        "Cancel": "Annuler",
        "Change effect...": "Changer d’effet...",
        "Delete": "Supprimer",
        "Session tempo; not read from the pedal": "Tempo de cette session ; non lu depuis le pédalier",
        "Tap in time; a 3-second pause resets the measurement": (
            "Tapez en rythme ; une pause de 3 secondes réinitialise la mesure"
        ),
        "LFO speed conversion is approximate": "La conversion de vitesse LFO est approximative",
        "Off preserves the preset values. Synchronization is applied when the tempo changes.": (
            "Off conserve les valeurs du preset. La synchronisation s’applique au changement de tempo."
        ),
        "Tempo outside the 20–300 BPM range; tap again": (
            "Tempo hors de la plage 20–300 BPM ; tapez à nouveau"
        ),
        "LFO: {hz:.2f} Hz is outside the 0.05–10 Hz range": (
            "LFO : {hz:.2f} Hz est hors de la plage 0,05–10 Hz"
        ),
        "Click the panel to change amplifier": "Cliquez sur le panneau pour changer d’ampli",
        "Amplifier": "Amplificateur",
        "Connecting...": "Connexion...",
        "Save": "Enregistrer",
        "Reload": "Recharger",
        "MY TONES": "MES SONS",
        "Search...": "Rechercher...",
        "— empty —": "— vide —",
        "Disconnected: {error}": "Déconnecté : {error}",
        "File": "Fichier",
        "Import preset...": "Importer un preset...",
        "Export preset...": "Exporter le preset...",
        "Select amplifier": "Sélectionner l’amplificateur",
        "unassigned": "non assigné",
        "Tempo: connect the pedal and load a preset": "Tempo : connectez le pédalier et chargez un preset",
        "Delay has no compatible TIME parameter": "Le delay n’a pas de paramètre TIME compatible",
        "Delay: {value} ms is outside the {low}–{high} ms range": (
            "Delay : {value} ms est hors de la plage {low}–{high} ms"
        ),
        "Unknown delay range": "Plage de delay inconnue",
        "LFO is not assigned": "LFO non assigné",
        "The device presets will be overwritten. Continue?": (
            "Les presets de l’appareil seront écrasés. Continuer ?"
        ),
        "Imported: {name}": "Importé : {name}",
        "Restored {count} presets": "{count} presets restaurés",
        "Preset name:": "Nom du preset :",
        "Saved to User {slot}": "Enregistré dans User {slot}",
        "Select a User slot": "Sélectionnez un emplacement User",
        "Quick stored to User {slot}": "Enregistrement rapide dans User {slot}",
        "Replace {label} with “Preset {slot}” using the default amplifier and cabinet, "
        "with no other effects? The slot will not be empty. The preset loaded in the "
        "editor will not change. This cannot be undone.": (
            "Remplacer {label} par « Preset {slot} » avec l’ampli et le baffle par défaut, "
            "sans autre effet ? L’emplacement ne sera pas vide. Le preset chargé dans "
            "l’éditeur ne changera pas. Cette action est irréversible."
        ),
        "Error deleting preset: {error}": "Erreur lors de la suppression du preset : {error}",
        "the device did not return the expected default preset": (
            "l’appareil n’a pas renvoyé le preset par défaut attendu"
        ),
        "Preset User {slot}: write sent; verification error: {error}": (
            "Preset User {slot} : écriture envoyée ; erreur de vérification : {error}"
        ),
        "Preset User {slot} reset; update error: {error}": (
            "Preset User {slot} réinitialisé ; erreur de mise à jour : {error}"
        ),
        "Preset User {slot} reset": "Preset User {slot} réinitialisé",
        "Error copying preset: {error}": "Erreur lors de la copie du preset : {error}",
        "Preset copied to the internal clipboard": "Preset copié dans le presse-papiers interne",
        "Error reordering: {error}": "Erreur lors du réordonnancement : {error}",
        "No preset loaded": "Aucun preset chargé",
        "Chain is full: all categories are in use": (
            "Chaîne complète : toutes les catégories sont utilisées"
        ),
        "No free slot in the chain": "Aucun emplacement libre dans la chaîne",
    },
    "de": {
        "Assign to a pedal": "Einem Pedal zuweisen",
        "— None —": "— Keine —",
        "Clear assignment": "Zuweisung löschen",
        "Expression pedal": "Expression-Pedal",
        "Assign to slot": "Slot zuweisen",
        "Parameter": "Parameter",
        "Assign": "Zuweisen",
        "Amplifiers": "Verstärker",
        "Distortion": "Verzerrung",
        "Compressor": "Kompressor",
        "Modulation": "Modulation",
        "Volume": "Lautstärke",
        "Select effect": "Effekt auswählen",
        "Cancel": "Abbrechen",
        "Change effect...": "Effekt ändern...",
        "Delete": "Löschen",
        "Session tempo; not read from the pedal": "Session-Tempo; wird nicht vom Pedal gelesen",
        "Tap in time; a 3-second pause resets the measurement": (
            "Im Takt tippen; nach 3 Sekunden Pause wird die Messung zurückgesetzt"
        ),
        "LFO speed conversion is approximate": "Die Umrechnung der LFO-Geschwindigkeit ist ungefähr",
        "Off preserves the preset values. Synchronization is applied when the tempo changes.": (
            "Off behält die Preset-Werte bei. Die Synchronisierung erfolgt bei Tempoänderungen."
        ),
        "Tempo outside the 20–300 BPM range; tap again": (
            "Tempo außerhalb des Bereichs 20–300 BPM; erneut tippen"
        ),
        "LFO: {hz:.2f} Hz is outside the 0.05–10 Hz range": (
            "LFO: {hz:.2f} Hz liegt außerhalb des Bereichs 0,05–10 Hz"
        ),
        "Click the panel to change amplifier": "Auf das Feld klicken, um den Verstärker zu ändern",
        "Amplifier": "Verstärker",
        "Connecting...": "Verbindung wird hergestellt...",
        "Save": "Speichern",
        "Reload": "Neu laden",
        "MY TONES": "MEINE KLÄNGE",
        "Search...": "Suchen...",
        "— empty —": "— leer —",
        "Disconnected: {error}": "Verbindung getrennt: {error}",
        "File": "Datei",
        "Import preset...": "Preset importieren...",
        "Export preset...": "Preset exportieren...",
        "Select amplifier": "Verstärker auswählen",
        "unassigned": "nicht zugewiesen",
        "Tempo: connect the pedal and load a preset": "Tempo: Pedal verbinden und ein Preset laden",
        "Delay has no compatible TIME parameter": "Delay hat keinen kompatiblen TIME-Parameter",
        "Delay: {value} ms is outside the {low}–{high} ms range": (
            "Delay: {value} ms liegt außerhalb des Bereichs {low}–{high} ms"
        ),
        "Unknown delay range": "Unbekannter Delay-Bereich",
        "LFO is not assigned": "LFO ist nicht zugewiesen",
        "The device presets will be overwritten. Continue?": (
            "Die Presets auf dem Gerät werden überschrieben. Fortfahren?"
        ),
        "Imported: {name}": "Importiert: {name}",
        "Restored {count} presets": "{count} Presets wiederhergestellt",
        "Preset name:": "Preset-Name:",
        "Saved to User {slot}": "In User {slot} gespeichert",
        "Select a User slot": "Einen User-Slot auswählen",
        "Quick stored to User {slot}": "Schnellspeicherung in User {slot}",
        "Replace {label} with “Preset {slot}” using the default amplifier and cabinet, "
        "with no other effects? The slot will not be empty. The preset loaded in the "
        "editor will not change. This cannot be undone.": (
            "{label} durch „Preset {slot}“ mit Standard-Verstärker und -Cabinet ersetzen, "
            "ohne weitere Effekte? Der Slot bleibt nicht leer. Das im Editor geladene "
            "Preset bleibt unverändert. Dieser Vorgang kann nicht rückgängig gemacht werden."
        ),
        "Error deleting preset: {error}": "Fehler beim Löschen des Presets: {error}",
        "the device did not return the expected default preset": (
            "das Gerät hat nicht das erwartete Standard-Preset zurückgegeben"
        ),
        "Preset User {slot}: write sent; verification error: {error}": (
            "Preset User {slot}: Schreibvorgang gesendet; Überprüfungsfehler: {error}"
        ),
        "Preset User {slot} reset; update error: {error}": (
            "Preset User {slot} zurückgesetzt; Aktualisierungsfehler: {error}"
        ),
        "Preset User {slot} reset": "Preset User {slot} zurückgesetzt",
        "Error copying preset: {error}": "Fehler beim Kopieren des Presets: {error}",
        "Preset copied to the internal clipboard": "Preset in die interne Zwischenablage kopiert",
        "Error reordering: {error}": "Fehler beim Neuordnen: {error}",
        "No preset loaded": "Kein Preset geladen",
        "Chain is full: all categories are in use": (
            "Effektkette voll: Alle Kategorien sind belegt"
        ),
        "No free slot in the chain": "Kein freier Slot in der Effektkette",
    },
    "it": {
        "Assign to a pedal": "Assegna a un pedale",
        "— None —": "— Nessuno —",
        "Clear assignment": "Rimuovi assegnazione",
        "Expression pedal": "Pedale di espressione",
        "Assign to slot": "Assegna allo slot",
        "Parameter": "Parametro",
        "Assign": "Assegna",
        "Amplifiers": "Amplificatori",
        "Distortion": "Distorsione",
        "Compressor": "Compressore",
        "Modulation": "Modulazione",
        "Volume": "Volume",
        "Select effect": "Seleziona effetto",
        "Cancel": "Annulla",
        "Change effect...": "Cambia effetto...",
        "Delete": "Elimina",
        "Session tempo; not read from the pedal": "Tempo della sessione; non viene letto dal pedale",
        "Tap in time; a 3-second pause resets the measurement": (
            "Tocca a tempo; una pausa di 3 secondi azzera la misurazione"
        ),
        "LFO speed conversion is approximate": "La conversione della velocità LFO è approssimativa",
        "Off preserves the preset values. Synchronization is applied when the tempo changes.": (
            "Off mantiene i valori del preset. La sincronizzazione avviene quando cambia il tempo."
        ),
        "Tempo outside the 20–300 BPM range; tap again": (
            "Tempo fuori dall’intervallo 20–300 BPM; tocca di nuovo"
        ),
        "LFO: {hz:.2f} Hz is outside the 0.05–10 Hz range": (
            "LFO: {hz:.2f} Hz è fuori dall’intervallo 0,05–10 Hz"
        ),
        "Click the panel to change amplifier": "Fai clic sul pannello per cambiare amplificatore",
        "Amplifier": "Amplificatore",
        "Connecting...": "Connessione in corso...",
        "Save": "Salva",
        "Reload": "Ricarica",
        "MY TONES": "I MIEI SUONI",
        "Search...": "Cerca...",
        "— empty —": "— vuoto —",
        "Disconnected: {error}": "Disconnesso: {error}",
        "File": "File",
        "Import preset...": "Importa preset...",
        "Export preset...": "Esporta preset...",
        "Select amplifier": "Seleziona amplificatore",
        "unassigned": "non assegnato",
        "Tempo: connect the pedal and load a preset": "Tempo: collega il pedale e carica un preset",
        "Delay has no compatible TIME parameter": "Il delay non ha un parametro TIME compatibile",
        "Delay: {value} ms is outside the {low}–{high} ms range": (
            "Delay: {value} ms fuori dall’intervallo {low}–{high} ms"
        ),
        "Unknown delay range": "Intervallo del delay sconosciuto",
        "LFO is not assigned": "LFO non assegnato",
        "The device presets will be overwritten. Continue?": (
            "I preset del dispositivo verranno sovrascritti. Continuare?"
        ),
        "Imported: {name}": "Importato: {name}",
        "Restored {count} presets": "Ripristinati {count} preset",
        "Preset name:": "Nome del preset:",
        "Saved to User {slot}": "Salvato in User {slot}",
        "Select a User slot": "Seleziona uno slot User",
        "Quick stored to User {slot}": "Salvataggio rapido in User {slot}",
        "Replace {label} with “Preset {slot}” using the default amplifier and cabinet, "
        "with no other effects? The slot will not be empty. The preset loaded in the "
        "editor will not change. This cannot be undone.": (
            "Sostituire {label} con “Preset {slot}” usando amplificatore e cabinet "
            "predefiniti, senza altri effetti? Lo slot non sarà vuoto. Il preset caricato "
            "nell’editor non cambierà. L’operazione non può essere annullata."
        ),
        "Error deleting preset: {error}": "Errore durante l’eliminazione del preset: {error}",
        "the device did not return the expected default preset": (
            "il dispositivo non ha restituito il preset predefinito previsto"
        ),
        "Preset User {slot}: write sent; verification error: {error}": (
            "Preset User {slot}: scrittura inviata; errore di verifica: {error}"
        ),
        "Preset User {slot} reset; update error: {error}": (
            "Preset User {slot} ripristinato; errore di aggiornamento: {error}"
        ),
        "Preset User {slot} reset": "Preset User {slot} ripristinato",
        "Error copying preset: {error}": "Errore durante la copia del preset: {error}",
        "Preset copied to the internal clipboard": "Preset copiato negli appunti interni",
        "Error reordering: {error}": "Errore durante il riordino: {error}",
        "No preset loaded": "Nessun preset caricato",
        "Chain is full: all categories are in use": (
            "Catena completa: tutte le categorie sono in uso"
        ),
        "No free slot in the chain": "Nessuno slot libero nella catena",
    },
    "ja": {
        "Assign to a pedal": "ペダルに割り当て",
        "— None —": "— なし —",
        "Clear assignment": "割り当てを解除",
        "Expression pedal": "エクスプレッションペダル",
        "Assign to slot": "スロットに割り当て",
        "Parameter": "パラメーター",
        "Assign": "割り当て",
        "Amplifiers": "アンプ",
        "Distortion": "ディストーション",
        "Compressor": "コンプレッサー",
        "Modulation": "モジュレーション",
        "Volume": "ボリューム",
        "Select effect": "エフェクトを選択",
        "Cancel": "キャンセル",
        "Change effect...": "エフェクトを変更...",
        "Delete": "削除",
        "Session tempo; not read from the pedal": "セッションのテンポ（ペダルからは読み取りません）",
        "Tap in time; a 3-second pause resets the measurement": (
            "リズムに合わせてタップしてください。3秒間タップしないと計測をリセットします"
        ),
        "LFO speed conversion is approximate": "LFO速度の変換は概算です",
        "Off preserves the preset values. Synchronization is applied when the tempo changes.": (
            "Offではプリセットの値を保持します。テンポを変更すると同期されます。"
        ),
        "Tempo outside the 20–300 BPM range; tap again": (
            "テンポが20～300 BPMの範囲外です。もう一度タップしてください"
        ),
        "LFO: {hz:.2f} Hz is outside the 0.05–10 Hz range": (
            "LFO: {hz:.2f} Hz は 0.05～10 Hz の範囲外です"
        ),
        "Click the panel to change amplifier": "パネルをクリックしてアンプを変更",
        "Amplifier": "アンプ",
        "Connecting...": "接続中...",
        "Save": "保存",
        "Reload": "再読み込み",
        "MY TONES": "マイ・トーン",
        "Search...": "検索...",
        "— empty —": "— 空 —",
        "Disconnected: {error}": "切断されました: {error}",
        "File": "ファイル",
        "Import preset...": "プリセットをインポート...",
        "Export preset...": "プリセットをエクスポート...",
        "Select amplifier": "アンプを選択",
        "unassigned": "未割り当て",
        "Tempo: connect the pedal and load a preset": "テンポ: ペダルを接続してプリセットを読み込んでください",
        "Delay has no compatible TIME parameter": "対応するTIMEパラメーターがDelayにありません",
        "Delay: {value} ms is outside the {low}–{high} ms range": (
            "Delay: {value} ms は {low}～{high} ms の範囲外です"
        ),
        "Unknown delay range": "Delayの範囲が不明です",
        "LFO is not assigned": "LFOは割り当てられていません",
        "The device presets will be overwritten. Continue?": (
            "デバイス上のプリセットは上書きされます。続行しますか？"
        ),
        "Imported: {name}": "インポートしました: {name}",
        "Restored {count} presets": "{count}個のプリセットを復元しました",
        "Preset name:": "プリセット名:",
        "Saved to User {slot}": "User {slot}に保存しました",
        "Select a User slot": "Userスロットを選択してください",
        "Quick stored to User {slot}": "User {slot}にクイック保存しました",
        "Replace {label} with “Preset {slot}” using the default amplifier and cabinet, "
        "with no other effects? The slot will not be empty. The preset loaded in the "
        "editor will not change. This cannot be undone.": (
            "{label}を既定のアンプとキャビネットを使った「Preset {slot}」に置き換えます。"
            "他のエフェクトは含まれません。スロットは空になりません。エディターで読み込んでいる"
            "プリセットは変更されません。この操作は元に戻せません。"
        ),
        "Error deleting preset: {error}": "プリセットの削除エラー: {error}",
        "the device did not return the expected default preset": (
            "デバイスから期待した既定のプリセットが返されませんでした"
        ),
        "Preset User {slot}: write sent; verification error: {error}": (
            "Preset User {slot}: 書き込みを送信しました。確認エラー: {error}"
        ),
        "Preset User {slot} reset; update error: {error}": (
            "Preset User {slot}をリセットしました。更新エラー: {error}"
        ),
        "Preset User {slot} reset": "Preset User {slot}をリセットしました",
        "Error copying preset: {error}": "プリセットのコピーエラー: {error}",
        "Preset copied to the internal clipboard": "プリセットを内部クリップボードにコピーしました",
        "Error reordering: {error}": "並べ替えエラー: {error}",
        "No preset loaded": "プリセットが読み込まれていません",
        "Chain is full: all categories are in use": (
            "エフェクトチェーンがいっぱいです。すべてのカテゴリが使用中です"
        ),
        "No free slot in the chain": "エフェクトチェーンに空きスロットがありません",
    },
}

_UI_CATALOGS = {
    "es": {
        "+ Pedal": "+ Pedal",
        "Copy": "Copiar",
        "Delay: {value} ms": "Delay: {value} ms",
        "LFO: ~{hz:.2f} Hz": "LFO: ~{hz:.2f} Hz",
        "Slot {slot}": "Slot {slot}",
        "EQ effect only. Frequency mappings are interpolated and filter shapes are "
        "illustrative; this is not a measured response. The vertical scale adjusts to the curve.": (
            "Solo el efecto EQ. Las frecuencias se interpolan y las formas de los filtros "
            "son ilustrativas; no es una respuesta medida. La escala vertical se ajusta a la curva."
        ),
        "Level": "Nivel",
        "User": "Usuario",
        "Factory": "Fábrica",
        "Library": "Biblioteca",
        "Footswitch": "Interruptor de pie",
        "Stompbox": "Pedal",
        "Expression": "Expresión",
        "Expression Link": "Asignación de expresión",
        "LFO": "LFO",
        "LFO Link": "Asignación de LFO",
        "Tempo": "Tempo",
        "Wah": "Wah",
        "Mod": "Modulación",
        "Reverb": "Reverb",
        "Gate": "Gate",
        "EQ": "EQ",
        "Other": "Otros",
        "Wah Settings": "Ajustes de wah",
        "Min": "Mín.",
        "Max": "Máx.",
        "Speed": "Velocidad",
        "Wave": "Forma de onda",
        "Tap": "Marcar",
        "Delay": "Delay",
        "Off": "Off",
        "Half": "Mitad",
        "Quarter": "Negra",
        "Dotted eighth": "Corchea con puntillo",
        "Eighth": "Corchea",
        "Eighth triplet": "Tresillo de corcheas",
        "Sixteenth": "Semicorchea",
        "Wide": "Ancho",
        "Medium": "Medio",
        "Narrow": "Estrecho",
        "WIDE": "ANCHO",
        "MEDIUM": "MEDIO",
        "NARROW": "ESTRECHO",
        "Wide, Medium or Narrow": "Ancho, medio o estrecho",
        "Unknown": "Desconocido",
        "parameter unavailable": "parámetro no disponible",
        "Cabinet": "Gabinete",
        "AMP": "AMPLI",
        "ON": "ENCENDIDO",
        "Bypass": "Bypass",
        "EQ ESTIMATE": "ESTIMACIÓN EQ",
        "NO EQ": "SIN EQ",
        "EQ BYPASSED": "EQ EN BYPASS",
        "EQ UNAVAILABLE": "EQ NO DISPONIBLE",
        "LOW": "GRAVES",
        "MID": "MEDIOS",
        "HIGH": "AGUDOS",
        "Backup...": "Copia de seguridad...",
        "Restore...": "Restaurar...",
        "Preset": "Preset",
        "Store New...": "Guardar nuevo...",
        "Quick Store": "Guardado rápido",
        "Delete User Preset...": "Eliminar preset de usuario...",
        "Delete...": "Eliminar...",
        "Backup 99 presets": "Respaldar 99 presets",
        "Restaurar 99 presets": "Restaurar 99 presets",
        "Restore": "Restaurar",
        "Store New": "Guardar nuevo",
        "Slot (1-99):": "Slot (1-99):",
        "Delete User Preset": "Eliminar preset de usuario",
        "DigiTux — RP360/XP Editor": "DigiTux — Editor RP360/XP",
        "Offline: {error}": "Sin conexión: {error}",
        "Error: {error}": "Error: {error}",
        "Error reload: {error}": "Error al recargar: {error}",
        "Preset: {name}": "Preset: {name}",
        "Error sync: {error}": "Error de sincronización: {error}",
        "Error stomp: {error}": "Error del footswitch: {error}",
        "Error expr: {error}": "Error de expresión: {error}",
        "Error lfo: {error}": "Error de LFO: {error}",
        "Error LFO: {error}": "Error de LFO: {error}",
        "Error backup: {error}": "Error al respaldar: {error}",
        "Error restore: {error}": "Error al restaurar: {error}",
        "Error import: {error}": "Error al importar: {error}",
        "Error export: {error}": "Error al exportar: {error}",
        "Error level: {error}": "Error de nivel: {error}",
        "Error cabinet: {error}": "Error de gabinete: {error}",
        "Backup → {path}": "Respaldo → {path}",
        "Exported → {path}": "Exportado → {path}",
        "{ctrl} unassigned": "{ctrl} sin asignación",
        "{ctrl} → slot {slot}": "{ctrl} → slot {slot}",
        "{ctrl} → slot {slot} {param}": "{ctrl} → slot {slot} {param}",
        "LFO → slot {slot} {param}": "LFO → slot {slot} {param}",
        "User {slot}": "Usuario {slot}",
        'User {slot} ("{name}")': 'Usuario {slot} ("{name}")',
    },
    "fr": {
        "+ Pedal": "+ Pédale",
        "Copy": "Copier",
        "Delay: {value} ms": "Delay : {value} ms",
        "LFO: ~{hz:.2f} Hz": "LFO : ~{hz:.2f} Hz",
        "Slot {slot}": "Emplacement {slot}",
        "EQ effect only. Frequency mappings are interpolated and filter shapes are "
        "illustrative; this is not a measured response. The vertical scale adjusts to the curve.": (
            "Effet EQ uniquement. Les fréquences sont interpolées et les formes des filtres "
            "sont illustratives ; il ne s’agit pas d’une réponse mesurée. L’échelle verticale "
            "s’ajuste à la courbe."
        ),
        "Level": "Niveau",
        "User": "Utilisateur",
        "Factory": "Usine",
        "Library": "Bibliothèque",
        "Footswitch": "Pédale",
        "Stompbox": "Pédale",
        "Expression": "Expression",
        "Expression Link": "Liaison d’expression",
        "LFO": "LFO",
        "LFO Link": "Liaison LFO",
        "Tempo": "Tempo",
        "Wah": "Wah",
        "Mod": "Modulation",
        "Reverb": "Réverbération",
        "Gate": "Gate",
        "EQ": "EQ",
        "Other": "Autre",
        "Wah Settings": "Réglages du wah",
        "Min": "Min",
        "Max": "Max",
        "Speed": "Vitesse",
        "Wave": "Forme d’onde",
        "Tap": "Tempo",
        "Delay": "Delay",
        "Off": "Désactivé",
        "Half": "Blanche",
        "Quarter": "Noire",
        "Dotted eighth": "Croche pointée",
        "Eighth": "Croche",
        "Eighth triplet": "Triolet de croches",
        "Sixteenth": "Double croche",
        "Wide": "Large",
        "Medium": "Moyen",
        "Narrow": "Étroit",
        "WIDE": "LARGE",
        "MEDIUM": "MOYEN",
        "NARROW": "ÉTROIT",
        "Wide, Medium or Narrow": "Large, moyen ou étroit",
        "Unknown": "Inconnu",
        "parameter unavailable": "paramètre indisponible",
        "Cabinet": "Baffle",
        "AMP": "AMPLI",
        "ON": "ACTIVÉ",
        "Bypass": "Bypass",
        "EQ ESTIMATE": "ESTIMATION EQ",
        "NO EQ": "SANS EQ",
        "EQ BYPASSED": "EQ CONTOURNÉ",
        "EQ UNAVAILABLE": "EQ INDISPONIBLE",
        "LOW": "GRAVE",
        "MID": "MÉDIUM",
        "HIGH": "AIGU",
        "Backup...": "Sauvegarder...",
        "Restore...": "Restaurer...",
        "Preset": "Preset",
        "Store New...": "Enregistrer sous...",
        "Quick Store": "Enregistrement rapide",
        "Delete User Preset...": "Supprimer le preset utilisateur...",
        "Delete...": "Supprimer...",
        "Backup 99 presets": "Sauvegarder les 99 presets",
        "Restaurar 99 presets": "Restaurer les 99 presets",
        "Restore": "Restaurer",
        "Store New": "Nouvel enregistrement",
        "Slot (1-99):": "Emplacement (1–99) :",
        "Delete User Preset": "Supprimer le preset utilisateur",
        "DigiTux — RP360/XP Editor": "DigiTux — Éditeur RP360/XP",
        "Offline: {error}": "Hors ligne : {error}",
        "Error: {error}": "Erreur : {error}",
        "Error reload: {error}": "Erreur de rechargement : {error}",
        "Preset: {name}": "Preset : {name}",
        "Error sync: {error}": "Erreur de synchronisation : {error}",
        "Error stomp: {error}": "Erreur de pédale : {error}",
        "Error expr: {error}": "Erreur d’expression : {error}",
        "Error lfo: {error}": "Erreur LFO : {error}",
        "Error LFO: {error}": "Erreur LFO : {error}",
        "Error backup: {error}": "Erreur de sauvegarde : {error}",
        "Error restore: {error}": "Erreur de restauration : {error}",
        "Error import: {error}": "Erreur d’importation : {error}",
        "Error export: {error}": "Erreur d’exportation : {error}",
        "Error level: {error}": "Erreur de niveau : {error}",
        "Error cabinet: {error}": "Erreur de baffle : {error}",
        "Backup → {path}": "Sauvegarde → {path}",
        "Exported → {path}": "Exporté → {path}",
        "{ctrl} unassigned": "{ctrl} non assigné",
        "{ctrl} → slot {slot}": "{ctrl} → emplacement {slot}",
        "{ctrl} → slot {slot} {param}": "{ctrl} → emplacement {slot} {param}",
        "LFO → slot {slot} {param}": "LFO → emplacement {slot} {param}",
        "User {slot}": "Utilisateur {slot}",
        'User {slot} ("{name}")': 'Utilisateur {slot} ("{name}")',
    },
    "de": {
        "+ Pedal": "+ Pedal",
        "Copy": "Kopieren",
        "Delay: {value} ms": "Delay: {value} ms",
        "LFO: ~{hz:.2f} Hz": "LFO: ~{hz:.2f} Hz",
        "Slot {slot}": "Slot {slot}",
        "EQ effect only. Frequency mappings are interpolated and filter shapes are "
        "illustrative; this is not a measured response. The vertical scale adjusts to the curve.": (
            "Nur der EQ-Effekt. Frequenzen werden interpoliert und Filterformen sind "
            "anschaulich dargestellt; dies ist keine gemessene Antwort. Die vertikale "
            "Skala passt sich der Kurve an."
        ),
        "Level": "Pegel",
        "User": "Benutzer",
        "Factory": "Werk",
        "Library": "Bibliothek",
        "Footswitch": "Fußschalter",
        "Stompbox": "Fußschalter",
        "Expression": "Expression",
        "Expression Link": "Expression-Zuweisung",
        "LFO": "LFO",
        "LFO Link": "LFO-Zuweisung",
        "Tempo": "Tempo",
        "Wah": "Wah",
        "Mod": "Modulation",
        "Reverb": "Hall",
        "Gate": "Gate",
        "EQ": "EQ",
        "Other": "Sonstiges",
        "Wah Settings": "Wah-Einstellungen",
        "Min": "Min",
        "Max": "Max",
        "Speed": "Geschwindigkeit",
        "Wave": "Wellenform",
        "Tap": "Tippen",
        "Delay": "Delay",
        "Off": "Aus",
        "Half": "Halbe",
        "Quarter": "Viertel",
        "Dotted eighth": "Punktierte Achtel",
        "Eighth": "Achtel",
        "Eighth triplet": "Achteltriole",
        "Sixteenth": "Sechzehntel",
        "Wide": "Breit",
        "Medium": "Mittel",
        "Narrow": "Schmal",
        "WIDE": "BREIT",
        "MEDIUM": "MITTEL",
        "NARROW": "SCHMAL",
        "Wide, Medium or Narrow": "Breit, mittel oder schmal",
        "Unknown": "Unbekannt",
        "parameter unavailable": "Parameter nicht verfügbar",
        "Cabinet": "Cabinet",
        "AMP": "AMP",
        "ON": "EIN",
        "Bypass": "Bypass",
        "EQ ESTIMATE": "EQ-SCHÄTZUNG",
        "NO EQ": "KEIN EQ",
        "EQ BYPASSED": "EQ ÜBERBRÜCKT",
        "EQ UNAVAILABLE": "EQ NICHT VERFÜGBAR",
        "LOW": "TIEFEN",
        "MID": "MITTEN",
        "HIGH": "HÖHEN",
        "Backup...": "Sichern...",
        "Restore...": "Wiederherstellen...",
        "Preset": "Preset",
        "Store New...": "Neu speichern...",
        "Quick Store": "Schnellspeichern",
        "Delete User Preset...": "Benutzer-Preset löschen...",
        "Delete...": "Löschen...",
        "Backup 99 presets": "99 Presets sichern",
        "Restaurar 99 presets": "99 Presets wiederherstellen",
        "Restore": "Wiederherstellen",
        "Store New": "Neu speichern",
        "Slot (1-99):": "Slot (1–99):",
        "Delete User Preset": "Benutzer-Preset löschen",
        "DigiTux — RP360/XP Editor": "DigiTux — RP360/XP-Editor",
        "Offline: {error}": "Offline: {error}",
        "Error: {error}": "Fehler: {error}",
        "Error reload: {error}": "Fehler beim Neuladen: {error}",
        "Preset: {name}": "Preset: {name}",
        "Error sync: {error}": "Synchronisierungsfehler: {error}",
        "Error stomp: {error}": "Fußschalterfehler: {error}",
        "Error expr: {error}": "Expression-Fehler: {error}",
        "Error lfo: {error}": "LFO-Fehler: {error}",
        "Error LFO: {error}": "LFO-Fehler: {error}",
        "Error backup: {error}": "Fehler beim Sichern: {error}",
        "Error restore: {error}": "Fehler beim Wiederherstellen: {error}",
        "Error import: {error}": "Fehler beim Importieren: {error}",
        "Error export: {error}": "Fehler beim Exportieren: {error}",
        "Error level: {error}": "Pegel-Fehler: {error}",
        "Error cabinet: {error}": "Cabinet-Fehler: {error}",
        "Backup → {path}": "Sicherung → {path}",
        "Exported → {path}": "Exportiert → {path}",
        "{ctrl} unassigned": "{ctrl} nicht zugewiesen",
        "{ctrl} → slot {slot}": "{ctrl} → Slot {slot}",
        "{ctrl} → slot {slot} {param}": "{ctrl} → Slot {slot} {param}",
        "LFO → slot {slot} {param}": "LFO → Slot {slot} {param}",
        "User {slot}": "Benutzer {slot}",
        'User {slot} ("{name}")': 'Benutzer {slot} ("{name}")',
    },
    "it": {
        "+ Pedal": "+ Pedale",
        "Copy": "Copia",
        "Delay: {value} ms": "Delay: {value} ms",
        "LFO: ~{hz:.2f} Hz": "LFO: ~{hz:.2f} Hz",
        "Slot {slot}": "Slot {slot}",
        "EQ effect only. Frequency mappings are interpolated and filter shapes are "
        "illustrative; this is not a measured response. The vertical scale adjusts to the curve.": (
            "Solo l’effetto EQ. Le frequenze sono interpolate e le forme dei filtri sono "
            "illustrative; non si tratta di una risposta misurata. La scala verticale si "
            "adatta alla curva."
        ),
        "Level": "Livello",
        "User": "Utente",
        "Factory": "Fabbrica",
        "Library": "Libreria",
        "Footswitch": "Interruttore a pedale",
        "Stompbox": "Pedale",
        "Expression": "Espressione",
        "Expression Link": "Assegnazione espressione",
        "LFO": "LFO",
        "LFO Link": "Assegnazione LFO",
        "Tempo": "Tempo",
        "Wah": "Wah",
        "Mod": "Modulazione",
        "Reverb": "Riverbero",
        "Gate": "Gate",
        "EQ": "EQ",
        "Other": "Altro",
        "Wah Settings": "Impostazioni wah",
        "Min": "Min",
        "Max": "Max",
        "Speed": "Velocità",
        "Wave": "Forma d’onda",
        "Tap": "Tocca",
        "Delay": "Delay",
        "Off": "Off",
        "Half": "Metà",
        "Quarter": "Quarto",
        "Dotted eighth": "Croma puntato",
        "Eighth": "Croma",
        "Eighth triplet": "Terzina di crome",
        "Sixteenth": "Semicroma",
        "Wide": "Largo",
        "Medium": "Medio",
        "Narrow": "Stretto",
        "WIDE": "LARGO",
        "MEDIUM": "MEDIO",
        "NARROW": "STRETTO",
        "Wide, Medium or Narrow": "Largo, medio o stretto",
        "Unknown": "Sconosciuto",
        "parameter unavailable": "parametro non disponibile",
        "Cabinet": "Cabinet",
        "AMP": "AMP",
        "ON": "ACCESO",
        "Bypass": "Bypass",
        "EQ ESTIMATE": "STIMA EQ",
        "NO EQ": "NESSUN EQ",
        "EQ BYPASSED": "EQ BYPASS",
        "EQ UNAVAILABLE": "EQ NON DISPONIBILE",
        "LOW": "BASSI",
        "MID": "MEDI",
        "HIGH": "ALTI",
        "Backup...": "Backup...",
        "Restore...": "Ripristina...",
        "Preset": "Preset",
        "Store New...": "Salva nuovo...",
        "Quick Store": "Salvataggio rapido",
        "Delete User Preset...": "Elimina preset utente...",
        "Delete...": "Elimina...",
        "Backup 99 presets": "Backup di 99 preset",
        "Restaurar 99 presets": "Ripristina 99 preset",
        "Restore": "Ripristina",
        "Store New": "Salva nuovo",
        "Slot (1-99):": "Slot (1–99):",
        "Delete User Preset": "Elimina preset utente",
        "DigiTux — RP360/XP Editor": "DigiTux — Editor RP360/XP",
        "Offline: {error}": "Non connesso: {error}",
        "Error: {error}": "Errore: {error}",
        "Error reload: {error}": "Errore durante il ricaricamento: {error}",
        "Preset: {name}": "Preset: {name}",
        "Error sync: {error}": "Errore di sincronizzazione: {error}",
        "Error stomp: {error}": "Errore del pedale: {error}",
        "Error expr: {error}": "Errore di espressione: {error}",
        "Error lfo: {error}": "Errore LFO: {error}",
        "Error LFO: {error}": "Errore LFO: {error}",
        "Error backup: {error}": "Errore durante il backup: {error}",
        "Error restore: {error}": "Errore durante il ripristino: {error}",
        "Error import: {error}": "Errore durante l’importazione: {error}",
        "Error export: {error}": "Errore durante l’esportazione: {error}",
        "Error level: {error}": "Errore di livello: {error}",
        "Error cabinet: {error}": "Errore cabinet: {error}",
        "Backup → {path}": "Backup → {path}",
        "Exported → {path}": "Esportato → {path}",
        "{ctrl} unassigned": "{ctrl} non assegnato",
        "{ctrl} → slot {slot}": "{ctrl} → slot {slot}",
        "{ctrl} → slot {slot} {param}": "{ctrl} → slot {slot} {param}",
        "LFO → slot {slot} {param}": "LFO → slot {slot} {param}",
        "User {slot}": "Utente {slot}",
        'User {slot} ("{name}")': 'Utente {slot} ("{name}")',
    },
    "ja": {
        "+ Pedal": "+ ペダル",
        "Copy": "コピー",
        "Delay: {value} ms": "ディレイ: {value} ms",
        "LFO: ~{hz:.2f} Hz": "LFO: 約{hz:.2f} Hz",
        "Slot {slot}": "スロット{slot}",
        "EQ effect only. Frequency mappings are interpolated and filter shapes are "
        "illustrative; this is not a measured response. The vertical scale adjusts to the curve.": (
            "EQエフェクトのみを表示します。周波数は補間値、フィルター形状は参考表示であり、"
            "測定結果ではありません。縦軸のスケールは曲線に合わせて調整されます。"
        ),
        "Level": "レベル",
        "User": "ユーザー",
        "Factory": "ファクトリー",
        "Library": "ライブラリ",
        "Footswitch": "フットスイッチ",
        "Stompbox": "ストンプボックス",
        "Expression": "エクスプレッション",
        "Expression Link": "エクスプレッション割り当て",
        "LFO": "LFO",
        "LFO Link": "LFO割り当て",
        "Tempo": "テンポ",
        "Wah": "ワウ",
        "Mod": "モジュレーション",
        "Reverb": "リバーブ",
        "Gate": "ゲート",
        "EQ": "EQ",
        "Other": "その他",
        "Wah Settings": "ワウ設定",
        "Min": "最小",
        "Max": "最大",
        "Speed": "速度",
        "Wave": "波形",
        "Tap": "タップ",
        "Delay": "ディレイ",
        "Off": "オフ",
        "Half": "2分音符",
        "Quarter": "4分音符",
        "Dotted eighth": "付点8分音符",
        "Eighth": "8分音符",
        "Eighth triplet": "8分3連符",
        "Sixteenth": "16分音符",
        "Wide": "広い",
        "Medium": "中",
        "Narrow": "狭い",
        "WIDE": "広い",
        "MEDIUM": "中",
        "NARROW": "狭い",
        "Wide, Medium or Narrow": "広い、中、狭い",
        "Unknown": "不明",
        "parameter unavailable": "パラメーターを利用できません",
        "Cabinet": "キャビネット",
        "AMP": "アンプ",
        "ON": "オン",
        "Bypass": "バイパス",
        "EQ ESTIMATE": "EQ推定",
        "NO EQ": "EQなし",
        "EQ BYPASSED": "EQバイパス中",
        "EQ UNAVAILABLE": "EQ利用不可",
        "LOW": "低音",
        "MID": "中音",
        "HIGH": "高音",
        "Backup...": "バックアップ...",
        "Restore...": "復元...",
        "Preset": "プリセット",
        "Store New...": "新規保存...",
        "Quick Store": "クイック保存",
        "Delete User Preset...": "ユーザープリセットを削除...",
        "Delete...": "削除...",
        "Backup 99 presets": "99個のプリセットをバックアップ",
        "Restaurar 99 presets": "99個のプリセットを復元",
        "Restore": "復元",
        "Store New": "新規保存",
        "Slot (1-99):": "スロット (1～99):",
        "Delete User Preset": "ユーザープリセットを削除",
        "DigiTux — RP360/XP Editor": "DigiTux — RP360/XP エディター",
        "Offline: {error}": "オフライン: {error}",
        "Error: {error}": "エラー: {error}",
        "Error reload: {error}": "再読み込みエラー: {error}",
        "Preset: {name}": "プリセット: {name}",
        "Error sync: {error}": "同期エラー: {error}",
        "Error stomp: {error}": "フットスイッチエラー: {error}",
        "Error expr: {error}": "エクスプレッションエラー: {error}",
        "Error lfo: {error}": "LFOエラー: {error}",
        "Error LFO: {error}": "LFOエラー: {error}",
        "Error backup: {error}": "バックアップエラー: {error}",
        "Error restore: {error}": "復元エラー: {error}",
        "Error import: {error}": "インポートエラー: {error}",
        "Error export: {error}": "エクスポートエラー: {error}",
        "Error level: {error}": "レベルエラー: {error}",
        "Error cabinet: {error}": "キャビネットエラー: {error}",
        "Backup → {path}": "バックアップ → {path}",
        "Exported → {path}": "エクスポートしました → {path}",
        "{ctrl} unassigned": "{ctrl}は未割り当てです",
        "{ctrl} → slot {slot}": "{ctrl} → スロット{slot}",
        "{ctrl} → slot {slot} {param}": "{ctrl} → スロット{slot} {param}",
        "LFO → slot {slot} {param}": "LFO → スロット{slot} {param}",
        "User {slot}": "ユーザー {slot}",
        'User {slot} ("{name}")': 'ユーザー {slot} ("{name}")',
    },
}


@lru_cache(maxsize=1)
def _system_language():
    return QLocale.system().name().split("_", 1)[0].lower()


def translate(text):
    """Translate a UI string using the language selected by the system locale."""
    language = _system_language()
    english_text = _ENGLISH.get(text, text)
    if language == "en":
        return english_text
    return (_CATALOGS.get(language, {}).get(english_text)
            or _UI_CATALOGS.get(language, {}).get(english_text, text))
