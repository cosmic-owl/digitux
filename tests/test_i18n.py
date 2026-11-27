import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import QLocale
from PyQt5.QtWidgets import QApplication, QLabel

from nexus.ui.control_panel import ControlPanel
from nexus.ui.i18n import _system_language, translate
from nexus.ui.tempo_panel import TempoPanel


class LocalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        _system_language.cache_clear()

    def tearDown(self):
        _system_language.cache_clear()

    def test_english_system_locale_translates_control_panel(self):
        with patch("nexus.ui.i18n.QLocale.system", return_value=QLocale(QLocale.English)):
            panel = ControlPanel(None)
        labels = [label.text() for label in panel.findChildren(QLabel)]
        self.assertIn("Assign to a pedal", labels)
        self.assertIn("Expression pedal", labels)
        self.assertEqual(translate("Asignar a pedal"), "Assign to a pedal")

    def test_spanish_locale_translates_and_unknown_text_falls_back(self):
        with patch("nexus.ui.i18n.QLocale.system", return_value=QLocale(QLocale.Spanish)):
            self.assertEqual(translate("Asignar a pedal"), "Asignar al pedal")
            self.assertEqual(translate("Unmapped text"), "Unmapped text")

    def test_supported_system_languages(self):
        examples = (
            (QLocale.Spanish, "Asignar al pedal", "Pedal EQ"),
            (QLocale.English, "Assign to a pedal", "EQ Pedal"),
            (QLocale.French, "Assigner à une pédale", "Pédale EQ"),
            (QLocale.German, "Einem Pedal zuweisen", "EQ-Pedal"),
            (QLocale.Italian, "Assegna a un pedale", "Pedale EQ"),
            (QLocale.Japanese, "ペダルに割り当て", "EQペダル"),
        )
        for language, expected, eq_title in examples:
            with self.subTest(language=language), patch(
                "nexus.ui.i18n.QLocale.system", return_value=QLocale(language)
            ):
                _system_language.cache_clear()
                self.assertEqual(translate("Asignar a pedal"), expected)
                controls = ControlPanel(None)
                labels = [label.text() for label in controls.findChildren(QLabel)]
                self.assertIn(expected, labels)
                self.assertEqual(controls.eq_heading.text(), eq_title)
                tempo = TempoPanel()
                self.assertEqual(tempo.tap.text(), translate("Tap"))
                self.assertEqual(tempo.delay.itemText(0), translate("Off"))
                controls.close()
                tempo.close()


if __name__ == "__main__":
    unittest.main()
