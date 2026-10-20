from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


PROJECT = Path(r"C:\Users\katom\iCloudDrive\Smaller Creator\Sky\Marc Torrens Assignment")
SOURCE = PROJECT / "slides" / "Mark-slides.md"
OUTPUT = PROJECT / "slides" / "credit-risk-business-deck-final.pptx"

PML = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"

SLIDE_W = 12192000
SLIDE_H = 6858000
BG = "070A12"
WHITE = "F7F9FC"
MUTED = "D5DCE6"
PURPLE = "8A4DFF"
TEAL = "35E0D0"
SILVER = "B9C4D2"
PANEL = "121827"
HEADER = "2B1E59"
ACCENT = "35E0D0"


def x(tag: str, attrs: dict[str, str] | None = None, body: str = "") -> str:
    attrs = attrs or {}
    attr_text = "".join(f' {k}="{escape(str(v))}"' for k, v in attrs.items())
    return f"<{tag}{attr_text}>{body}</{tag}>"


def empty(tag: str, attrs: dict[str, str] | None = None) -> str:
    attrs = attrs or {}
    attr_text = "".join(f' {k}="{escape(str(v))}"' for k, v in attrs.items())
    return f"<{tag}{attr_text}/>"


def parse_slides(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^## Slide \d+\s*(?:-\s*)?(.+)$", text, flags=re.MULTILINE))
    slides: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        slides.append((match.group(1).strip(), text[start:end].strip()))
    if not slides:
        raise ValueError("No slides found")
    return slides


def normalize(value: str) -> str:
    return (
        value.replace("Ã—", "×")
        .replace("â€”", "—")
        .replace("â€“", "–")
        .replace("â‚¬", "€")
        .replace("â€¢", "•")
        .replace("â€˜", "‘")
        .replace("â€™", "’")
    )


def normalize(value: str) -> str:
    replacements = [
        (chr(0xC3) + chr(0x2014), chr(0xD7)),
        (chr(0xE2) + chr(0x201A) + chr(0xAC), chr(0x20AC)),
        (chr(0xE2) + chr(0x20AC) + chr(0xA2), chr(0x2022)),
        (chr(0xE2) + chr(0x20AC) + chr(0x201D), chr(0x2014)),
        (chr(0xE2) + chr(0x20AC) + chr(0x201C), chr(0x2013)),
    ]
    for old, new in replacements:
        value = value.replace(old, new)
    return value


def text_run(value: str, size: int, color: str = WHITE, bold: bool = False, font: str = "Aptos") -> str:
    props = empty("a:rPr", {"lang": "en-US", "sz": str(size), "b": "1" if bold else "0", "dirty": "0"})
    props += x("a:solidFill", body=x("a:srgbClr", {"val": color}))
    props += empty("a:latin", {"typeface": font})
    return x("a:r", body=props + x("a:t", body=escape(normalize(value))))


def paragraph(value: str, size: int = 1800, color: str = WHITE, bold: bool = False) -> str:
    default_props = x("a:defRPr", {"lang": "en-US", "sz": str(size), "b": "1" if bold else "0"}, body=solid_fill(color) + empty("a:latin", {"typeface": "Aptos"}))
    return x(
        "a:p",
        body=(
            x("a:pPr", {"marL": "0", "indent": "0"}, default_props)
            + text_run(value, size, color, bold)
            + empty("a:endParaRPr", {"lang": "en-US", "sz": str(size)})
        ),
    )


def tx_body(paragraphs: list[str], size: int = 1800, color: str = WHITE, bold_first: bool = False) -> str:
    body = empty("a:bodyPr", {"wrap": "square", "rtlCol": "0"})
    body += empty("a:lstStyle")
    for idx, value in enumerate(paragraphs):
        body += paragraph(value, size, color, bold_first and idx == 0)
    return body


def solid_fill(color: str, alpha: int = 100000) -> str:
    color_xml = x("a:srgbClr", {"val": color})
    if alpha < 100000:
        color_xml = x("a:srgbClr", {"val": color}, empty("a:alpha", {"val": str(alpha)}))
    return x("a:solidFill", body=color_xml)


def gradient_fill(start: str, end: str, alpha: int = 100000, angle: int = 5400000) -> str:
    start_xml = x("a:srgbClr", {"val": start}, empty("a:alpha", {"val": str(alpha)}))
    end_xml = x("a:srgbClr", {"val": end}, empty("a:alpha", {"val": str(alpha)}))
    return x("a:gradFill", {"rotWithShape": "1"}, x("a:gsLst", body=x("a:gs", {"pos": "0"}, start_xml) + x("a:gs", {"pos": "100000"}, end_xml)) + empty("a:lin", {"ang": str(angle), "scaled": "1"}))


def shape(sp_id: int, name: str, left: int, top: int, width: int, height: int, body: str, fill: str | None = None, line: str | None = None, geom_prst: str = "rect", fill_xml: str | None = None, line_xml: str | None = None) -> str:
    fill_xml = fill_xml if fill_xml is not None else (empty("a:noFill") if fill is None else solid_fill(fill))
    line_xml = line_xml if line_xml is not None else (empty("a:noFill") if line is None else solid_fill(line))
    geom = empty("a:prstGeom", {"prst": geom_prst})
    sp_pr = x("p:spPr", body=x("a:xfrm", body=empty("a:off", {"x": left, "y": top}) + empty("a:ext", {"cx": width, "cy": height})) + geom + fill_xml + x("a:ln", body=line_xml))
    nv = x("p:nvSpPr", body=empty("p:cNvPr", {"id": sp_id, "name": name}) + empty("p:cNvSpPr") + empty("p:nvPr"))
    return x("p:sp", body=nv + sp_pr + x("p:txBody", body=body))


def title_shape(sp_id: int, title: str) -> str:
    return shape(sp_id, "Title", 430000, 250000, 11300000, 620000, tx_body([title], 2600, WHITE, True))


def body_shape(sp_id: int, paragraphs: list[str], size: int = 1800, top: int = 1050000, height: int = 5450000) -> str:
    return shape(sp_id, "Body", 600000, top, 11180000, height, tx_body(paragraphs, size, MUTED))


def panel_shape(sp_id: int, accent: str, top: int = 1000000, height: int = 5550000) -> str:
    return shape(sp_id, "Content panel", 430000, top, 11300000, height, tx_body([]), geom_prst="roundRect", fill_xml=solid_fill(PANEL, 90000), line_xml=solid_fill(accent, 52000))


def footer_shapes(index: int, total: int) -> list[str]:
    footer_text = tx_body(["CREDIT RISK CLASSIFICATION  /  DECISION SUPPORT"], 700, SILVER)
    page_text = tx_body([f"{index:02d} / {total:02d}"], 800, TEAL, True)
    return [
        shape(15, "Footer", 650000, 6420000, 6500000, 260000, footer_text),
        shape(16, "Page number", 10300000, 6420000, 900000, 260000, page_text),
        shape(17, "Footer rule", 650000, 6250000, 10500000, 30000, tx_body([]), fill_xml=solid_fill(PURPLE, 75000), line_xml=empty("a:noFill")),
    ]


def centered_title_shape(sp_id: int, title: str) -> str:
    return shape(sp_id, "Closing title", 1200000, 2700000, 9700000, 1050000, tx_body([title], 4200, WHITE, True))


def decorative_shapes() -> list[str]:
    return [
        shape(11, "Purple glow", 8750000, -900000, 4700000, 3500000, tx_body([]), geom_prst="ellipse", fill_xml=gradient_fill(PURPLE, "331A75", 23000, 5400000)),
        shape(12, "Turquoise glow", -1050000, 5100000, 4000000, 2600000, tx_body([]), geom_prst="ellipse", fill_xml=gradient_fill(TEAL, "123E59", 18000, 0)),
        shape(13, "Accent rule", 650000, 850000, 1700000, 45000, tx_body([]), fill_xml=solid_fill(TEAL), line_xml=empty("a:noFill")),
        shape(14, "Purple rule", 2400000, 850000, 900000, 45000, tx_body([]), fill_xml=solid_fill(PURPLE), line_xml=empty("a:noFill")),
    ]


def table_cell(value: str, width: int, height: int, header: bool = False) -> str:
    fill = HEADER if header else "1A1E22"
    tc_pr = x("a:tcPr", body=x("a:solidFill", body=x("a:srgbClr", {"val": fill})) + x("a:lnL", body=x("a:solidFill", body=x("a:srgbClr", {"val": "77818B"}))) + x("a:lnR", body=x("a:solidFill", body=x("a:srgbClr", {"val": "77818B"}))) + x("a:lnT", body=x("a:solidFill", body=x("a:srgbClr", {"val": "77818B"}))) + x("a:lnB", body=x("a:solidFill", body=x("a:srgbClr", {"val": "77818B"}))))
    return x(
        "a:tc",
        body=(
            x("a:txBody", body=empty("a:bodyPr", {"wrap": "square"}) + empty("a:lstStyle") + paragraph(value, 650 if header else 600, WHITE, header))
            + tc_pr
            + empty("a:extLst")
        ),
    )


def table_shape(sp_id: int, rows: list[list[str]], widths: list[int] | None = None, top: int = 970000, height: int = 4500000) -> str:
    widths = widths or [930000, 2200000, 730000, 560000, 560000, 560000, 560000, 760000, 760000, 1080000, 1080000]
    row_height = 720000
    tbl_grid = "".join(empty("a:gridCol", {"w": w}) for w in widths)
    rows_xml = ""
    for row_index, row in enumerate(rows):
        cells = "".join(table_cell(cell, widths[col_index], row_height, row_index == 0) for col_index, cell in enumerate(row))
        rows_xml += x("a:tr", {"h": row_height}, cells)
    graphic = x(
        "a:graphic",
        body=x(
            "a:graphicData",
            {"uri": "http://schemas.openxmlformats.org/drawingml/2006/table"},
            x("a:tbl", body=empty("a:tblPr", {"firstRow": "1", "bandRow": "1"}) + x("a:tblGrid", body=tbl_grid) + rows_xml),
        ),
    )
    return x(
        "p:graphicFrame",
        body=x("p:nvGraphicFramePr", body=empty("p:cNvPr", {"id": sp_id, "name": "Threshold table"}) + empty("p:cNvGraphicFramePr") + empty("p:nvPr"))
        + x("p:xfrm", body=empty("a:off", {"x": 260000, "y": top}) + empty("a:ext", {"cx": 11600000, "cy": height}))
        + graphic,
    )


def slide_xml(title: str, body: str, index: int) -> str:
    total = 8
    if index == total:
        shapes = decorative_shapes() + [panel_shape(20, TEAL, 850000, 5000000), centered_title_shape(2, title)]
    else:
        panel_accent = TEAL if index % 2 else PURPLE
        shapes = decorative_shapes() + [panel_shape(20, panel_accent), title_shape(2, title)] + footer_shapes(index, total)
    if index == 3:
        compact_rows = [
            ["Model and threshold", "Reviews", "TP FP FN TN", "Precision recall", "Loss avoided", "Net value"],
            ["Example format only", "n and percent", "counts scaled to 8,000", "both metrics", "TP × effectiveness × LGD", "formula and EUR"],
        ]
        compact_widths = [2100000, 1300000, 2200000, 1900000, 2100000, 2000000]
        shapes.append(table_shape(3, compact_rows, compact_widths, top=950000, height=1800000))
        questions = [
            "If recall increases while precision decreases, what changes for the credit team and for applicants?",
            "Which error is more expensive under the base-case assumptions, and does that conclusion change when review capacity is binding?",
            "How does class prevalence affect precision and expected workload, even if ranking quality is unchanged?",
            "Would you deploy a probability threshold, a top-k ranking rule, or a segmented policy? Explain why.",
            "What is missing from the dataset: causal review effect, applicant-level loss exposure, affordability or review eligibility?",
        ]
        shapes.append(body_shape(4, questions, 1250, 3050000, 3050000))
    elif index == 5:
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        table_lines = [line for line in lines if line.startswith("|")]
        rows: list[list[str]] = []
        for line in table_lines:
            if set(line.replace("|", "").replace("-", "").replace(":", "").replace(" ", "")) == set():
                continue
            cells = [normalize(c.strip()) for c in line.strip("|").split("|")]
            if cells and cells[0] != "---":
                rows.append(cells)
        shapes.append(table_shape(3, rows))
        shapes.append(body_shape(4, ["All counts and values are scaled to 8,000 monthly applications."], 1200, 5750000, 500000))
    else:
        cleaned = re.sub(r"</?p>|</?div>|<strong>|</strong>", "", body)
        cleaned = normalize(cleaned)
        paragraphs: list[str] = []
        current = ""
        for raw_line in cleaned.splitlines():
            line = raw_line.strip()
            if not line:
                if current:
                    paragraphs.append(current.strip())
                    current = ""
                continue
            is_bullet = line.startswith("-") or line.startswith(chr(0x2022))
            if is_bullet:
                if current:
                    paragraphs.append(current.strip())
                    current = ""
                paragraphs.append(line.lstrip("-" + chr(0x2022) + " ").strip())
            else:
                current = f"{current} {line}".strip()
        if current:
            paragraphs.append(current.strip())
        size = {1: 1450, 2: 1450, 4: 1250, 6: 1500, 7: 1350, 8: 1800}.get(index, 1500)
        shapes.append(body_shape(3, paragraphs, size))
    shapes_xml = "".join(shapes)
    bg_fill = gradient_fill(BG, "1A0D32", 100000, 5400000)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<p:sld xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{PML}"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/><p:sp id="10" name="Background"><p:nvSpPr><p:cNvPr id="10" name="Background"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_W}" cy="{SLIDE_H}"/></a:xfrm><a:prstGeom prst="rect"/>{bg_fill}<a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/></p:txBody></p:sp>{shapes_xml}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'''


def package_xml(slide_count: int) -> dict[str, str]:
    content = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="{CT}"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/><Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/><Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/><Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'''
    content += "".join(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' for i in range(1, slide_count + 1))
    content += "</Types>"
    files = {"[Content_Types].xml": content}
    files["_rels/.rels"] = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{REL}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>'''
    slide_ids = "".join(f'<p:sldId id="{255 + i}" r:id="rId{i}"/>' for i in range(1, slide_count + 1))
    files["ppt/presentation.xml"] = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:presentation xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{PML}" saveSubsetFonts="1"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId{slide_count + 1}"/></p:sldMasterIdLst><p:sldIdLst>{slide_ids}</p:sldIdLst><p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle><a:defPPr/></p:defaultTextStyle></p:presentation>'''
    rels = "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>' for i in range(1, slide_count + 1))
    rels += f'<Relationship Id="rId{slide_count + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    files["ppt/_rels/presentation.xml.rels"] = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{REL}">{rels}</Relationships>'''
    files["ppt/theme/theme1.xml"] = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:theme xmlns:a="{A}" name="Credit Risk"><a:themeElements><a:clrScheme name="Credit Risk"><a:dk1><a:srgbClr val="000000"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="{BG}"/></a:dk2><a:lt2><a:srgbClr val="{WHITE}"/></a:lt2><a:accent1><a:srgbClr val="{ACCENT}"/></a:accent1><a:accent2><a:srgbClr val="{HEADER}"/></a:accent2><a:hlink><a:srgbClr val="5B8DB8"/></a:hlink><a:folHlink><a:srgbClr val="5B8DB8"/></a:folHlink></a:clrScheme><a:fontScheme name="Aptos"><a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme><a:fmtScheme name="Office"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme></a:themeElements></a:theme>'''
    files["ppt/slideLayouts/slideLayout1.xml"] = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldLayout xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{PML}" type="blank"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'''
    files["ppt/slideLayouts/_rels/slideLayout1.xml.rels"] = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{REL}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>'''
    files["ppt/slideMasters/slideMaster1.xml"] = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldMaster xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{PML}"><p:cSld name="Master"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld><p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles/><p:clrMap accent1="accent1" accent2="accent2" bg1="lt1" tx1="dk1"/></p:sldMaster>'''
    files["ppt/slideMasters/_rels/slideMaster1.xml.rels"] = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{REL}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>'''
    return files


def main() -> None:
    slides = parse_slides(SOURCE.read_text(encoding="utf-8"))
    files = package_xml(len(slides))
    for index, (title, body) in enumerate(slides, 1):
        files[f"ppt/slides/slide{index}.xml"] = slide_xml(title, body, index)
        files[f"ppt/slides/_rels/slide{index}.xml.rels"] = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{REL}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    print(f"Created {OUTPUT}")
    print(f"Slides: {len(slides)}")


if __name__ == "__main__":
    main()
