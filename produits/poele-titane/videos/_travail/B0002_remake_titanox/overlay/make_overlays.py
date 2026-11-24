# Overlays PNG 1080x1920 (titre, mention) — Pillow, police Montserrat (OFL)
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D="/Users/youssef/AgentsAds/produits/poele-titane/videos/_travail/"
O=D+"B0002_remake_titanox/overlay/"
XB=ImageFont.truetype(D+"fonts/Montserrat-ExtraBold.ttf",53)
SB=ImageFont.truetype(D+"fonts/Montserrat-Bold.ttf",26)
# 1) Titre : bloc blanc x84-996 y399-656, 2 lignes centrées (mesures source x1.5)
t=Image.new("RGBA",(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(t)
d.rectangle((84,399,996,656),fill=(255,255,255,255))
for txt,cap_top in (("JE N'UTILISERAI PLUS JAMAIS",463),("DE POÊLES BON MARCHÉ",555)):
    # aligne le haut des capitales (sans accent) sur cap_top
    bb=d.textbbox((0,0),"H",font=XB); w=d.textlength(txt,font=XB)
    d.text(((1080-w)/2,cap_top-bb[1]),txt,font=XB,fill=(1,1,1,255))
t.save(O+"titre.png")
# 2) Mention « Images générées » : petit texte blanc, ombre, dans la zone sûre (bas droite, y<=1480)
m=Image.new("RGBA",(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(m)
txt="Images générées"; w=d.textlength(txt,font=SB); x=1000-w; y=1440
sh=Image.new("RGBA",(1080,1920),(0,0,0,0)); ImageDraw.Draw(sh).text((x+2,y+2),txt,font=SB,fill=(0,0,0,200))
sh=sh.filter(ImageFilter.GaussianBlur(2)); m=Image.alpha_composite(sh,m); d=ImageDraw.Draw(m)
d.text((x,y),txt,font=SB,fill=(255,255,255,235))
m.save(O+"mention.png"); print("ok", w)
