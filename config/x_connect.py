import os
import sys

import tweepy

from flask import g

def get_x_client():
    """Função para obter a conexão com a API do X."""
    env = os.getenv('FLASK_ENV', 'dev')

    if "x_client" not in g:
        try:
            bearer_token = os.getenv("BEARER_TOKEN")
            if not bearer_token:
                raise ValueError("❌ BEARER_TOKEN not found in .env")

            g.twitter_client = tweepy.Client(bearer_token)

            if env == "prod":
                print("✅ Tweepy successfully configured")

        except Exception as e:
            print(f"❌ Error connecting to Twitter API: {e}")
            sys.exit(1)

    return g.twitter_client