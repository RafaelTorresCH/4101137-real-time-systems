#!/usr/bin/env python3
"""
Generador del documento RET (.docx) — Estado actual: Semana 1 (Lab 01).
Se construye incrementalmente laboratorio por laboratorio junto con el usuario.
"""

import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ACCENT_HEX = "0D9488"      # Color oficial del curso (coursekit.toml)
GRAY_BG_HEX = "F3F4F6"     # Fondo para recuadros de capturas


def w_p(text="", bold=False, italic=False, color=None, size_pt=11, space_after=120, heading_level=None):
    if heading_level == 1:
        size_pt = 18
        bold = True
        color = ACCENT_HEX
        space_after = 180
    elif heading_level == 2:
        size_pt = 14
        bold = True
        color = "111827"
        space_after = 140
    elif heading_level == 3:
        size_pt = 12
        bold = True
        color = ACCENT_HEX
        space_after = 100

    sz = int(size_pt * 2)
    rpr = f"<w:sz w:val=\"{sz}\"/><w:szCs w:val=\"{sz}\"/>"
    if bold:
        rpr += "<w:b/>"
    if italic:
        rpr += "<w:i/>"
    if color:
        rpr += f"<w:color w:val=\"{color}\"/>"

    return (
        f"<w:p>"
        f"<w:pPr><w:spacing w:after=\"{space_after}\"/></w:pPr>"
        f"<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space=\"preserve\">{escape(text)}</w:t></w:r>"
        f"</w:p>"
    )


def w_evidence_box(title, subtitle):
    return (
        f"<w:tbl>"
        f"<w:tblPr>"
        f"<w:tblW w:w=\"5000\" w:type=\"pct\"/>"
        f"<w:tblBorders>"
        f"<w:top w:val=\"dashed\" w:sz=\"8\" w:space=\"0\" w:color=\"{ACCENT_HEX}\"/>"
        f"<w:left w:val=\"dashed\" w:sz=\"8\" w:space=\"0\" w:color=\"{ACCENT_HEX}\"/>"
        f"<w:bottom w:val=\"dashed\" w:sz=\"8\" w:space=\"0\" w:color=\"{ACCENT_HEX}\"/>"
        f"<w:right w:val=\"dashed\" w:sz=\"8\" w:space=\"0\" w:color=\"{ACCENT_HEX}\"/>"
        f"</w:tblBorders>"
        f"</w:tblPr>"
        f"<w:tr><w:tc>"
        f"<w:tcPr>"
        f"<w:shd w:val=\"clear\" w:color=\"auto\" w:fill=\"{GRAY_BG_HEX}\"/>"
        f"<w:tcMar><w:top w:w=\"140\" w:type=\"dxa\"/><w:bottom w:w=\"140\" w:type=\"dxa\"/>"
        f"<w:left w:w=\"180\" w:type=\"dxa\"/><w:right w:w=\"180\" w:type=\"dxa\"/></w:tcMar>"
        f"</w:tcPr>"
        f"{w_p(title, bold=True, color=ACCENT_HEX, size_pt=10, space_after=40)}"
        f"{w_p(subtitle, italic=True, color='4B5563', size_pt=9.5, space_after=160)}"
        f"{w_p('[ Pegar imagen / captura aquí (Ctrl+V) ]', color='6B7280', size_pt=9.5, space_after=160)}"
        f"</w:tc></w:tr></w:tbl>"
        f"{w_p('', space_after=80)}"
    )


