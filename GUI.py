#!/usr/bin/env python3
import sys
import os
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QFormLayout, QLineEdit, QPushButton,
    QFileDialog, QMessageBox, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QFrame
)
from PyQt5.QtCore import Qt
from main import generate_abc_flow

class ABCFlowGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ABC Flow Generator GUI")
        self._build_ui()

    def _build_ui(self):
        layout = QFormLayout()

        # ABC coefficients
        self.A_edit = QLineEdit("1.0")
        layout.addRow("Coefficient A:", self.A_edit)
        self.B_edit = QLineEdit("1.0")
        layout.addRow("Coefficient B:", self.B_edit)
        self.C_edit = QLineEdit("1.0")
        layout.addRow("Coefficient C:", self.C_edit)

        # Separator before grid size
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setFrameShadow(QFrame.Sunken)
        layout.addRow(sep1)

        # Grid points per axis
        self.N_edit = QLineEdit("48")
        layout.addRow("Grid points per axis (N):", self.N_edit)

        # Sinusoidal terms table
        self.table = QTableWidget(1, 3)
        self.table.setHorizontalHeaderLabels(["ε_i", "ω_i", "β_i"])
        self.table.verticalHeader().setDefaultSectionSize(20)
        for col in range(3):
            self.table.setColumnWidth(col, 60)
            self.table.setItem(0, col, QTableWidgetItem(""))
        self.table.itemChanged.connect(self._on_table_item_changed)
        layout.addRow(QLabel("Sinusoidal terms (fill one cell to add row):"), self.table)

        # Linear rates input
        self.a_list_edit = QLineEdit("1.0,0.3")
        layout.addRow("Linear rates a_j (comma-separated):", self.a_list_edit)

        # Time parameters
        self.tstart_edit = QLineEdit("0.0")
        layout.addRow("Start time t_start:", self.tstart_edit)
        self.tend_edit = QLineEdit("10.0")
        layout.addRow("End time t_end:", self.tend_edit)
        self.nstep_edit = QLineEdit("200")
        layout.addRow("Number of steps n_step:", self.nstep_edit)

        # Separator before filename
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setFrameShadow(QFrame.Sunken)
        layout.addRow(sep2)

        # Base filename
        self.basename_edit = QLineEdit("abc")
        layout.addRow("Base filename:", self.basename_edit)

        # Output directory
        self.outdir_edit = QLineEdit(os.path.abspath("output"))
        choose_btn = QPushButton("Browse...")
        choose_btn.clicked.connect(self._choose_outdir)
        dir_widget = QWidget()
        dir_layout = QHBoxLayout(dir_widget)
        dir_layout.setContentsMargins(0, 0, 0, 0)
        dir_layout.addWidget(self.outdir_edit)
        dir_layout.addWidget(choose_btn)
        layout.addRow("Output directory:", dir_widget)

        # Generate Flow button
        self.run_btn = QPushButton("Generate Flow")
        self.run_btn.clicked.connect(self._on_run)
        layout.addRow(self.run_btn)

        self.setLayout(layout)

    def _on_table_item_changed(self, item):
        row = item.row()
        last = self.table.rowCount() - 1
        if row == last and item.text().strip():
            self.table.blockSignals(True)
            for col in range(3):
                cell = self.table.item(row, col)
                if not cell.text().strip():
                    cell.setText("0")
            self.table.blockSignals(False)
            self.table.insertRow(last + 1)
            for c in range(3):
                self.table.setItem(last + 1, c, QTableWidgetItem(""))

    def _choose_outdir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.outdir_edit.setText(directory)

    def _on_run(self):
        try:
            # parse inputs
            A = float(self.A_edit.text()); B = float(self.B_edit.text()); C = float(self.C_edit.text())
            N = int(self.N_edit.text())
            # sinusoidal terms
            epsilons, omegas, betas = [], [], []
            for r in range(self.table.rowCount()):
                items = [self.table.item(r, c) for c in range(3)]
                if any(it is None or not it.text().strip() for it in items):
                    break
                epsilons.append(float(items[0].text())); omegas.append(float(items[1].text())); betas.append(float(items[2].text()))
            a_list = [float(x) for x in self.a_list_edit.text().split(',') if x.strip()]
            t0 = float(self.tstart_edit.text()); t1 = float(self.tend_edit.text()); steps = int(self.nstep_edit.text())
            out = self.outdir_edit.text(); base = self.basename_edit.text().strip()

            def update_progress(done, total):
                pct = int(done / total * 100)
                self.run_btn.setText(f"{pct}%")
                p = pct / 100.0
                delta = 0.001
                style = (
                    "QPushButton {"
                    "border: 1px solid #555;"
                    "border-radius: 4px;"
                    "padding: 5px;"
                    "color: black;"
                    "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
                    f"stop:0 green, stop:{p:.3f} green, stop:{min(p+delta,1.0):.3f} lightgray, stop:1 lightgray);"
                    "}"
                )
                self.run_btn.setStyleSheet(style)
                QApplication.processEvents()

            self.run_btn.setEnabled(False)
            generate_abc_flow(
                N, A, B, C,
                epsilons, omegas, betas,
                a_list,
                t0, t1, steps,
                out, base,
                progress_callback=update_progress
            )
            self.run_btn.setText("Generate Flow")
            self.run_btn.setStyleSheet("")
            self.run_btn.setEnabled(True)
            QMessageBox.information(self, "Success", f"Generated flow in '{out}'")
        except Exception as e:
            self.run_btn.setEnabled(True)
            self.run_btn.setText("Generate Flow")
            self.run_btn.setStyleSheet("")
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ABCFlowGUI()
    gui.show()
    sys.exit(app.exec_())
