# Python
from __future__ import annotations
import sys
import threading
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

# Import core logic (no Qt dependencies here)
from .ingestion import ingest_corpus
from .preprocessing import build_pipeline, preflight_spacy, content_counts_for_doc
from .io_artifacts import write_docs_csv, write_tokens_csv, write_errors_csv, write_run_poc_json
from .logging_setup import setup_logging

# Qt imports used only in this GUI module
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt, Signal, QThread

# Matplotlib with Qt backend
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


@dataclass
class GuiParams:
    input_dir: Path
    output_dir: Path
    encoding: str = "utf-8"
    include_patterns: List[str] = None
    exclude_patterns: List[str] = None
    keep_stopwords: bool = False
    content_pos: List[str] = None
    lowercase: bool = True
    batch_size: int = 64
    log_level: str = "INFO"

    def __post_init__(self):
        if self.include_patterns is None:
            self.include_patterns = ["*.txt"]
        if self.exclude_patterns is None:
            self.exclude_patterns = []
        if self.content_pos is None:
            self.content_pos = ["NOUN", "VERB", "ADJ", "ADV"]


class PocWorker(QThread):
    progress = Signal(str)
    error = Signal(str)
    finished_with_results = Signal(list, list, dict)  # docs_rows, tokens_rows, meta

    def __init__(self, params: GuiParams, parent=None):
        super().__init__(parent)
        self.params = params
        self._cancel = threading.Event()

    def cancel(self):
        self._cancel.set()

    def run(self):
        try:
            p = self.params
            # Logging
            log_path = setup_logging(p.output_dir, level=p.log_level)
            self.progress.emit(f"Logging to {log_path}")

            # Preflight spaCy
            self.progress.emit("Preflighting spaCy model…")
            try:
                spacy_version, model_name = preflight_spacy("en_core_web_sm")
            except Exception as e:
                self.error.emit("spaCy model not available: en_core_web_sm")
                return

            if self._cancel.is_set():
                self.progress.emit("Cancelled before ingestion")
                return

            # Ingestion
            self.progress.emit("Discovering and reading documents…")
            try:
                docs, errors = ingest_corpus(
                    input_dir=p.input_dir,
                    encoding=p.encoding,
                    include_patterns=p.include_patterns,
                    exclude_patterns=p.exclude_patterns,
                    fail_on_decode_error=False,
                )
            except Exception as e:
                self.error.emit(f"Ingestion failed: {e}")
                return

            if self._cancel.is_set():
                self.progress.emit("Cancelled before preprocessing")
                return

            # Preprocessing
            self.progress.emit("Building NLP pipeline…")
            nlp = build_pipeline("en_core_web_sm", add_sentencizer=True)

            docs_rows: List[Dict[str, object]] = []
            tokens_rows: List[Dict[str, object]] = []

            for i, d in enumerate(docs):
                if self._cancel.is_set():
                    self.progress.emit("Cancellation requested; stopping…")
                    break
                n_sentences, n_tokens_raw, n_tokens_content, counts, n_types_content = content_counts_for_doc(
                    nlp=nlp,
                    text=d.text,
                    content_pos=p.content_pos,
                    lowercase=p.lowercase,
                    keep_stopwords=p.keep_stopwords,
                )
                docs_rows.append(
                    {
                        "doc_id": d.doc_id,
                        "category": d.category,
                        "path": str(d.path),
                        "n_chars": d.n_chars,
                        "n_sentences": n_sentences,
                        "n_tokens_raw": n_tokens_raw,
                        "n_tokens_content": n_tokens_content,
                        "n_types_content": n_types_content,
                        "encoding_used": d.encoding_used,
                        "warnings": "",
                    }
                )
                for (lemma, pos), count in counts.items():
                    tokens_rows.append({"doc_id": d.doc_id, "lemma": lemma, "pos": pos, "count": int(count)})
                if i % 5 == 0:
                    self.progress.emit(f"Processed {i+1}/{len(docs)} docs…")

            # Artifacts (best-effort; even if cancelled midway, we may write partial for demo)
            try:
                docs_csv = write_docs_csv(p.output_dir, docs_rows)
                tokens_csv = write_tokens_csv(p.output_dir, tokens_rows)
                errors_csv = write_errors_csv(p.output_dir, [
                    {"path": str(ep), "stage": stg, "error_type": "UnicodeDecodeError", "message": msg}
                    for (ep, stg, msg) in errors
                ]) if 'errors' in locals() else None
                meta = {
                    "docs_csv": str(docs_csv),
                    "tokens_csv": str(tokens_csv),
                    "errors_csv": str(errors_csv) if errors_csv else None,
                    "log_file": str((p.output_dir / 'logs' / 'poc_run.log')),
                    "spacy_version": spacy_version,
                    "spacy_model": model_name,
                }
                # Minimal run summary JSON
                write_run_poc_json(
                    p.output_dir,
                    environment={
                        "started_at": None,
                        "python": sys.version.split()[0],
                        "packages": {"spacy": spacy_version, "model": model_name},
                    },
                    config_snapshot={
                        "input": {
                            "corpus_dir": str(p.input_dir),
                            "encoding": p.encoding,
                            "include_patterns": p.include_patterns,
                            "exclude_patterns": p.exclude_patterns,
                        },
                        "preprocessing": {
                            "language": "en",
                            "keep_stopwords": bool(p.keep_stopwords),
                            "content_pos": p.content_pos,
                            "lowercase": bool(p.lowercase),
                            "batch_size": int(p.batch_size),
                        },
                        "output": {"output_dir": str(p.output_dir)},
                    },
                    inputs={"documents_processed": len(docs_rows)},
                    artifacts={
                        "docs_csv": {"path": meta["docs_csv"]},
                        "tokens_table": {"path": meta["tokens_csv"]},
                        "errors_csv": {"path": meta["errors_csv"]},
                        "log_file": {"path": meta["log_file"]},
                    },
                    timings_sec={"ingestion": 0.0, "preprocessing": 0.0, "export": 0.0},
                )
            except Exception:
                # Non-fatal for GUI display
                pass

            self.finished_with_results.emit(docs_rows, tokens_rows, meta)
        except Exception as e:
            tb = traceback.format_exc()
            self.error.emit(f"Unexpected error: {e}\n{tb}")


class MatplotlibWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def plot_top_tokens(self, tokens_rows: List[Dict[str, object]], top_n: int = 10):
        ax = self.figure.clear().add_subplot(111)
        # Aggregate by lemma
        from collections import Counter
        c = Counter()
        for r in tokens_rows:
            c[(r["lemma"], r["pos"]) ] += int(r["count"])  # type: ignore
        top = c.most_common(top_n)
        labels = [f"{lem} ({pos})" for (lem, pos), _ in top]
        values = [val for _, val in top]
        ax.bar(labels, values)
        ax.set_title("Top content tokens")
        ax.set_ylabel("Count")
        ax.set_xticklabels(labels, rotation=45, ha='right')
        self.canvas.draw_idle()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LMDA PoC (PySide6 GUI)")
        self.resize(900, 600)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # Controls
        form = QtWidgets.QFormLayout()
        self.input_edit = QtWidgets.QLineEdit(str(Path("data/fixture_corpus").resolve()))
        self.output_edit = QtWidgets.QLineEdit(str(Path("artefacts_poc").resolve()))
        browse_in = QtWidgets.QPushButton("Browse…")
        browse_out = QtWidgets.QPushButton("Browse…")
        hb1 = QtWidgets.QHBoxLayout(); hb1.addWidget(self.input_edit); hb1.addWidget(browse_in)
        hb2 = QtWidgets.QHBoxLayout(); hb2.addWidget(self.output_edit); hb2.addWidget(browse_out)
        form.addRow("Input Dir:", self._wrap(hb1))
        form.addRow("Output Dir:", self._wrap(hb2))

        self.run_btn = QtWidgets.QPushButton("Run")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        hb3 = QtWidgets.QHBoxLayout(); hb3.addStretch(1); hb3.addWidget(self.run_btn); hb3.addWidget(self.cancel_btn)

        layout.addLayout(form)
        layout.addLayout(hb3)

        # Plot + Table
        self.plot = MatplotlibWidget()
        self.table = QtWidgets.QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["doc_id", "category", "n_sentences", "n_tokens_raw", "n_tokens_content", "n_types_content"])
        self.table.horizontalHeader().setStretchLastSection(True)

        split = QtWidgets.QSplitter(Qt.Horizontal)
        split.addWidget(self.plot)
        split.addWidget(self.table)
        split.setSizes([600, 300])
        layout.addWidget(split)

        # Status
        self.status_edit = QtWidgets.QPlainTextEdit()
        self.status_edit.setReadOnly(True)
        layout.addWidget(self.status_edit, stretch=1)

        # Menu
        self._build_menu()

        # Connections
        browse_in.clicked.connect(self._choose_input)
        browse_out.clicked.connect(self._choose_output)
        self.run_btn.clicked.connect(self._on_run)
        self.cancel_btn.clicked.connect(self._on_cancel)

        self.worker: PocWorker | None = None

    def _wrap(self, layout: QtWidgets.QHBoxLayout) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget(); w.setLayout(layout); return w

    def _build_menu(self):
        m = self.menuBar().addMenu("Help")
        about = QtWidgets.QAction("About / Licenses", self)
        about.triggered.connect(self._show_about)
        m.addAction(about)

    def _show_about(self):
        QtWidgets.QMessageBox.information(
            self,
            "About LMDA PoC",
            "LMDA PoC GUI (PySide6)\n\n"
            "Project License: Apache-2.0.\n"
            "This application uses PySide6/Qt (LGPLv3).\n"
            "For distribution, include license texts in a licenses/ folder.")

    def _choose_input(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose input directory", self.input_edit.text())
        if d:
            self.input_edit.setText(d)

    def _choose_output(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose output directory", self.output_edit.text())
        if d:
            self.output_edit.setText(d)

    def log(self, msg: str):
        self.status_edit.appendPlainText(msg)

    def _on_run(self):
        inp = Path(self.input_edit.text())
        out = Path(self.output_edit.text())
        if not inp.exists():
            QtWidgets.QMessageBox.warning(self, "Invalid input", f"Input directory does not exist: {inp}")
            return
        out.mkdir(parents=True, exist_ok=True)
        params = GuiParams(input_dir=inp, output_dir=out)
        self.worker = PocWorker(params)
        self.worker.progress.connect(self.log)
        self.worker.error.connect(lambda m: QtWidgets.QMessageBox.critical(self, "Error", m))
        self.worker.finished_with_results.connect(self._on_finished)
        self.worker.start()
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.log("Started…")

    def _on_cancel(self):
        if self.worker:
            self.worker.cancel()
            self.log("Cancellation requested…")

    def closeEvent(self, e):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(2000)
        return super().closeEvent(e)

    def _on_finished(self, docs_rows: List[Dict[str, object]], tokens_rows: List[Dict[str, object]], meta: Dict[str, str]):
        self.log("Finished.")
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        # Update table
        self.table.setRowCount(0)
        for r in docs_rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            vals = [r.get("doc_id", ""), r.get("category", ""), r.get("n_sentences", 0), r.get("n_tokens_raw", 0), r.get("n_tokens_content", 0), r.get("n_types_content", 0)]
            for col, v in enumerate(vals):
                item = QtWidgets.QTableWidgetItem(str(v))
                if isinstance(v, int):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, col, item)
        # Plot
        self.plot.plot_top_tokens(tokens_rows, top_n=10)


def launch_gui():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    return app.exec()
