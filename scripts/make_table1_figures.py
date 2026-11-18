#!/usr/bin/env python3
"""Render Table 1 schedule and timing figures as dependency-free SVG files."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / 'results/processed/summary.csv'
OUT_DIR = ROOT / 'results/figures'

PAPER = {
    'CVE-2016-7911': {'schedules_to_first_bug': 3, 'total_schedules': 19,
                      'buggy_schedules': 8},
    'CVE-2016-9806': {'schedules_to_first_bug': 6, 'total_schedules': 42,
                      'buggy_schedules': 4},
    'CVE-2017-15265': {'schedules_to_first_bug': 11, 'total_schedules': 96,
                       'buggy_schedules': 1},
}
COMBOS = [('period', 'CVE-2016-7911'), ('serial', 'CVE-2016-7911'),
          ('period', 'CVE-2016-9806'), ('serial', 'CVE-2016-9806'),
          ('period', 'CVE-2017-15265')]
COLORS = {'period': '#2b6cb0', 'serial': '#c05621'}
PAPER_COLOR = '#4a5568'
METRICS = [('schedules_to_first_bug', 'Schedules to first bug', 13),
           ('total_schedules', 'Total schedules', 105),
           ('buggy_schedules', 'Buggy schedules', 9)]


def load():
    rows = {}
    with SUMMARY.open(encoding='utf-8', newline='') as handle:
        for row in csv.DictReader(handle):
            rows[(row['mode'], row['benchmark'], row['metric'])] = row
    return rows


def esc(text):
    return (text.replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


def schedule_svg(rows):
    width, height = 1220, 760
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
             'viewBox="0 0 %d %d">' % (width, height, width, height),
             '<rect width="100%" height="100%" fill="#ffffff"/>',
             '<text x="60" y="40" font-family="Arial, Helvetica, sans-serif" '
             'font-size="22" font-weight="bold" fill="#1a202c">'
             'Table 1 schedule metrics: paper vs. local scoped runs</text>',
             '<text x="60" y="66" font-family="Arial, Helvetica, sans-serif" '
             'font-size="13" fill="#4a5568">'
             'Bars: local mean; error bars: sample SD (n-1); dashed line: paper value. '
             'Labels show n. Serial/15265 excluded.</text>']
    # legend
    parts.append('<rect x="60" y="80" width="14" height="14" fill="%s"/>' % COLORS['period'])
    parts.append('<text x="80" y="92" font-family="Arial" font-size="13">Period (ours)</text>')
    parts.append('<rect x="200" y="80" width="14" height="14" fill="%s"/>' % COLORS['serial'])
    parts.append('<text x="220" y="92" font-family="Arial" font-size="13">Serial (ours)</text>')
    parts.append('<line x1="340" y1="87" x2="380" y2="87" stroke="%s" stroke-width="2" '
                 'stroke-dasharray="6,4"/>' % PAPER_COLOR)
    parts.append('<text x="388" y="92" font-family="Arial" font-size="13">paper</text>')

    panel_w, panel_h, top = 350, 480, 140
    for panel, (metric, title, maxv) in enumerate(METRICS):
        x0 = 60 + panel * (panel_w + 30)
        y0 = top
        parts.append('<text x="%d" y="%d" font-family="Arial" font-size="16" '
                     'font-weight="bold">%s</text>' % (x0, y0 - 16, esc(title)))
        # axes and grid
        parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#cbd5e0"/>'
                     % (x0, y0, x0, y0 + panel_h))
        parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#cbd5e0"/>'
                     % (x0, y0 + panel_h, x0 + panel_w, y0 + panel_h))
        for tick in range(0, maxv + 1, max(1, maxv // 5)):
            ty = y0 + panel_h - tick / maxv * panel_h
            parts.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#edf2f7"/>'
                         % (x0, ty, x0 + panel_w, ty))
            parts.append('<text x="%d" y="%.1f" font-family="Arial" font-size="10" '
                         'text-anchor="end" fill="#4a5568">%d</text>'
                         % (x0 - 6, ty + 3, tick))
        n_bars = len(COMBOS)
        bar_w = 38
        gap = (panel_w - n_bars * bar_w) / (n_bars + 1)
        for index, (method, case) in enumerate(COMBOS):
            row = rows[(method, case, metric)]
            mean = float(row['mean'])
            sd = float(row['stddev'])
            n = int(row['n'])
            bx = x0 + gap + index * (bar_w + gap)
            bh = mean / maxv * panel_h
            by = y0 + panel_h - bh
            parts.append('<rect x="%.1f" y="%.1f" width="%d" height="%.1f" fill="%s" '
                         'opacity="0.9"/>' % (bx, by, bar_w, bh, COLORS[method]))
            if sd > 0:
                ey = sd / maxv * panel_h
                parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1a202c" '
                             'stroke-width="1.5"/>' % (bx + bar_w / 2, by - ey,
                                                       bx + bar_w / 2, by + ey))
                parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1a202c" '
                             'stroke-width="1.5"/>' % (bx + bar_w / 2 - 5, by - ey,
                                                       bx + bar_w / 2 + 5, by - ey))
                parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1a202c" '
                             'stroke-width="1.5"/>' % (bx + bar_w / 2 - 5, by + ey,
                                                       bx + bar_w / 2 + 5, by + ey))
            if (method, case) in [('period', 'CVE-2016-7911'), ('serial', 'CVE-2016-7911'),
                                  ('period', 'CVE-2016-9806'), ('serial', 'CVE-2016-9806'),
                                  ('period', 'CVE-2017-15265')]:
                paper = PAPER[case][metric]
                py = y0 + panel_h - paper / maxv * panel_h
                parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                             'stroke-width="2" stroke-dasharray="6,4"/>'
                             % (bx - 2, py, bx + bar_w + 2, py, PAPER_COLOR))
            parts.append('<text x="%.1f" y="%.1f" font-family="Arial" font-size="10" '
                         'text-anchor="middle" fill="#1a202c">%s</text>'
                         % (bx + bar_w / 2, y0 + panel_h + 18, case.split('-')[-1]))
            parts.append('<text x="%.1f" y="%.1f" font-family="Arial" font-size="10" '
                         'text-anchor="middle" fill="#4a5568">%s n=%d</text>'
                         % (bx + bar_w / 2, y0 + panel_h + 33, method[0].upper(), n))
    parts.append('<text x="60" y="720" font-family="Arial" font-size="11" fill="#4a5568">'
                 'Source: results/processed/summary.csv; scripts/make_table1_figures.py. '
                 'Paper values: Table 1, p.8 (Period/Serial combined column). '
                 'Serial/CVE-2017-15265 is excluded; see the evidence README.</text>')
    parts.append('</svg>')
    return '\n'.join(parts)


def time_svg(rows):
    width, height = 760, 480
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
             'viewBox="0 0 %d %d">' % (width, height, width, height),
             '<rect width="100%" height="100%" fill="#ffffff"/>',
             '<text x="60" y="40" font-family="Arial" font-size="21" font-weight="bold" '
             'fill="#1a202c">Tool time (descriptive only)</text>',
             '<text x="60" y="66" font-family="Arial" font-size="12" fill="#4a5568">'
             'Mean tool elapsed seconds; error bars: sample SD (n-1). The paper does not '
             'report these times; hosts differ.</text>']
    x0, y0, panel_w, panel_h, maxv = 80, 120, 620, 260, 12
    parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#cbd5e0"/>'
                 % (x0, y0, x0, y0 + panel_h))
    parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#cbd5e0"/>'
                 % (x0, y0 + panel_h, x0 + panel_w, y0 + panel_h))
    for tick in range(0, maxv + 1, 2):
        ty = y0 + panel_h - tick / maxv * panel_h
        parts.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#edf2f7"/>'
                     % (x0, ty, x0 + panel_w, ty))
        parts.append('<text x="%d" y="%.1f" font-family="Arial" font-size="10" '
                     'text-anchor="end" fill="#4a5568">%d</text>' % (x0 - 6, ty + 3, tick))
    bar_w = 60
    gap = (panel_w - len(COMBOS) * bar_w) / (len(COMBOS) + 1)
    for index, (method, case) in enumerate(COMBOS):
        row = rows[(method, case, 'tool_elapsed_seconds')]
        mean = float(row['mean'])
        sd = float(row['stddev'])
        n = int(row['n'])
        bx = x0 + gap + index * (bar_w + gap)
        bh = mean / maxv * panel_h
        by = y0 + panel_h - bh
        parts.append('<rect x="%.1f" y="%.1f" width="%d" height="%.1f" fill="%s" '
                     'opacity="0.9"/>' % (bx, by, bar_w, bh, COLORS[method]))
        if sd > 0:
            ey = sd / maxv * panel_h
            parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1a202c" '
                         'stroke-width="1.5"/>' % (bx + bar_w / 2, by - ey,
                                                   bx + bar_w / 2, by + ey))
            parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1a202c" '
                         'stroke-width="1.5"/>' % (bx + bar_w / 2 - 6, by - ey,
                                                   bx + bar_w / 2 + 6, by - ey))
            parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1a202c" '
                         'stroke-width="1.5"/>' % (bx + bar_w / 2 - 6, by + ey,
                                                   bx + bar_w / 2 + 6, by + ey))
        parts.append('<text x="%.1f" y="%.1f" font-family="Arial" font-size="10" '
                     'text-anchor="middle">%s %s</text>'
                     % (bx + bar_w / 2, y0 + panel_h + 18, method[0].upper(),
                        case.split('-')[-1]))
        parts.append('<text x="%.1f" y="%.1f" font-family="Arial" font-size="10" '
                     'text-anchor="middle" fill="#4a5568">n=%d</text>'
                     % (bx + bar_w / 2, y0 + panel_h + 33, n))
    parts.append('<text x="60" y="450" font-family="Arial" font-size="11" fill="#4a5568">'
                 'Source: results/processed/summary.csv; scripts/make_table1_figures.py. '
                 'Timing is not part of the paper table and is not used to claim speed.</text>')
    parts.append('</svg>')
    return '\n'.join(parts)


def main():
    rows = load()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / 'table1-schedules.svg').write_text(schedule_svg(rows), encoding='utf-8')
    (OUT_DIR / 'table1-time.svg').write_text(time_svg(rows), encoding='utf-8')
    print('Wrote table1-schedules.svg and table1-time.svg')


if __name__ == '__main__':
    main()
