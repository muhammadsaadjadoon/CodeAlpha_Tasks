import argparse, json
from pathlib import Path
import numpy as np, pandas as pd, librosa, torch
from sklearn.metrics import classification_report, confusion_matrix
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

parser=argparse.ArgumentParser(); parser.add_argument("--model",default="ml/outputs/wav2vec2/champion"); parser.add_argument("--manifest",default="data/manifests/inflect.csv"); args=parser.parse_args()
extractor=AutoFeatureExtractor.from_pretrained(args.model); model=AutoModelForAudioClassification.from_pretrained(args.model).eval(); df=pd.read_csv(args.manifest); df=df[df.split=="test"]
y_true=[]; y_pred=[]
for row in df.itertuples():
    signal,_=librosa.load(row.path,sr=16000,mono=True); batch=extractor(signal,sampling_rate=16000,return_tensors="pt",truncation=True,max_length=128000)
    with torch.inference_mode(): pred=int(model(**batch).logits.argmax(-1))
    y_true.append(model.config.label2id[row.label]); y_pred.append(pred)
report=classification_report(y_true,y_pred,target_names=[model.config.id2label[i] for i in range(model.config.num_labels)],output_dict=True,zero_division=0)
print(json.dumps(report,indent=2)); print(confusion_matrix(y_true,y_pred))
