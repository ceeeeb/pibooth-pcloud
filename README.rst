===============
pibooth-pcloud
===============

|PythonVersions| |License|

Plugin ``pibooth-pcloud`` pour `pibooth <https://github.com/pibooth/pibooth>`_
permettant l'upload automatique des photos vers un serveur `pCloud <https://www.pcloud.com>`_.

Un QR Code avec le lien public vers la galerie est affiché sur l'écran d'attente.

.. note:: Une connexion internet est requise pour le fonctionnement de ce plugin.

Installation
------------

::

    pip install pibooth-pcloud

Configuration
-------------

Obtenir un token OAuth2
~~~~~~~~~~~~~~~~~~~~~~~

1. Créer une application pCloud sur https://docs.pcloud.com/methods/oauth_2.0/authorize.html
   (noter le ``client_id`` et ``client_secret``)

2. Lancer le script d'aide fourni :

::

    python get_token.py

3. Le navigateur s'ouvre, autoriser l'application sur pCloud

4. Le token est affiché dans le terminal, le copier dans la config pibooth

.. note:: Le token n'expire pas sauf révocation manuelle depuis les paramètres pCloud.

Options
~~~~~~~

Éditer le fichier de configuration pibooth (``~/.config/pibooth/pibooth.cfg``) :

.. code-block:: ini

    [PCLOUD]

    # Activer l'upload vers pCloud
    activate = True

    # Token OAuth2 pCloud
    access_token =

    # Région du compte pCloud (US ou EU)
    region = EU

    # Dossier distant sur pCloud
    folder_path = /Pibooth

    # Position du QR code (top-left, top-right, bottom-left, bottom-right, center)
    qr_position = top-left

    # Taille du QR code (3-10)
    qr_size = 5

    # Marge du QR code par rapport au bord (pixels)
    qr_margin = 10

Fonctionnement
--------------

Au démarrage :

- Le plugin vérifie le token d'authentification
- Crée le dossier distant s'il n'existe pas
- Génère un lien public vers le dossier
- Affiche un QR Code pointant vers la galerie

Après chaque prise de photo :

- La photo est uploadée en arrière-plan (non-bloquant)

.. |PythonVersions| image:: https://img.shields.io/badge/python-3.6+-green.svg
   :target: https://www.python.org/downloads/

.. |License| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
