import sys, colorsys
from PIL import Image
def dom(im, box, k=4):
    c = im.crop(box).convert('RGB')
    q = c.quantize(colors=k, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:3*k]; counts = sorted(q.getcolors(), reverse=True)
    tot = sum(n for n, _ in counts); out = []
    for n, i in counts:
        r, g, b = pal[3*i:3*i+3]
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        out.append(f"#{r:02x}{g:02x}{b:02x}({100*n/tot:.0f}%,L{l*100:.0f})")
    return ' '.join(out)
f = 0.7
regions = {
 'A': [
  ('WS5 fasada (Wybrzeże Słowackiego 5)', (690,560,765,635)),
  ('Mazowiecka – dachy (czerwone)', (430,505,610,520)),
  ('Mazowiecka – fasady', (430,525,610,558)),
  ('Długi biały blok po lewej (zespół UMWD?)', (30,580,400,655)),
  ('DUW dach', (1060,425,1250,468)),
  ('DUW fasada', (1060,480,1250,525)),
  ('Pylon mostu (bliski)', (1490,620,1550,715)),
  ('Kratownica mostu', (1150,600,1440,670)),
  ('Ostrów Tumski (cegła/dachy)', (1440,340,1570,410)),
  ('Odra – woda', (600,820,1000,950)),
  ('Drzewa jesienne (lewy brzeg)', (40,720,300,830)),
 ],
 'B': [
  ('DUW fasada', (60,520,470,630)),
  ('DUW dach', (60,450,470,505)),
  ('Mazowiecka 17 fasada', (1560,760,1950,900)),
  ('Mazowiecka 17 dach (dachówka)', (1520,600,1950,690)),
  ('Mazowiecka 17 parter/cokół', (1700,900,1950,1000)),
  ('Mazowiecka 19 fasada', (1320,610,1470,800)),
  ('WS5 (tył, nad Oławą)', (1340,470,1720,540)),
  ('Pylon mostu', (765,430,880,525)),
  ('Kratownica/cięgna mostu', (890,400,1040,470)),
  ('Mur nabrzeża (prawy brzeg Odry)', (1060,445,1320,470)),
  ('Manhattan (pl. Grunwaldzki)', (910,300,1120,380)),
  ('Trawa – teren', (1000,800,1300,980)),
  ('Odra – woda', (1100,480,1300,525)),
 ]}
for key, path in [('A', sys.argv[1]), ('B', sys.argv[2])]:
    im = Image.open(path)
    print('==', key, im.size)
    for name, b in regions[key]:
        bb = tuple(int(v*f) for v in b)
        print(f"{name:45s} {dom(im, bb)}")
