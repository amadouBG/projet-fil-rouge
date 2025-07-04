# interface/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.orm import joinedload
from .forms import LoginForm, URLForm
from api_config.api_script.models import User, SessionLocal, Tweet, Detection
from api_config.api_script.post_from_url import fetch_and_store_post

main = Blueprint('main', __name__)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        db_session = SessionLocal()
        user = db_session.query(User).filter_by(username=form.username.data).first()
        db_session.close()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Connexion réussie !', 'success')
            return redirect(request.args.get('next') or url_for('main.dashboard'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
    return render_template('login.html', title='Connexion', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('main.login'))

@main.route('/', methods=['GET', 'POST'])
@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = URLForm()
    tweet_obj = None
    detection_obj = None

    if form.validate_on_submit():
        url = form.bluesky_url.data
        try:
            # On récupère les deux objets et le statut retournés par la fonction
            tweet_obj, detection_obj, status = fetch_and_store_post(url, user_id=current_user.id)
            
            if status == 'new':
                flash("Post récupéré et analysé avec succès !", "success")
            elif status == 'existing':
                flash("Ce post existait déjà. Les informations ont été chargées depuis la base de données.", "info")
            else: # status == 'error'
                flash("Impossible de récupérer ce post. Vérifiez l'URL ou réessayez plus tard.", "danger")

        except Exception as e:
            print(f"Erreur lors de l'appel à fetch_and_store_post: {e}")
            flash("Une erreur interne est survenue.", "danger")

    # On passe les deux objets (ou None) au template
    return render_template(
        'dashboard.html',
        title='Dashboard',
        form=form,
        tweet_obj=tweet_obj,
        detection_obj=detection_obj
    )

@main.route('/all_tweets')
@login_required
def all_tweets():
    """Affiche tous les tweets présents dans la base de données."""
    db_session = SessionLocal()
    tweets_list = []
    try:
        # On utilise .options(joinedload(...)) pour charger les données liées
        # (auteur et détections) en une seule requête optimisée.
        tweets_list = db_session.query(Tweet).options(
            joinedload(Tweet.author), 
            joinedload(Tweet.detections)
        ).order_by(Tweet.created_at.desc()).all()
    finally:
        db_session.close()

    return render_template(
        'tweets_table.html',
        title="Tous les Tweets Analysés",
        tweets=tweets_list
    )

@main.route('/my_tweets')
@login_required
def my_tweets():
    """Affiche les tweets soumis par l'utilisateur connecté."""
    db_session = SessionLocal()
    tweets_list = []
    try:
        # On charge aussi les données liées ici pour éviter l'erreur DetachedInstanceError.
        tweets_list = db_session.query(Tweet).options(
            joinedload(Tweet.author), 
            joinedload(Tweet.detections)
        ).filter_by(user_id=current_user.id).order_by(Tweet.created_at.desc()).all()
    finally:
        db_session.close()

    return render_template(
        'tweets_table.html',
        title="Mes Tweets Soumis",
        tweets=tweets_list
    )
