import sys; sys.path.insert(0,'/home/claude')
from bvh import *
import numpy as np, json
def analyze(path):
    j,d,ft=parse(path); P,R=fk(j,d)
    N=len(d)
    # axis: walking direction
    dirv=P["Hips"][-1]-P["Hips"][0]; dirv[1]=0; dirv/=np.linalg.norm(dirv)
    up=np.array([0,1,0.]); side=np.cross(up,dirv)  # lateral (left positive?)
    def comp(v): return np.stack([v@dirv, v@up, v@side],-1)   # (fwd, up, lateral)
    L=lambda a,b: comp(P[a]-P[b])
    legLen=np.linalg.norm(P["LeftUpLeg"][0]-P["LeftLeg"][0])+np.linalg.norm(P["LeftLeg"][0]-P["LeftFoot"][0])
    hipw=np.linalg.norm(P["LeftUpLeg"][0]-P["RightUpLeg"][0]); shw=np.linalg.norm(P["LeftArm"][0]-P["RightArm"][0])
    def ang(v):   # angle from straight-down, + forward
        return np.degrees(np.arctan2(v[:,0],-v[:,1]))
    out={}
    for S,Sd in (("Left","L"),("Right","R")):
        th=L(S+"Leg",S+"UpLeg"); sh=L(S+"Foot",S+"Leg")
        out[Sd+"_thigh"]=ang(th); out[Sd+"_shank"]=ang(sh)
        ua=L(S+"ForeArm",S+"Arm"); fa=L(S+"Hand",S+"ForeArm")
        out[Sd+"_uarm"]=ang(ua); out[Sd+"_farm"]=ang(fa)
        out[Sd+"_foot_fwd"]=L(S+"Foot","Hips")[:,0]/legLen; out[Sd+"_foot_up"]=(P[S+"Foot"][:,1]-P[S+"Foot"][:,1].min())/legLen
    tr=L("Neck","Hips"); out["trunk_lean"]=np.degrees(np.arctan2(tr[:,0],tr[:,1]))
    sw=P["LeftArm"]-P["RightArm"]; hw=P["LeftUpLeg"]-P["RightUpLeg"]
    out["sh_tilt"]=np.degrees(np.arctan2(sw[:,1],hipw*0+shw)); out["hip_tilt"]=np.degrees(np.arctan2(hw[:,1],hipw))
    out["sh_yaw"]=np.degrees(np.arctan2(comp(sw)[:,0],shw)); out["hip_yaw"]=np.degrees(np.arctan2(comp(hw)[:,0],hipw))
    out["pelvis_up"]=(P["Hips"][:,1]-P["Hips"][:,1].mean())/legLen
    lat=comp(P["Hips"])[:,2]; out["pelvis_lat"]=(lat-np.convolve(lat,np.ones(120)/120,'same'))/legLen
    out["head_lean"]=np.degrees(np.arctan2(L("Head","Neck")[:,0],L("Head","Neck")[:,1]))
    # cycles: left foot forward-most (heel strike) = peak of L_foot_fwd
    f=out["L_foot_fwd"]; pk=[i for i in range(5,N-5) if f[i]==f[i-5:i+6].max() and f[i]>f.mean()]
    return out,pk,ft,legLen
def cycle_avg(path,n=12):
    out,pk,ft,ll=analyze(path)
    pk=[p for k,p in enumerate(pk) if k==0 or p-pk[k-1]>20]
    segs=[]
    for a,b in zip(pk[:-1],pk[1:]):
        segs.append((a,b))
    res={}
    for key,v in out.items():
        arr=[]
        for a,b in segs:
            x=np.linspace(a,b,n,endpoint=False); arr.append(np.interp(x,np.arange(len(v)),v))
        res[key]=np.mean(arr,0)
    T=np.mean([b-a for a,b in segs])*ft
    return res,T,len(segs)
if __name__=="__main__":
    for p in sys.argv[1:]:
        r,T,n=cycle_avg(p)
        print(p.split('/')[-1],"cycles",n,"period %.2fs"%T)
        for k,v in r.items(): print("%-11s"%k," ".join("%6.2f"%x for x in v))
