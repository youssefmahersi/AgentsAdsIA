# Bande son 100 % synthétisée (aucun échantillon externe, aucun son de la source) : ding, grésillement, plops, spatule, whoosh, atterrissage.
import numpy as np, wave, sys
SR=48000; DUR=11.367; N=int(SR*DUR); rng=np.random.default_rng(7)
t=np.arange(N)/SR; out=np.zeros(N)
def env_at(start,length,attack=0.005,decay=None):
    e=np.zeros(N); i0=int(start*SR); n=int(length*SR); n=min(n,N-i0)
    tt=np.arange(n)/SR; a=np.minimum(1,tt/attack)
    d=np.exp(-tt/decay) if decay else np.ones(n)
    e[i0:i0+n]=a*d; return e
def bandnoise(lo,hi,n=N):
    x=rng.standard_normal(n); X=np.fft.rfft(x); f=np.fft.rfftfreq(n,1/SR)
    X[(f<lo)|(f>hi)]=0; y=np.fft.irfft(X,n); return y/np.max(np.abs(y))
# 1) ding à 0,10 s (cloche douce)
dg=np.zeros(N)
for fr,amp,dec in ((1318.5,1.0,0.9),(2637,0.45,0.5),(3955,0.2,0.3),(5274,0.08,0.2)):
    dg+=amp*np.sin(2*np.pi*fr*t)*env_at(0.10,2.0,0.003,dec)
out+=0.35*dg
# 2) grésillement : bruit 2-9 kHz modulé par crépitements aléatoires
siz=bandnoise(2000,9000); crack=np.zeros(N)
for k in range(int(DUR*60)):
    p=rng.uniform(0,DUR); crack+=rng.uniform(0.3,1.0)*env_at(p,0.03,0.001,0.006)
mod=0.35+0.65*np.clip(np.convolve(crack,np.ones(48)/48,'same')*8,0,1.5)
lvl=np.interp(t,[0,0.5,1.0,3.13,5.6,7.2,9.63,10.23,10.6,DUR],[0,0.02,0.10,0.22,0.24,0.2,0.24,0.22,0.06,0.04])
out+=siz*mod*lvl
# 3) œufs qui tombent dans la poêle (P1) : plop grave + bouffée de grésillement
low=bandnoise(80,500)
for p in (0.85,1.25,1.45,1.70,1.90,2.10,2.35,2.60):
    out+=0.25*low*env_at(p,0.25,0.004,0.05)+0.18*siz*env_at(p+0.02,0.5,0.01,0.2)
# 4) spatule qui glisse (P2, 3,5-5,4 s)
scr=bandnoise(900,3500); out+=0.10*scr*np.interp(t,[3.4,3.7,5.2,5.5],[0,1,1,0],left=0,right=0)*(0.6+0.4*np.sin(2*np.pi*7*t))
# 5) glissement de la galette (P3, 5,7-7,1 s)
out+=0.07*bandnoise(300,1500)*np.interp(t,[5.7,6.0,6.9,7.15],[0,1,1,0],left=0,right=0)
# 6) whoosh du retournement (P4) : balayage de bande 8,0-8,5 s
wh=np.zeros(N); i0=int(8.0*SR); n=int(0.55*SR); seg=rng.standard_normal(n)
fc=np.linspace(400,2500,n); 
# filtre simple : passe-bande glissant par blocs
bs=1024
for b in range(0,n,bs):
    blk=seg[b:b+bs]; X=np.fft.rfft(blk,bs); f=np.fft.rfftfreq(bs,1/SR); c=fc[min(b,n-1)]
    X*=np.exp(-((f-c)/(c*0.6))**2); wh[i0+b:i0+b+len(blk)]=np.fft.irfft(X,bs)[:len(blk)]
wh/=np.max(np.abs(wh)); wh*=np.sin(np.linspace(0,np.pi,N))*0+1
out+=0.35*wh*np.interp(t,[8.0,8.25,8.55],[0,1,0],left=0,right=0)
# 7) atterrissage (≈8,85 s) : flop + grésillement
out+=0.45*low*env_at(8.85,0.3,0.003,0.06)+0.25*siz*env_at(8.87,0.8,0.01,0.3)
# stéréo légère
L=out+0.002*rng.standard_normal(N); R=np.roll(out,int(0.0004*SR))
st=np.stack([L,R],1); st/=np.max(np.abs(st))*1.12
pcm=(st*32767).astype(np.int16)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close(); print("ok")