def w_table(headers, rows):
    borders = (
        "<w:tblBorders>"
        "<w:top w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"D1D5DB\"/>"
        "<w:left w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"D1D5DB\"/>"
        "<w:bottom w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"D1D5DB\"/>"
        "<w:right w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"D1D5DB\"/>"
        "<w:insideH w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"E5E7EB\"/>"
        "<w:insideV w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"E5E7EB\"/>"
        "</w:tblBorders>"
    )
    xml = f"<w:tbl><w:tblPr><w:tblW w:w=\"5000\" w:type=\"pct\"/>{borders}</w:tblPr>"

    xml += "<w:tr>"
    for h in headers:
        xml += (
            "<w:tc>"
            f"<w:tcPr><w:shd w:val=\"clear\" w:color=\"auto\" w:fill=\"{ACCENT_HEX}\"/>"
            "<w:tcMar><w:top w:w=\"100\" w:type=\"dxa\"/><w:bottom w:w=\"100\" w:type=\"dxa\"/>"
            "<w:left w:w=\"120\" w:type=\"dxa\"/><w:right w:w=\"120\" w:type=\"dxa\"/></w:tcMar></w:tcPr>"
            f"{w_p(h, bold=True, color='FFFFFF', size_pt=10, space_after=0)}"
            "</w:tc>"
        )
    xml += "</w:tr>"

    for idx, row in enumerate(rows):
        bg = "FFFFFF" if idx % 2 == 0 else "F9FAFB"
        xml += "<w:tr>"
        for cell in row:
            xml += (
                "<w:tc>"
                f"<w:tcPr><w:shd w:val=\"clear\" w:color=\"auto\" w:fill=\"{bg}\"/>"
                "<w:tcMar><w:top w:w=\"80\" w:type=\"dxa\"/><w:bottom w:w=\"80\" w:type=\"dxa\"/>"
                "<w:left w:w=\"120\" w:type=\"dxa\"/><w:right w:w=\"120\" w:type=\"dxa\"/></w:tcMar></w:tcPr>"
                f"{w_p(str(cell), bold=False, color='111827', size_pt=9.5, space_after=0)}"
                "</w:tc>"
            )
        xml += "</w:tr>"

    xml += f"</w:tbl>{w_p('', space_after=100)}"
    return xml


