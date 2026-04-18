===============
pibooth-pcloud
===============

|PythonVersions| |License|

Plugin ``pibooth-pcloud`` pour `pibooth <https://github.com/pibooth/pibooth>`_
qui envoie automatiquement les photos finales vers un compte
`pCloud <https://www.pcloud.com>`_ et affiche un QR code vers la galerie
publique sur l'écran d'attente.

Fonctionnalités :

- Authentification par email + mot de passe (digest par appel, aucun OAuth à
  créer côté pCloud).
- Upload d'un album par événement (``folder_path/album_name``) et lien public
  généré sur ce sous-dossier.
- Synchronisation de rattrapage : au démarrage et après chaque photo, les
  fichiers présents en local mais absents de pCloud sont envoyés, ce qui
  absorbe les coupures Internet pendant un événement.

.. note:: Une connexion internet est requise pendant l'événement (ou plus
          tard pour rattraper les uploads).

Installation
------------

::

    pip install pibooth-pcloud

Configuration
-------------

Vérifier les identifiants pCloud
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Le script fourni valide les identifiants et imprime le bloc à coller dans
``~/.config/pibooth/pibooth.cfg`` :

::

    pibooth-pcloud-token

L'email doit être vérifié côté pCloud — sans vérification, l'API refuse la
création de liens publics.

Exemple de configuration
~~~~~~~~~~~~~~~~~~~~~~~~

Voir ``pibooth.cfg.example`` à la racine du dépôt. Bloc à ajouter dans
``~/.config/pibooth/pibooth.cfg`` :

.. code-block:: ini

    [PCLOUD]

    # Activer le plugin
    activate = True

    # Identifiants pCloud (stockés en clair — restreindre les droits du fichier)
    email = your.email@example.com
    password = your-password

    # Région du compte (EU ou US)
    region = EU

    # Dossier parent sur pCloud (créé s'il n'existe pas)
    folder_path = /Pibooth

    # Sous-dossier événement sur pCloud ; le lien public cible ce sous-dossier
    album_name = MonEvenement

    # Position du QR code (top-left, top-right, bottom-left, bottom-right, center)
    qr_position = top-right

    # Taille du QR code (3-10)
    qr_size = 5

    # Marge du QR code par rapport au bord (pixels)
    qr_margin = 10

Après édition, restreindre les droits du fichier :

::

    chmod 600 ~/.config/pibooth/pibooth.cfg

Fonctionnement
--------------

Au démarrage de pibooth :

- Authentification par digest, création du dossier parent et de l'album.
- Récupération du lien public de l'album, génération du QR code.
- Première passe de synchronisation : les photos locales absentes de pCloud
  sont envoyées.

Après chaque photo (``state_processing_exit``) :

- Synchronisation en arrière-plan : la nouvelle photo et toute photo
  restée en retard sont envoyées. L'opération ne bloque pas l'interface.

.. |PythonVersions| image:: https://img.shields.io/badge/python-3.6+-green.svg
   :target: https://www.python.org/downloads/

.. |License| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
