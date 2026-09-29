import json
sil=[(0,2.427),(10.611,11.344),(15.387,15.825),(19.197,19.928),(21.140,21.640),(23.009,23.683),(28.174,28.758),(28.984,29.993),(36.338,36.961),(40.834,41.351),(45.598,46.016),(50.269,50.901),(57.270,57.826),(59.432,59.854),(65.149,69.099)]
PAD_IN,PAD_OUT=0.10,0.15
keep=[];cur=0.0
for s,e in sil:
    a=cur; b=s+PAD_OUT
    if b-a>0.05: keep.append([round(a,3),round(b,3)])
    cur=max(e-PAD_IN,b)
keep=[[max(0,a),b] for a,b in keep if b-a>0.05]
json.dump(keep,open('cuts/cuts.json','w'),indent=1)
print(keep, sum(b-a for a,b in keep))
