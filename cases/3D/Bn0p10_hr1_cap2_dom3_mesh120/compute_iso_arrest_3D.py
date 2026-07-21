#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D çeyrek-silindir iso-contour RADYAL run-out + YIELD-ARREST (2D compute_iso_arrest'in 3D genellemesi).
Mesh: NX x NY x NZ over (LX,LY,LZ); flat i = ix + iy*NX + iz*NX*NY.
  (1) r_iso(t): alpha=0.5 izoyüzeyinin max RADYAL konumu. x-ışınları (iy,iz sabit) ve y-ışınları (ix,iz sabit)
      boyunca alt-hücre interpolasyon; radial=sqrt(cross^2 + diğer_eksen^2); hepsi üzerinde max. (Dairesel cephe -> R verir.)
  (2) yield_count: akan hücre (alpha>0.5 & gammaDot>gammaMin); gammaDot=sqrt(2 S:S), S=symm(grad U) 3D numpy FD.
  arrest = yield_count ilk stabil sifir; r_iso(arrest) = yield-kesim.
Cikti: <case>/iso_arrest.csv (t,t_bar,r_iso,yield_count).
Kullanim: python3 compute_iso_arrest_3D.py <case_dir> <NX> <NY> <NZ> <LX> <LY> <LZ> <R0> <tc>
"""
import os, re, sys, csv
import numpy as np

GMIN = 1e-3
ATHR = 0.5

def read_field(path, ncomp, ncell):
    txt = open(path).read()
    i = txt.find('internalField'); seg = txt[i:]
    if 'nonuniform' not in seg:
        a = seg.find('uniform') + 7; b = seg.find(';', a)
        vals = seg[a:b].strip().lstrip('(').rstrip(')').split()
        if ncomp == 1: return np.full(ncell, float(vals[0]))
        return np.tile([float(x) for x in vals], (ncell, 1))
    p = seg.find('<'); lp = seg.find('\n', p); rest = seg[lp:]
    op = rest.find('('); cnt = int(rest[:op].strip().split()[-1]); cp = rest.find('\n)', op)
    body = rest[op+1:cp]
    if ncomp == 1:
        return np.fromstring(body.replace('\n', ' '), sep=' ')[:cnt]
    body = body.replace('(', ' ').replace(')', ' ')
    return np.fromstring(body, sep=' ')[:cnt*ncomp].reshape(cnt, ncomp)

def iso_radial(alpha, NX, NY, NZ, DX, DY, R0):
    a = alpha.reshape(NZ, NY, NX)  # [iz,iy,ix]
    xc = (np.arange(NX)+0.5)*DX; yc = (np.arange(NY)+0.5)*DY
    rmax = 0.0
    # x-isinlari: her (iz,iy) icin x boyunca en uzak alpha=0.5 gecisi
    for iz in range(NZ):
        for iy in range(NY):
            row = a[iz, iy]; ge = np.where(row >= 0.5)[0]
            if ge.size == 0: continue
            ix = ge.max()
            xcr = xc[ix] if ix >= NX-1 else (xc[ix] if row[ix]==row[ix+1] else xc[ix]+(0.5-row[ix])/(row[ix+1]-row[ix])*DX)
            r = (xcr*xcr + yc[iy]*yc[iy])**0.5
            if r > rmax: rmax = r
    # y-isinlari: her (iz,ix) icin y boyunca
    for iz in range(NZ):
        for ix in range(NX):
            col = a[iz, :, ix]; ge = np.where(col >= 0.5)[0]
            if ge.size == 0: continue
            iy = ge.max()
            ycr = yc[iy] if iy >= NY-1 else (yc[iy] if col[iy]==col[iy+1] else yc[iy]+(0.5-col[iy])/(col[iy+1]-col[iy])*DY)
            r = (xc[ix]*xc[ix] + ycr*ycr)**0.5
            if r > rmax: rmax = r
    return rmax / R0

def gammadot(U, NX, NY, NZ, DX, DY, DZ):
    Ux = U[:,0].reshape(NZ,NY,NX); Uy = U[:,1].reshape(NZ,NY,NX); Uz = U[:,2].reshape(NZ,NY,NX)
    # axis0=z, axis1=y, axis2=x
    dUxdx=np.gradient(Ux,DX,axis=2); dUxdy=np.gradient(Ux,DY,axis=1); dUxdz=np.gradient(Ux,DZ,axis=0)
    dUydx=np.gradient(Uy,DX,axis=2); dUydy=np.gradient(Uy,DY,axis=1); dUydz=np.gradient(Uy,DZ,axis=0)
    dUzdx=np.gradient(Uz,DX,axis=2); dUzdy=np.gradient(Uz,DY,axis=1); dUzdz=np.gradient(Uz,DZ,axis=0)
    Sxx=dUxdx; Syy=dUydy; Szz=dUzdz
    Sxy=0.5*(dUxdy+dUydx); Sxz=0.5*(dUxdz+dUzdx); Syz=0.5*(dUydz+dUzdy)
    g2 = Sxx**2+Syy**2+Szz**2 + 2*(Sxy**2+Sxz**2+Syz**2)
    return np.sqrt(2*g2).ravel()

def main():
    case=os.path.abspath(sys.argv[1])
    NX,NY,NZ=int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4])
    LX,LY,LZ=float(sys.argv[5]),float(sys.argv[6]),float(sys.argv[7])
    R0=float(sys.argv[8]); TC=float(sys.argv[9])
    DX,DY,DZ=LX/NX,LY/NY,LZ/NZ; n=NX*NY*NZ
    times=sorted(float(d) for d in os.listdir(case) if re.fullmatch(r'[\d.eE+-]+',d)
                 and os.path.isdir(os.path.join(case,d))
                 and os.path.exists(os.path.join(case,d,'U')) and os.path.exists(os.path.join(case,d,'alpha.mayo')))
    rows=[]
    for t in times:
        d=os.path.join(case, ('%d'%int(t)) if t==int(t) else repr(t))
        if not os.path.isdir(d):
            for nm in os.listdir(case):
                if os.path.isdir(os.path.join(case,nm)) and re.fullmatch(r'[\d.eE+-]+',nm) and float(nm)==t: d=os.path.join(case,nm); break
        try:
            alpha=read_field(os.path.join(d,'alpha.mayo'),1,n); U=read_field(os.path.join(d,'U'),3,n)
        except Exception as e:
            print('  [skip t=%g] %s'%(t,e)); continue
        r=iso_radial(alpha,NX,NY,NZ,DX,DY,R0)
        g=gammadot(U,NX,NY,NZ,DX,DY,DZ)
        yc=int(np.count_nonzero((alpha>ATHR)&(g>GMIN)))
        rows.append((t,t/TC,r,yc))
    rows.sort()
    with open(os.path.join(case,'iso_arrest.csv'),'w',newline='') as f:
        w=csv.writer(f); w.writerow(['t','t_bar','r_iso','yield_count']); w.writerows(rows)
    arr=None; seen=False
    for k,(t,tb,ri,yc) in enumerate(rows):
        if yc>0: seen=True
        elif seen and arr is None and t>0 and all(rows[j][3]==0 for j in range(k,min(k+3,len(rows)))): arr=(t,tb,ri)
    base=os.path.basename(case)
    if arr: print('%s: ARREST t_bar=%.0f (t=%.0f) r_iso=%.4f | raw_son=%.4f | 3D %dx%dx%d | tc=%.4f'%(base,arr[1],arr[0],arr[2],rows[-1][2],NX,NY,NZ,TC))
    else: print('%s: ARREST YOK | son yield=%d | raw_son=%.4f | 3D %dx%dx%d'%(base,rows[-1][3],rows[-1][2],NX,NY,NZ))

if __name__=='__main__': main()
