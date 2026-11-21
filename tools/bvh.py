import numpy as np, re
def parse(path):
    toks=open(path).read().split('\n')
    joints=[];stack=[];ch=[];off={}
    i=0;name=None
    while i<len(toks):
        l=toks[i].strip()
        if l.startswith(("ROOT","JOINT")):
            name=l.split()[1]; joints.append(dict(name=name,parent=stack[-1] if stack else None,off=None,ch=[]))
        elif l.startswith("End Site"):
            stack.append(None) ; i+=1  # '{'
            # skip End Site block
            i+=2; # OFFSET line then '}'
            stack.pop(); i+=1; continue
        elif l.startswith("OFFSET"):
            joints[-1]["off"]=np.array(l.split()[1:4],float)
        elif l.startswith("CHANNELS"):
            p=l.split(); joints[-1]["ch"]=p[2:]
        elif l=="{": stack.append(joints[-1]["name"])
        elif l=="}": stack.pop()
        elif l.startswith("MOTION"):
            break
        i+=1
    n=int(toks[i+1].split()[1]); ft=float(toks[i+2].split()[2])
    data=np.array([[float(v) for v in toks[i+3+k].split()] for k in range(n)])
    return joints,data,ft
def rot(ax,a):
    c,s=np.cos(a),np.sin(a)
    if ax=='X': return np.array([[1,0,0],[0,c,-s],[0,s,c]])
    if ax=='Y': return np.array([[c,0,s],[0,1,0],[-s,0,c]])
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def fk(joints,data):
    idx={j["name"]:k for k,j in enumerate(joints)}
    N=len(data); P={j["name"]:np.zeros((N,3)) for j in joints}; R={}
    col=0; cols={}
    for j in joints:
        cols[j["name"]]=col; col+=len(j["ch"])
    for f in range(N):
        Rw={}
        for j in joints:
            nm=j["name"]; c=cols[nm]; vals=data[f,c:c+len(j["ch"])]
            pos=np.zeros(3); Rl=np.eye(3)
            for chn,v in zip(j["ch"],vals):
                if chn.endswith("position"): pos["XYZ".index(chn[0])]=v
                else: Rl=Rl@rot(chn[0],np.deg2rad(v))
            if j["parent"] is None:
                Rw[nm]=Rl; P[nm][f]=pos
            else:
                pr=j["parent"]; Rw[nm]=Rw[pr]@Rl; P[nm][f]=P[pr][f]+Rw[pr]@j["off"]
        R[f]=Rw
    return P,R
