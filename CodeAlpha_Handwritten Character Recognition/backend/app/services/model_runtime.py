from functools import lru_cache
from pathlib import Path
import json
import numpy as np
import torch
from .image_preprocessing import ProcessedCharacter
from ..config import settings

ROOT = Path(__file__).resolve().parents[3]

class ModelRuntime:
    def __init__(self):
        self._loaded: dict[str, tuple[torch.jit.ScriptModule, dict]] = {}

    def _registry(self) -> dict:
        path = (ROOT / settings.model_registry_path).resolve() if not Path(settings.model_registry_path).is_absolute() else Path(settings.model_registry_path)
        if not path.exists(): return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _resolve(self, value: str) -> Path:
        path=Path(value)
        return path if path.is_absolute() else ROOT/path

    def load(self, role: str):
        registry=self._registry(); entry=registry.get(role)
        if not entry: raise RuntimeError(f"No model is registered for role '{role}'.")
        checkpoint=self._resolve(entry["checkpoint"]); metadata_path=self._resolve(entry["metadata"])
        if not checkpoint.exists() or not metadata_path.exists():
            raise RuntimeError(f"The {entry.get('name', role)} checkpoint has not been trained yet.")
        cache_key=f"{role}:{checkpoint.stat().st_mtime_ns}:{metadata_path.stat().st_mtime_ns}"
        if cache_key not in self._loaded:
            model=torch.jit.load(str(checkpoint), map_location="cpu").eval()
            metadata=json.loads(metadata_path.read_text(encoding="utf-8"))
            self._loaded={k:v for k,v in self._loaded.items() if not k.startswith(role+":")}
            self._loaded[cache_key]=(model,metadata)
        return self._loaded[cache_key]

    def predict(self, processed: ProcessedCharacter, role: str) -> dict:
        model,meta=self.load(role)
        tensor=torch.from_numpy(processed.tensor)
        with torch.inference_mode():
            logits=model(tensor)
            probs=torch.softmax(logits,dim=1)[0]
        top_prob,top_idx=torch.topk(probs,min(5,probs.numel()))
        classes=[str(x) for x in meta["classes"]]
        distribution=[{"label":classes[int(i)],"probability":float(p)} for p,i in zip(top_prob,top_idx)]
        return {"primary_label":distribution[0]["label"],"confidence":distribution[0]["probability"],"distribution":distribution,"model_version":meta.get("model_version",meta.get("name","unknown"))}

    def status(self) -> dict:
        result={}
        for role,entry in self._registry().items():
            cp=self._resolve(entry["checkpoint"]); md=self._resolve(entry["metadata"]); metrics=self._resolve(entry.get("metrics","")) if entry.get("metrics") else None
            result[role]={"name":entry.get("name",role),"ready":cp.exists() and md.exists(),"checkpoint":str(cp.relative_to(ROOT)) if cp.is_relative_to(ROOT) else str(cp),"metrics_available":bool(metrics and metrics.exists())}
        return result

    def metrics(self) -> dict:
        output={}
        for role,entry in self._registry().items():
            if not entry.get("metrics"): continue
            path=self._resolve(entry["metrics"])
            if path.exists(): output[role]=json.loads(path.read_text(encoding="utf-8"))
        return output

runtime=ModelRuntime()
