# ============================================================
# create_tables.py — run this ONCE to create all DB tables
# ============================================================
from database import Base, engine
import models   # registers all 4 table classes with Base

Base.metadata.create_all(bind=engine)
print("Tables created: users, students, predictions, interventions")