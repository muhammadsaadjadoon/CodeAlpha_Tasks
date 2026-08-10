import argparse
from pathlib import Path
import sys, yaml, numpy as np, pandas as pd, librosa
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))
from datasets import Dataset, DatasetDict, Audio
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification, TrainingArguments, Trainer, EarlyStoppingCallback
from inflect_ml.labels import LABELS, LABEL2ID
from inflect_ml.metrics import classification_metrics

parser=argparse.ArgumentParser(); parser.add_argument("--config",default="ml/configs/default.yaml"); parser.add_argument("--manifest",default="data/manifests/inflect.csv"); args=parser.parse_args()
config=yaml.safe_load(Path(args.config).read_text()); df=pd.read_csv(args.manifest)
sets={split:Dataset.from_pandas(df[df.split==split][["path","label","dataset","speaker_id"]],preserve_index=False).cast_column("path",Audio(sampling_rate=config["sample_rate"])) for split in ["train","validation","test"]}
dataset=DatasetDict(sets); extractor=AutoFeatureExtractor.from_pretrained(config["model_name"])
def preprocess(batch):
    audio=batch["path"]; out=extractor(audio["array"],sampling_rate=audio["sampling_rate"],max_length=int(config["sample_rate"]*config["max_duration_seconds"]),truncation=True)
    out["labels"]=LABEL2ID[batch["label"]]; return out
dataset=dataset.map(preprocess,remove_columns=dataset["train"].column_names)
model=AutoModelForAudioClassification.from_pretrained(config["model_name"],num_labels=len(LABELS),label2id=LABEL2ID,id2label={v:k for k,v in LABEL2ID.items()},ignore_mismatched_sizes=True)
training_args=TrainingArguments(output_dir=config["output_dir"],learning_rate=config["learning_rate"],per_device_train_batch_size=config["batch_size"],per_device_eval_batch_size=config["eval_batch_size"],num_train_epochs=config["epochs"],weight_decay=config["weight_decay"],warmup_ratio=config["warmup_ratio"],eval_strategy="epoch",save_strategy="epoch",load_best_model_at_end=True,metric_for_best_model="macro_f1",greater_is_better=True,save_total_limit=2,logging_steps=25,report_to="none",seed=config["seed"])
trainer=Trainer(model=model,args=training_args,train_dataset=dataset["train"],eval_dataset=dataset["validation"],processing_class=extractor,compute_metrics=classification_metrics,callbacks=[EarlyStoppingCallback(config["patience"])])
trainer.train(); print(trainer.evaluate(dataset["test"],metric_key_prefix="test")); trainer.save_model(config["output_dir"]+"/champion"); extractor.save_pretrained(config["output_dir"]+"/champion")
