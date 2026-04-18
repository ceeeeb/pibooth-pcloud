#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Validate pCloud email/password and print the pibooth config block.

pibooth-pcloud authenticates each API call with a fresh digest derived from
email+password — no long-lived token. This helper just confirms the
credentials work and formats the config block ready to paste into
~/.config/pibooth/pibooth.cfg.
"""

import getpass
import hashlib

import requests

API_HOSTS = {
    "EU": "https://eapi.pcloud.com",
    "US": "https://api.pcloud.com",
}


def check_credentials():
    print("=" * 60)
    print("  pibooth-pcloud - Verification des identifiants")
    print("=" * 60)
    print()

    region = input("Region du compte (EU/US) [EU] : ").strip().upper() or "EU"
    if region not in API_HOSTS:
        print(f"Region invalide : {region}")
        return
    host = API_HOSTS[region]

    email = input("Email pCloud : ").strip()
    password = getpass.getpass("Mot de passe pCloud : ")
    if not email or not password:
        print("Erreur : email et mot de passe requis.")
        return

    digest_resp = requests.get(f"{host}/getdigest", timeout=30).json()
    if digest_resp.get("result") != 0:
        print(f"Erreur getdigest : {digest_resp.get('error')}")
        return
    digest = digest_resp["digest"]

    username_sha1 = hashlib.sha1(email.lower().encode()).hexdigest()
    password_digest = hashlib.sha1(
        (password + username_sha1 + digest).encode()
    ).hexdigest()

    data = requests.get(f"{host}/userinfo", params={
        "username": email, "digest": digest,
        "passworddigest": password_digest,
    }, timeout=30).json()

    if data.get("result") != 0:
        print(f"Echec : {data.get('error', 'code ' + str(data.get('result')))}")
        return

    print()
    print("=" * 60)
    print("  AUTHENTIFICATION REUSSIE")
    print("=" * 60)
    print()
    print(f"  Compte  : {data.get('email', email)}")
    print(f"  Region  : {region}")
    print(f"  Plan    : {data.get('plan', '?')}")
    print()
    print("A ajouter dans ~/.config/pibooth/pibooth.cfg :")
    print()
    print("  [PCLOUD]")
    print("  activate = True")
    print(f"  email = {email}")
    print(f"  password = {password}")
    print(f"  region = {region}")
    print("  folder_path = /Pibooth")
    print("  qr_position = top-right")
    print()
    print("Puis restreindre les droits :")
    print("  chmod 600 ~/.config/pibooth/pibooth.cfg")


if __name__ == "__main__":
    check_credentials()
