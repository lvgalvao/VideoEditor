import json
W=json.load(open('assets/words_clean.json'))
sfx=[(0.0,'whoosh'),(3.0,'whoosh'),(3.3,'pop'),(3.9,'pop'),(4.5,'pop'),(5.7,'pop'),(6.3,'thump'),(8.5,'whoosh'),
(9.2,'pop'),(10.15,'pop'),(10.62,'pop'),(11.55,'ding'),(12.8,'whoosh'),(17.85,'pop'),(18.6,'pop'),(19.5,'whoosh'),
(20.6,'pop'),(21.3,'pop'),(22.0,'pop'),(24.15,'thump'),(26.15,'whoosh'),(29.25,'pop'),(30.85,'pop'),(31.85,'pop'),
(32.55,'pop'),(33.35,'pop'),(34.95,'whoosh'),(37.1,'pop'),(41.1,'thump'),(43.8,'whoosh'),(44.6,'whoosh'),(45.2,'ding'),
(47.25,'pop'),(49.0,'pop'),(50.55,'thump'),(52.45,'whoosh'),(55.0,'whoosh')]
vol={'whoosh':0.22,'pop':0.3,'ding':0.18,'thump':0.5}
dur={'whoosh':0.45,'pop':0.12,'ding':0.5,'thump':0.5}
tags='\n      '.join(f'<audio id="sfx{i}" src="assets/{n}.wav" data-start="{t}" data-duration="{dur[n]}" data-track-index="{3+i%3}" data-volume="{vol[n]}"></audio>' for i,(t,n) in enumerate(sfx))
h=open('../composition_template.html').read().replace('__WORDS__',json.dumps(W,ensure_ascii=False)).replace('__SFX__',tags)
open('index.html','w').write(h)
