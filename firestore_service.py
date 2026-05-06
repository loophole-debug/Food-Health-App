import os
from google.cloud import firestore
import datetime

class FirestoreService:
    def __init__(self):
        project_id = os.getenv("GCP_PROJECT_ID")
        self.db = firestore.AsyncClient(project=project_id) if project_id else firestore.AsyncClient()

    async def save_context(self, user_id: str, context_data: dict) -> str:
        doc_ref = self.db.collection('users').document(user_id).collection('contexts').document()
        context_data['timestamp'] = firestore.SERVER_TIMESTAMP
        await doc_ref.set(context_data)
        return doc_ref.id

    async def save_nudge(self, user_id: str, nudge_text: str, context_data: dict) -> str:
        doc_ref = self.db.collection('users').document(user_id).collection('nudges').document()
        await doc_ref.set({
            'nudge_text': nudge_text,
            'context': context_data,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'helpful': None
        })
        return doc_ref.id

    async def get_history(self, user_id: str, limit: int = 10) -> list:
        nudges_ref = self.db.collection('users').document(user_id).collection('nudges')
        query = nudges_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
        docs = query.stream()
        
        history = []
        async for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            history.append(data)
        return history

    async def save_preferences(self, user_id: str, prefs: dict) -> None:
        doc_ref = self.db.collection('users').document(user_id).collection('preferences').document('user_prefs')
        await doc_ref.set(prefs, merge=True)

    async def save_feedback(self, nudge_id: str, helpful: bool) -> None:
        nudges = self.db.collection_group('nudges').where(firestore.FieldPath.document_id(), '==', nudge_id)
        docs = nudges.stream()
        async for doc in docs:
            await doc.reference.update({'helpful': helpful})
            return

    async def get_behavior_patterns(self, user_id: str, days: int = 7) -> list:
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
        contexts_ref = self.db.collection('users').document(user_id).collection('contexts')
        query = contexts_ref.where('timestamp', '>=', cutoff).order_by('timestamp')
        docs = query.stream()
        
        patterns = []
        async for doc in docs:
            patterns.append(doc.to_dict())
        return patterns

firestore_service = FirestoreService()
