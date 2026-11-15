"""Draw the pseudo-localized windows figure.

Two windows show expanded en-XA text and mirrored ar-XB layout. The exported
`fig_localization` function returns the SVG string, drawn from the shared
`figuregen.palette` colours. `figuregen.cli` calls it to write
`fig-31-localization.svg` under `figures/`.
"""

from __future__ import annotations

from figuregen.canvas import para, svg_doc, txt
from figuregen.ornaments import title_block
from figuregen.palette import F_DISPLAY, F_MONO, OXIDE, PINE2, SOFT
from figuregen.widgets import button, window_shell


def fig_localization() -> str:
    """Draw pseudo-localized left-to-right and right-to-left windows.

    Returns
    -------
    str
    """
    body = title_block(
        64,
        70,
        "Language is not a later coat of paint",
        "Pseudo-locales expose hard-coded widths, concatenated strings and left-to-right assumptions before translation begins.",
    )
    # LTR expanded.
    x, y, w, h = 64, 160, 480, 340
    body += txt(
        x,
        150,
        "EN-XA · +35% MINIMUM",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += window_shell(
        x,
        y,
        w,
        h,
        title="Facet Notes — ⟦Ŵöŕļď ťŕáńšîťîöń ··⟧",
        menu=["⟦Fîļé⟧", "⟦Édîť⟧", "⟦Vîéŵ⟧", "⟦Héļþ⟧"],
        status="⟦Ŝávéď · 3 émбédš ····⟧",
        state="Current",
    )
    body += txt(
        x + 22,
        y + 96,
        "⟦Ťŕáńšîťîöń þáťĥŵáýš ···⟧",
        size=20,
        family=F_DISPLAY,
        style="italic",
    )
    body += para(
        x + 22,
        y + 124,
        w - 44,
        "⟦Ťĥé ťŕáńšîťîöń îš ńöť öńé déçîšîöń бůť á šéqůéńçé öf šмáļļ öńéš. ······⟧",
        size=11,
        leading=17,
    )
    body += button(x + 22, y + 216, 190, "⟦Éхþöŕť áš PDF ·⟧", primary=True, height=36)
    body += button(x + 224, y + 218, 130, "⟦Çáńçéļ ·⟧", height=32)
    body += txt(
        x + 22,
        y + 292,
        "Controls grow; labels do not clip.",
        size=10,
        fill=OXIDE,
        family=F_MONO,
    )
    # RTL mirrored.
    x2 = 656
    body += txt(
        x2,
        150,
        "AR-XB · MIRRORED",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    body += window_shell(
        x2,
        y,
        480,
        h,
        title="مفكرة الأوجه — انتقال بحر الشمال",
        menu=["ملف", "تحرير", "عرض", "مساعدة"],
        status="محفوظ · ٣ كائنات",
        state="Current",
        rtl=True,
    )
    body += txt(
        x2 + w - 22,
        y + 96,
        "انتقال بحر الشمال",
        size=20,
        family=F_DISPLAY,
        style="italic",
        anchor="end",
    )
    body += para(
        x2 + w - 22,
        y + 124,
        w - 44,
        "الانتقال ليس قراراً واحداً بل سلسلة من القرارات الصغيرة. يبقى كل مصدر قابلاً للتحرير، ويحتفظ كل كائن بهويته.",
        size=11,
        leading=17,
        anchor="end",
    )
    body += button(x2 + w - 182, y + 214, 160, "تصدير PDF", primary=True, height=38)
    body += button(x2 + w - 324, y + 214, 130, "إلغاء", height=38)
    body += txt(
        x2 + w - 22,
        y + 284,
        "تنتقل الواجهة كاملة إلى اليمين.",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        anchor="end",
    )
    # Notes.
    body += txt(
        64,
        552,
        "WHAT THE PSEUDO-LOCALES CATCH",
        size=10,
        fill=OXIDE,
        family=F_MONO,
        weight="bold",
        spacing=1,
    )
    notes = [
        ("en-XA", "Expanded accents reveal clipped labels and fixed-width buttons."),
        (
            "ar-XB",
            "Mirrored layout reveals panes, icons and reading order that assume left-to-right.",
        ),
        (
            "Numbers",
            "Digits, dates and currency are formatted by locale, never assembled from strings.",
        ),
        ("Strings", "Full sentences are resources. Fragments are not concatenated."),
    ]
    for index, (name, detail) in enumerate(notes):
        nx = 64 + index * 270
        body += txt(
            nx, 582, name.upper(), size=10, fill=PINE2, family=F_MONO, weight="bold"
        )
        body += para(nx, 602, 246, detail, size=11, leading=16)
    body += txt(
        64,
        704,
        "A localized build is a gate, not a screenshot. The pseudo-locales run in the same export bundle as the default language.",
        size=11,
        fill=SOFT,
    )
    return svg_doc(
        1200,
        760,
        "Pseudo-localized left-to-right and right-to-left windows",
        "Two windows showing expanded en-XA text and mirrored ar-XB layout, with notes on what the pseudo-locales test.",
        body=body,
    )
