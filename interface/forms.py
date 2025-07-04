# interface/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, URL

class LoginForm(FlaskForm):
    """Formulaire de connexion."""
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Se connecter")

class URLForm(FlaskForm):
    """Formulaire pour soumettre une URL Bluesky."""
    bluesky_url = StringField(
        "URL du post Bluesky",
        validators=[DataRequired(), URL(message="Veuillez entrer une URL valide.")],
        render_kw={"placeholder": "https://bsky.app/profile/.../post/..."}
    )
    submit = SubmitField("Analyser")