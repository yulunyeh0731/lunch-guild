"""v2.2 食物圖示改版：24 個圖示改成 32×32 重畫版（原始碼 foodhd.py，產出 food32.json）。
- FOOD／FPAL 換成 32×32 的列字串＋dict 調色盤（draw() 本來就支援 dict 調色盤）
- 「熱炒」(wok) 換成「甜點」(dessert)；熱炒的關鍵字分給自助餐／便當／麵店
- 加甜點關鍵字
改圖：改 foodhd.py → python3 foodhd.py → 重產 food32.json（見 CHANGELOG v2.2）→ build_index.py"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))


def _swap(h, name, obj):
    pat = re.compile(r'^const %s=\{.*\};$' % name, re.M)
    assert len(pat.findall(h)) == 1, name
    return pat.sub(lambda m: 'const %s=%s;' % (name, json.dumps(obj, ensure_ascii=False)), h, 1)


def _get(h, name):
    m = re.search(r'^const %s=(\{.*\});$' % name, h, re.M)
    return json.loads(m.group(1))


def apply(h):
    d = json.load(open(os.path.join(HERE, 'food32.json'), encoding='utf-8'))
    h = _swap(h, 'FOOD', d['FOOD'])
    h = _swap(h, 'FPAL', d['FPAL'])
    label = _get(h, 'LABEL')
    label = {('dessert' if k == 'wok' else k): ('甜點' if k == 'wok' else v) for k, v in label.items()}
    h = _swap(h, 'LABEL', label)
    g = _get(h, 'GUESS')
    g.pop('wok', None)
    g['buffet'] += ['熱炒', '快炒', '合菜', '客飯', '小吃']
    g['bento'] += ['炒飯', '燴飯']
    g['twnoodle'] += ['炒麵', '羹']
    g['dessert'] = ['甜點', '蛋糕', '甜品', '豆花', '鬆餅', '布丁', '甜甜圈', '烘焙', '麵包', '剉冰', '雪花冰', '冰店', '下午茶', '可麗餅', '舒芙蕾', 'dessert', 'cake']
    h = _swap(h, 'GUESS', g)
    h = h.replace("const ALIAS = { hotpot: 'feast',", "const ALIAS = { wok: 'buffet', hotpot: 'feast',", 1)
    assert "wok: 'buffet'" in h
    return h
