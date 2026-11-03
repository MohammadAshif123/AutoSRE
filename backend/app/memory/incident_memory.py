import os, json, hashlib
from datetime import datetime, timezone

class IncidentMemory:
    # Chroma is used when available. A small JSON fallback keeps the MVP runnable
    # in constrained environments while preserving the same retrieval interface.
    def __init__(self, path="./data/chroma"):
        self.path = path
        os.makedirs(path, exist_ok=True)
        self.fallback = os.path.join(path, "incidents.json")
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=path)
            self.collection = self.client.get_or_create_collection("incidents")
            self.chroma = True
        except Exception:
            self.chroma = False
            if not os.path.exists(self.fallback):
                open(self.fallback, "w", encoding="utf-8").write("[]")

    def _text(self, inc):
        return " ".join([
            inc.get("service",""), inc.get("symptom",""),
            inc.get("root_cause",""), " ".join(e.get("message","") for e in inc.get("evidence",[]))
        ])

    def add(self, incident):
        data = incident.model_dump() if hasattr(incident, "model_dump") else incident
        if self.chroma:
            doc = self._text(data)
            self.collection.upsert(
                ids=[data["id"]],
                documents=[doc],
                metadatas=[{
                    "service": data["service"],
                    "root_cause": data.get("root_cause") or "",
                    "action": data.get("action") or "",
                    "result": data.get("result") or "",
                    "recovery_succeeded": str(data.get("recovery_succeeded"))
                }]
            )
        else:
            items = json.loads(open(self.fallback, encoding="utf-8").read())
            items = [x for x in items if x["id"] != data["id"]]
            items.append(data)
            open(self.fallback, "w", encoding="utf-8").write(json.dumps(items, indent=2))

    def similar(self, incident, n=3):
        data = incident.model_dump() if hasattr(incident, "model_dump") else incident
        if self.chroma and self.collection.count():
            r = self.collection.query(query_texts=[self._text(data)], n_results=min(n, self.collection.count()))
            out=[]
            ids=(r.get("ids") or [[]])[0]
            metas=(r.get("metadatas") or [[]])[0]
            docs=(r.get("documents") or [[]])[0]
            for i, x in enumerate(ids):
                out.append({"id":x, "metadata": metas[i] if i < len(metas) else {}, "document": docs[i] if i < len(docs) else ""})
            return out
        items = json.loads(open(self.fallback, encoding="utf-8").read())
        words=set(self._text(data).lower().split())
        scored=[]
        for x in items:
            if x["id"] == data["id"]: continue
            score=len(words & set(self._text(x).lower().split()))
            scored.append((score,x))
        return [x for _,x in sorted(scored, reverse=True, key=lambda z:z[0])[:n]]
