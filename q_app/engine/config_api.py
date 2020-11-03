from random import choices

class ConfigureApi:
    def __init__(self, db_client):
        self._db = db_client

    def create_doc(self, collection_name, document_description):
        document_id = document_description["id"]
        del document_description["id"]
        self._db[collection_name].update_one(
            {"_id": document_id}, {"$set": document_description}, upsert=True
        )

        return {"status_code": 200}

    def delete_doc(self, collection_name, document_description):
        document_name = document_description["id"]
        document = self._db[collection_name].find_one({"_id": document_name})
        if not document:
            return {
                "status_code": 200,
                "error": f"No document with name: {document_name}",
            }

        self._db[collection_name].delete_one({"_id": document_name})

        return {"status_code": 200, "deleted_document": document}

    def get_doc(self, collection_name, document_name):
        document = self._db[collection_name].find_one({"_id": document_name})
        if not document:
            return {
                "status_code": 200,
                "error": f"No document with name: {document_name}",
            }

        return {"status_code": 200, "data": document}

    def list_all_docs(self, collection_name):
        all_documents = []
        for document in self._db[collection_name].find({}):
            all_documents.append(document["_id"])

        return {"status_code": 200, "data": all_documents}

