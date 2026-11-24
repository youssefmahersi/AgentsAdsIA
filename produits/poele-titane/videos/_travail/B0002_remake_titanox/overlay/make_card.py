# Carte de fin P6 (sans IA) : fond = image de NOTRE P5 floutée/zoomée, packshot photo 02 à la place du logo,
# bouton « COMMANDEZ MAINTENANT » #e11b22, pastille offre 59,99 € (#0c3358), mention « Images générées ».
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D="/Users/youssef/AgentsAds/produits/poele-titane/videos/_travail/"; O=D+"B0002_remake_titanox/overlay/"
bg_src=sys.argv[1]
XB=ImageFont.truetype(D+"fonts/Montserrat-ExtraBold.ttf",62)
PB=ImageFont.truetype(D+"fonts/Montserrat-ExtraBold.ttf",64)
SB=ImageFont.truetype(D+"fonts/Montserrat-Bold.ttf",26)
def elements():
    L=Image.new("RGBA",(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(L)
    # carte packshot (emprise du logo source : x273-810, y342-877)
    card=Image.new("RGBA",(537,537),(255,255,255,255))
    pk=Image.open("/Users/youssef/AgentsAds/produits/poele-titane/packshots/gemini/02-packshot-fond-blanc.webp").convert("RGB")
    pk=pk.crop((40,440,1960,1480)).resize((517,int(517*1040/1920)),Image.LANCZOS)
    card.paste(pk,(10,(537-pk.height)//2))
    mask=Image.new("L",(537,537),0); ImageDraw.Draw(mask).rounded_rectangle((0,0,536,536),36,fill=255)
    L.paste(card,(272,342),mask)
    # bouton (emprise source x215-866, y935-1145)
    d.rounded_rectangle((215,935,866,1145),14,fill=(0xe1,0x1b,0x22,255))
    for txt,y in (("COMMANDEZ",975),("MAINTENANT",1052)):
        bb=d.textbbox((0,0),txt,font=XB); w=bb[2]-bb[0]
        d.text(((1080-w)/2-bb[0],y-bb[1]+4),txt,font=XB,fill="white")
    # pastille offre (source : URL en bas, x192-888 ; remontée dans la zone sûre, bas <= 1440)
    d.rounded_rectangle((192,1290,888,1430),70,fill="white")
    txt="59,99 €"; bb=d.textbbox((0,0),txt,font=PB); w=bb[2]-bb[0]; h=bb[3]-bb[1]
    d.text(((1080-w)/2-bb[0],1360-h/2-bb[1]),txt,font=PB,fill=(0x0c,0x33,0x58,255))
    # mention
    t="Images générées"; tw=d.textlength(t,font=SB)
    d.text((1000-tw+2,1446),t,font=SB,fill=(0,0,0,150)); d.text((1000-tw,1444),t,font=SB,fill=(255,255,255,235))
    return L
E=elements(); E.save(O+"card_elements.png")
# fond flou : zoom 1.25 centré + flou
b=Image.open(bg_src).convert("RGB").resize((1080,1920))
b=b.resize((1350,2400),Image.LANCZOS).crop((135,240,1215,2160)).filter(ImageFilter.GaussianBlur(18))
Image.alpha_composite(b.convert("RGBA"),E).convert("RGB").save(O+"card_full.png")
# flash dégradé chaud (comme la source, ~0,17 s)
g=Image.new("RGB",(1080,1920)); gd=ImageDraw.Draw(g)
for y in range(1920):
    t=y/1919; c=(int(255),int(236-30*t),int(200-80*t)); gd.line((0,y,1079,y),fill=c)
Image.alpha_composite(g.convert("RGBA"),E).convert("RGB").save(O+"card_flash.png")
print("ok")
