"""v2.1 換上新選單圖示（ui34.NAV_ICONS）與小改過的頭像（portfix）。build_index.py 在 layout203 之後呼叫 apply(h)。"""
import json, re

PORTRAITS = False    # 頭像小改：使用者確認後打開


def _grab(h, name):
    m = re.search(r'const %s\s*=\s*' % name, h)
    j = m.end(); depth = 0; k = j
    while True:
        c = h[k]
        if c in '{[': depth += 1
        elif c in '}]':
            depth -= 1
            if depth == 0: break
        k += 1
    return j, k + 1, json.loads(h[j:k + 1])


def _put(h, name, obj):
    j, k, _ = _grab(h, name)
    return h[:j] + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + h[k:]


def apply(h):
    import ui34
    _, _, icon = _grab(h, 'ICON')
    for k, f in ui34.NAV_ICONS.items():
        icon[k] = f()
    h = _put(h, 'ICON', icon)
    if PORTRAITS:
        import portfix
        _, _, P = _grab(h, 'PORTRAIT'); _, _, PP = _grab(h, 'PPAL')
        P, PP = portfix.apply(P, PP)
        h = _put(h, 'PORTRAIT', P); h = _put(h, 'PPAL', PP)
    return h
