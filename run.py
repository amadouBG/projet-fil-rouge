# run.py
import sys
import os

# --- AJOUT POUR LE CHEMIN PYTHON ---
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("--- [DEBUG] Python Path (sys.path) ---")
print('\n'.join(sys.path))
print("------------------------------------")
# --- FIN AJOUT ---

from interface import create_app
# --- MODIFICATION ICI ---
from api_config.api_script.models import User, SessionLocal, Base, engine
# --- FIN MODIFICATION ---

app = create_app()

# --- OPTIONNEL : Créer un utilisateur test ---
"""def create_test_user():
    # --- AJOUT/MODIFICATION ICI (pour être sûr) ---
    from api_config.api_script.models import User, SessionLocal
    # --- FIN AJOUT/MODIFICATION ---
    db_session = SessionLocal()
    if not db_session.query(User).filter_by(username='testuser').first():
        print("Création de l'utilisateur 'testuser'...")
        test_user = User(username='testuser', email='test@test.com', password_hash='password123')
        db_session.add(test_user)
        db_session.commit()
        print("Utilisateur 'testuser' créé. Mot de passe : password123")
    else:
        print("L'utilisateur 'testuser' existe déjà.")
    db_session.close()"""

if __name__ == '__main__':
    with app.app_context():
         print("Initialisation de la BDD (si nécessaire)...")
         Base.metadata.create_all(bind=engine) # Crée les tables si besoin
         print("Création de l'utilisateur test (si nécessaire)...")
         #create_test_user() # Crée l'utilisateur test
         print("Démarrage de l'application Flask...")

    app.run(debug=True, port=5000)