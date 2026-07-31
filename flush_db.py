import sys
from google.cloud import firestore

def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        doc.reference.delete()
        deleted += 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

if __name__ == '__main__':
    print("Flushing database...")
    db = firestore.Client(project="fitnessapp-504108")
    workouts_ref = db.collection("workouts")
    delete_collection(workouts_ref, 50)
    print("Database flushed successfully.")