def build_document_xml():
    body = []

    # ENCABEZADO OFICIAL (templates/ret.md)
    body.append(w_p("RET — Timing Evidence Report", heading_level=1))
    body.append(w_p("• Team: <names>", size_pt=10.5, space_after=40))
    body.append(w_p("• Boards: ESP32-C6-DevKitC-1 (esp32c6_devkitc/esp32c6/hpcore), native_sim/native/64", size_pt=10.5, space_after=40))
    body.append(w_p("• AI use: Week 1: Antigravity (Gemini) — initial RET structure and EARS task set table.", size_pt=10.5, space_after=100))
    body.append(w_p(
        "Living document — updated every week; handed in at the workshop (week 7) and at the close (week 14).",
        italic=True, color="4B5563", size_pt=10, space_after=60
    ))
    body.append(w_p(
        "House rule: \"show me the trace\" — every timing claim cites a measurement.",
        bold=True, color="111827", size_pt=10, space_after=140
    ))

    # =========================================================================
    # 1. THE SYSTEM AND ITS TASK SET (ENTREGABLE DEL LAB 1)
    # =========================================================================
    body.append(w_p("1. The system and its task set", heading_level=2))
    body.append(w_p(
        "Requirements first — one sentence each, EARS style (when/while <condition>, "
        "the system shall <response> within <deadline>) — then the task that implements them:",
        size_pt=10
    ))

    body.append(w_table(
        ["ID", "Requirement"],
        [
            ["REQ-SAMP-01", "While the node is powered on, the system shall sample the pressure sensor, check the e-stop condition, and update the valve PWM phase every 1 ms (1 kHz) with bounded jitter."],
            ["REQ-CTRL-01", "While the system is irrigating, the control loop shall compute the PI control law and update the valve duty cycle every 10 ms (deadline = period)."],
            ["REQ-ESTOP-01", "When an overpressure condition is detected, the system shall close the valve and trip the emergency stop within 5 ms."],
            ["REQ-CONS-01", "When an operator sends a command over the UART console, the system shall parse and respond within 100 ms."],
            ["REQ-TELE-01", "While the system is running, the node shall transmit a CSV telemetry line every 1000 ms (1 Hz)."],
            ["REQ-DISP-01", "While the local OLED HMI is enabled, the system shall refresh the display every 500 ms (2 Hz)."],
        ]
    ))

    body.append(w_table(
        ["Task", "Req.", "Type (H/F/S)", "Period", "Deadline", "Measured C_i", "How it was measured"],
        [
            ["Sensor sampling", "REQ-SAMP-01", "Hard", "1 ms", "= T", "____", "<GPIO + analyzer / trace>"],
            ["Control loop", "REQ-CTRL-01", "Hard", "10 ms", "= T", "____", "<GPIO + analyzer / trace>"],
            ["Overpressure e-stop", "REQ-ESTOP-01", "Hard", "1 ms (polled)", "5 ms", "____", "<GPIO + analyzer / trace>"],
            ["Command console", "REQ-CONS-01", "Firm", "Sporadic", "100 ms", "____", "<GPIO + analyzer / trace>"],
            ["Telemetry to the Hub", "REQ-TELE-01", "Soft", "1000 ms", "1000 ms", "____", "<GPIO + analyzer / trace>"],
            ["Display HMI (optional)", "REQ-DISP-01", "Soft", "500 ms", "500 ms", "____", "<GPIO + analyzer / trace>"],
        ]
    ))

    # =========================================================================
    # 2. ADRs (PLANTILLA BASE DE templates/ret.md)
    # =========================================================================
    body.append(w_p("2. ADRs", heading_level=2))
    body.append(w_p("ADR-001 — <title>", heading_level=3))
    body.append(w_p("Context: … · Decision: … · Justification (with numbers): … · Status: …", size_pt=10))

    # =========================================================================
    # 3. EVIDENCE BY WEEK (SOLO LAB 1 POR AHORA + ENCABEZADOS VACÍOS DE PLANTILLA)
    # =========================================================================
    body.append(w_p("3. Evidence by week", heading_level=2))
    body.append(w_p("Each entry cites the REQ(s) it verifies.", size_pt=10))

    body.append(w_p("Week 1 — Bring-up: the team, the board, the toolchain", heading_level=3))
    body.append(w_table(
        ["Quantity", "Prediction", "Your value", "Target"],
        [
            ["Edit → build (-p) → flash → message on the console, one member's laptop", "____ s", "____ s", "< 60 s"],
            ["Same, incremental build (one line changed, no -p)", "____ s", "____ s", ""],
            ["Members with blinky running from their own laptop", "", "____ / ____", "all"],
        ]
    ))

    body.append(w_evidence_box(
        "Task A — Blinky running on ESP32-C6-DevKitC-1 (one flash per member)",
        "Pegar aquí foto del LED parpadeando / captura de terminal de cada integrante."
    ))
    body.append(w_evidence_box(
        "Task B — Serial console (115200 8N1) with modified hello_world message & cycle times",
        "Pegar aquí captura del monitor serial con el mensaje modificado y los dos tiempos (con -p y sin -p)."
    ))

    body.append(w_p("Week 2 — superloop baseline (state the board)", heading_level=3))
    body.append(w_p("<jitter/latency table + a one-sentence reading>", italic=True, color="6B7280", size_pt=10))

    # =========================================================================
    # 4, 5, 6 (SOLO ENCABEZADOS DE LA PLANTILLA OFICIAL templates/ret.md)
    # =========================================================================
    body.append(w_p("4. Schedulability analysis", heading_level=2))
    body.append(w_p(
        "U = ΣC_i/T_i with measured C_i; test used (RM / hyperbolic / EDF); RTA as a script with its output; blocking B_i if there are mutexes.",
        italic=True, color="6B7280", size_pt=10
    ))

    body.append(w_p("5. Functional safety (final project)", heading_level=2))
    body.append(w_p(
        "Declared safe state (failure ⇒ valve closed), watchdog, and the evidence of the fail-safe firing.",
        italic=True, color="6B7280", size_pt=10
    ))

    body.append(w_p("6. Agent-built components (final project)", heading_level=2))
    body.append(w_p(
        "The Hub's GUI and routing, built by an agent from spec/hub-soft.md.",
        italic=True, color="6B7280", size_pt=10
    ))

    body_xml = "".join(body)
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
        f"<w:body>{body_xml}"
        "<w:sectPr>"
        "<w:pgSz w:w=\"12240\" w:h=\"15840\"/>"
        "<w:pgMar w:top=\"1134\" w:right=\"1134\" w:bottom=\"1134\" w:left=\"1134\"/>"
        "</w:sectPr>"
        "</w:body></w:document>"
    )


def create_docx(output_path: Path):
    content_types = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
        "<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>"
        "<Default Extension=\"xml\" ContentType=\"application/xml\"/>"
        "<Override PartName=\"/word/document.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/>"
        "</Types>"
    )
    rels = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        "<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"word/document.xml\"/>"
        "</Relationships>"
    )
    doc_rels = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"/>"
    )

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/_rels/document.xml.rels", doc_rels)
        zf.writestr("word/document.xml", build_document_xml())


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent
    out_file = out_dir / "RET_y_Laboratorios.docx"
    create_docx(out_file)
    print(f"Plantilla con solo Lab 1 generada en: {out_file}")
