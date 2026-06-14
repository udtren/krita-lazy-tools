import os

from krita import Krita, InfoObject  # type: ignore

from ..compat import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from ..config.config_loader import get_export_settings, get_export_button_font_size


def _export_doc(doc, fmt: str, output_dir: str = None) -> bool:
    """Export *doc* to *fmt*. Uses the doc's own folder when *output_dir* is None."""
    if not doc:
        return False
    kra_path = doc.fileName()
    if not kra_path:
        print(f"[image_export] '{doc.name()}' not saved on disk — skipped.")
        return False

    if output_dir:
        basename = os.path.splitext(os.path.basename(kra_path))[0]
        export_path = os.path.join(output_dir, f"{basename}.{fmt}")
    else:
        export_path = os.path.splitext(kra_path)[0] + "." + fmt

    info = InfoObject()
    for key, value in get_export_settings(fmt).items():
        info.setProperty(key, value)

    doc.setBatchmode(True)
    success = doc.exportImage(export_path, info)
    doc.setBatchmode(False)

    if success:
        print(f"[image_export] OK  {export_path}")
    else:
        print(f"[image_export] FAIL {export_path}")
    return success


def _pick_folder(title: str) -> str:
    """Open a folder-picker dialog. Returns the chosen path or '' if cancelled."""
    dialog = QFileDialog()
    dialog.setWindowTitle(title)
    dialog.setFileMode(QFileDialog.Directory)
    dialog.setOption(QFileDialog.ShowDirsOnly, True)
    if dialog.exec_() == QFileDialog.Accepted:
        folders = dialog.selectedFiles()
        return folders[0] if folders else ""
    return ""


class ImageExportWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet(f"QPushButton {{ font-size: {get_export_button_font_size()}px; font-weight: bold; }}")

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        self.setLayout(layout)

        # --- same-folder exports ---
        label_same = QLabel("Export to same folder as .kra:")
        label_same.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(label_same)

        self._btn_png_active = QPushButton("PNG  — active doc")
        self._btn_png_all = QPushButton("PNG  — all docs")
        self._btn_jpg_active = QPushButton("JPEG — active doc")
        self._btn_jpg_all = QPushButton("JPEG — all docs")

        for btn in (
            self._btn_png_active,
            self._btn_png_all,
            self._btn_jpg_active,
            self._btn_jpg_all,
        ):
            layout.addWidget(btn)

        self._btn_png_active.clicked.connect(self._export_png_active)
        self._btn_png_all.clicked.connect(self._export_png_all)
        self._btn_jpg_active.clicked.connect(self._export_jpg_active)
        self._btn_jpg_all.clicked.connect(self._export_jpg_all)

        # --- choose-folder exports ---
        label_pick = QLabel("Export to chosen folder:")
        label_pick.setStyleSheet("color: #aaa; font-size: 11px; margin-top: 4px;")
        layout.addWidget(label_pick)

        self._btn_png_active_pick = QPushButton("PNG  — active doc…")
        self._btn_png_all_pick = QPushButton("PNG  — all docs…")
        self._btn_jpg_active_pick = QPushButton("JPEG — active doc…")
        self._btn_jpg_all_pick = QPushButton("JPEG — all docs…")

        for btn in (
            self._btn_png_active_pick,
            self._btn_png_all_pick,
            self._btn_jpg_active_pick,
            self._btn_jpg_all_pick,
        ):
            layout.addWidget(btn)

        self._btn_png_active_pick.clicked.connect(self._export_png_active_pick)
        self._btn_png_all_pick.clicked.connect(self._export_png_all_pick)
        self._btn_jpg_active_pick.clicked.connect(self._export_jpg_active_pick)
        self._btn_jpg_all_pick.clicked.connect(self._export_jpg_all_pick)

    # --- same-folder handlers ---
    def _export_png_active(self):
        _export_doc(Krita.instance().activeDocument(), "png")

    def _export_png_all(self):
        for doc in Krita.instance().documents():
            _export_doc(doc, "png")

    def _export_jpg_active(self):
        _export_doc(Krita.instance().activeDocument(), "jpg")

    def _export_jpg_all(self):
        for doc in Krita.instance().documents():
            _export_doc(doc, "jpg")

    # --- choose-folder handlers ---
    def _export_png_active_pick(self):
        folder = _pick_folder("Select output folder — PNG")
        if folder:
            _export_doc(Krita.instance().activeDocument(), "png", folder)

    def _export_png_all_pick(self):
        folder = _pick_folder("Select output folder — PNG (all docs)")
        if folder:
            for doc in Krita.instance().documents():
                _export_doc(doc, "png", folder)

    def _export_jpg_active_pick(self):
        folder = _pick_folder("Select output folder — JPEG")
        if folder:
            _export_doc(Krita.instance().activeDocument(), "jpg", folder)

    def _export_jpg_all_pick(self):
        folder = _pick_folder("Select output folder — JPEG (all docs)")
        if folder:
            for doc in Krita.instance().documents():
                _export_doc(doc, "jpg", folder)
