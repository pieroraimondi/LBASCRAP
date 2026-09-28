"""Crea un file XLSX standard con statistiche e riepilogo partite."""
from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED

from lba_tabellini import FIELDS


def xml_text(value):
    return escape(str(value), {'"': '&quot;', "'": '&apos;'})


def column(number):
    result = ''
    while number:
        number, rem = divmod(number - 1, 26)
        result = chr(65 + rem) + result
    return result


def excel_datetime(value):
    if not value:
        return ''
    return datetime.fromisoformat(value).astimezone(ZoneInfo('Europe/Rome')).replace(tzinfo=None)


def excel_serial(value):
    origin = datetime(1899, 12, 30)
    return (value - origin).total_seconds() / 86400


def sheet_xml(headers, rows):
    xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
           '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
           f'<dimension ref="A1:{column(len(headers))}{len(rows)+1}"/>',
           '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>',
           '<cols>']
    for i, key in enumerate(headers, 1):
        width = 23 if key in ('Squadra', 'Avversaria', 'Giocatore', 'Partita') else (30 if key in ('Data', 'Data e ora') else 16)
        xml.append(f'<col min="{i}" max="{i}" width="{width}" customWidth="1"/>')
    xml.append('</cols><sheetData>')
    for r, values in enumerate([headers] + rows, 1):
        xml.append(f'<row r="{r}">')
        for c, value in enumerate(values, 1):
            ref = column(c) + str(r)
            if value is None or value == '':
                continue
            if isinstance(value, datetime):
                xml.append(f'<c r="{ref}" s="2"><v>{excel_serial(value):.10f}</v></c>')
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                xml.append(f'<c r="{ref}"' + (' s="1"' if r == 1 else '') + f'><v>{value}</v></c>')
            else:
                xml.append(f'<c r="{ref}" t="inlineStr"' + (' s="1"' if r == 1 else '') + f'><is><t>{xml_text(value)}</t></is></c>')
        xml.append('</row>')
    xml.append('</sheetData>')
    if rows:
        xml.append(f'<autoFilter ref="A1:{column(len(headers))}{len(rows)+1}"/>')
    xml.append('</worksheet>')
    return ''.join(xml)


def make_xlsx(day, games):
    stat_headers = ['Stato', 'Data e ora'] + FIELDS
    stats = []
    match_headers = ['Giornata', 'GameID', 'Partita', 'Stato', 'Data e ora', 'Risultato',
                     '1°Q', '2°Q', '3°Q', '4°Q', 'OT', 'Giocatori']
    matches = []
    for g in games:
        partials = {p['name']: f"{p['home']} - {p['away']}" for p in g.get('periods', [])}
        matches.append([day, g['id'], g['home'] + ' - ' + g['away'], g['status'],
                        excel_datetime(g['datetime']), g['score']] +
                       [partials.get(name, '') for name in ('1°Q', '2°Q', '3°Q', '4°Q', 'OT')] +
                       [len(g['players'])])
        for p in g['players']:
            stats.append([g['status'], excel_datetime(g['datetime'])] + [excel_datetime(p.get(key)) if key == 'Data' else p.get(key, '') for key in FIELDS])
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>'''
    styles = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><numFmts count="1"><numFmt numFmtId="164" formatCode="dd/mm/yyyy hh:mm"/></numFmts><fonts count="2"><font><sz val="11"/><name val="Aptos"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Aptos"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFB41F2B"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="1" borderId="0" xfId="0" applyFont="1" applyFill="1"/><xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>'''
    buf = BytesIO()
    with ZipFile(buf, 'w', ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr('xl/workbook.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Statistiche" sheetId="1" r:id="rId1"/><sheet name="Partite" sheetId="2" r:id="rId2"/></sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
        z.writestr('xl/styles.xml', styles)
        z.writestr('xl/worksheets/sheet1.xml', sheet_xml(stat_headers, stats))
        z.writestr('xl/worksheets/sheet2.xml', sheet_xml(match_headers, matches))
    return buf.getvalue()
