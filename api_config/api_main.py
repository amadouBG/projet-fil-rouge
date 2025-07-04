from api_script.models import init_db
from api_script.timeline import fetch_public_feed

def main():
    init_db()
    fetch_public_feed()

if __name__ == "__main__":
    main()
