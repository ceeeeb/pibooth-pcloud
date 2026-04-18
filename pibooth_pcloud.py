# -*- coding: utf-8 -*-

"""Pibooth plugin for pCloud upload."""

import hashlib
import os
import threading

import requests
import qrcode
import pygame

import pibooth
from pibooth.utils import LOGGER

__version__ = "1.0.0"

SECTION = "PCLOUD"

# pCloud API hosts per region
API_HOSTS = {
    "US": "https://api.pcloud.com",
    "EU": "https://eapi.pcloud.com",
}


def _api_url(host, method):
    return f"{host}/{method}"


###########################################################################
# HOOKS pibooth
###########################################################################


@pibooth.hookimpl
def pibooth_configure(cfg):
    """Declare the plugin configuration options."""
    cfg.add_option(SECTION, 'activate', True,
                   "Enable upload to pCloud",
                   "Enable upload", ['True', 'False'])
    cfg.add_option(SECTION, 'email', '',
                   "pCloud account email",
                   "Email", '')
    cfg.add_option(SECTION, 'password', '',
                   "pCloud account password (stored in clear, chmod 600 recommended)",
                   "Password", '')
    cfg.add_option(SECTION, 'region', 'EU',
                   "pCloud account region (US or EU)",
                   "Region", ['US', 'EU'])
    cfg.add_option(SECTION, 'folder_path', '/Pibooth',
                   "Remote parent folder on pCloud",
                   "Folder Path", '/Pibooth')
    cfg.add_option(SECTION, 'album_name', 'Pibooth',
                   "Sub-folder (event album) inside folder_path; the public link points here",
                   "Album Name", 'Pibooth')
    cfg.add_option(SECTION, 'qr_position', 'top-left',
                   "QR code position (top-left, top-right, bottom-left, bottom-right, center)",
                   "QR Position", ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'])
    cfg.add_option(SECTION, 'qr_size', 5,
                   "QR code box_size (3-10)",
                   "QR Size", '5')
    cfg.add_option(SECTION, 'qr_margin', 10,
                   "QR code margin from screen edge in pixels",
                   "QR Margin", '10')


@pibooth.hookimpl
def pibooth_startup(app, cfg):
    """Initialize PCloudUpload instance and create QR code."""
    activate = cfg.getboolean(SECTION, 'activate')
    if not activate:
        LOGGER.info("pCloud upload is disabled")
        app.pcloud = None
        return

    email = cfg.get(SECTION, 'email').strip()
    password = cfg.get(SECTION, 'password')
    if not email or not password:
        LOGGER.warning("pCloud email or password is not configured")
        app.pcloud = None
        return

    region = cfg.get(SECTION, 'region').upper()
    api_host = API_HOSTS.get(region, API_HOSTS["EU"])
    parent_path = cfg.get(SECTION, 'folder_path').strip().rstrip('/') or '/Pibooth'
    if not parent_path.startswith('/'):
        parent_path = '/' + parent_path
    album_name = cfg.get(SECTION, 'album_name').strip() or 'Pibooth'
    album_path = f"{parent_path}/{album_name}"

    app.pcloud = PCloudUpload(email, password, api_host)
    app.pcloud.qr_position = cfg.get(SECTION, 'qr_position')
    app.pcloud.qr_size = cfg.getint(SECTION, 'qr_size')
    app.pcloud.qr_margin = cfg.getint(SECTION, 'qr_margin')
    app.pcloud.local_rep = cfg.get('GENERAL', 'directory')

    if not app.pcloud.check_credentials():
        LOGGER.error("pCloud authentication failed, plugin disabled")
        app.pcloud = None
        return

    if app.pcloud.ensure_folder(parent_path) is None:
        LOGGER.error("Cannot create pCloud folder '%s', plugin disabled", parent_path)
        app.pcloud = None
        return

    album_id = app.pcloud.ensure_folder(album_path)
    if album_id is None:
        LOGGER.error("Cannot create pCloud folder '%s', plugin disabled", album_path)
        app.pcloud = None
        return

    app.pcloud.folder_path = album_path
    app.pcloud.folder_id = album_id

    gallery_link = app.pcloud.get_folder_public_link(album_id)
    if not gallery_link:
        LOGGER.warning("Could not create public link, QR code will show folder path")
        gallery_link = album_path

    app.pcloud.gallery_link = gallery_link

    # Generate QR code
    qr_box_size = max(3, min(10, app.pcloud.qr_size))
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=qr_box_size,
        border=2,
    )
    qr.add_data(gallery_link)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    image.save(os.path.join(app.pcloud.local_rep, 'QRCODE.png'), "PNG")
    app.pcloud.qr_image = pygame.image.fromstring(
        image.tobytes(), image.size, image.mode
    )

    LOGGER.info("pCloud plugin ready (region=%s, folder=%s)", region, album_path)


@pibooth.hookimpl
def state_wait_enter(cfg, app, win):
    """Display QR code on the wait screen."""
    if not getattr(app, 'pcloud', None):
        return

    win_rect = win.get_rect()
    qr_rect = app.pcloud.qr_image.get_rect()
    margin = app.pcloud.qr_margin
    position = app.pcloud.qr_position

    positions = {
        "top-left": (margin, margin),
        "top-right": (win_rect.width - qr_rect.width - margin, margin),
        "bottom-left": (margin, win_rect.height - qr_rect.height - margin),
        "bottom-right": (win_rect.width - qr_rect.width - margin,
                         win_rect.height - qr_rect.height - margin),
        "center": ((win_rect.width - qr_rect.width) // 2,
                   (win_rect.height - qr_rect.height) // 2),
    }
    x, y = positions.get(position, (margin, margin))
    win.surface.blit(app.pcloud.qr_image, (x, y))


@pibooth.hookimpl
def state_processing_exit(app, cfg):
    """Upload the captured photo to pCloud (non-blocking)."""
    if not getattr(app, 'pcloud', None):
        return

    photo_path = app.previous_picture_file
    folder_path = app.pcloud.folder_path

    def _do_upload():
        if not app.pcloud.upload_lock.acquire(blocking=False):
            LOGGER.warning("pCloud upload already in progress, skipping")
            return
        try:
            app.pcloud.upload_file(photo_path, folder_path)
        finally:
            app.pcloud.upload_lock.release()

    thread = threading.Thread(target=_do_upload, daemon=True)
    thread.start()


###########################################################################
# pCloud API client
###########################################################################


class PCloudUpload:

    DIGEST_TTL = 60  # seconds — pCloud digests are short-lived, refresh often

    def __init__(self, email, password, api_host):
        self.email = email
        self.password = password
        self.api_host = api_host
        self.upload_lock = threading.Lock()
        self._digest_lock = threading.Lock()
        self._username_sha1 = hashlib.sha1(email.lower().encode()).hexdigest()
        self.gallery_link = ""
        self.folder_path = ""
        self.folder_id = 0
        self.qr_image = None
        self.qr_position = "top-left"
        self.qr_size = 5
        self.qr_margin = 10
        self.local_rep = ""

    def _fresh_auth_params(self):
        """Fetch a new digest and compute the password digest for a single call."""
        with self._digest_lock:
            resp = requests.get(_api_url(self.api_host, "getdigest"), timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if data.get("result") != 0:
                raise RuntimeError(f"getdigest failed: {data.get('error')}")
            digest = data["digest"]
        password_digest = hashlib.sha1(
            (self.password + self._username_sha1 + digest).encode()
        ).hexdigest()
        return {"username": self.email, "digest": digest,
                "passworddigest": password_digest}

    def _call(self, method, params=None, files=None, timeout=30):
        """Call a pCloud API method authenticated with a fresh digest."""
        url = _api_url(self.api_host, method)
        params = dict(params or {})

        try:
            params.update(self._fresh_auth_params())
            if files:
                resp = requests.post(url, data=params, files=files, timeout=timeout)
            else:
                resp = requests.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            if data.get("result") != 0:
                LOGGER.error("pCloud API error %s: %s",
                             data.get("result"), data.get("error", "unknown"))
                return None
            return data
        except (requests.RequestException, RuntimeError) as e:
            LOGGER.error("pCloud request failed (%s): %s", method, e)
            return None

    def check_credentials(self):
        """Verify the email/password authenticate successfully."""
        data = self._call("userinfo")
        if data:
            LOGGER.info("pCloud authenticated as %s", data.get("email", "unknown"))
            return True
        return False

    def ensure_folder(self, path):
        """Create the folder (and parents) if it does not exist.
        Returns the folder ID or None on error.
        """
        data = self._call("createfolderifnotexists", {"path": path})
        if data and "metadata" in data:
            folder_id = data["metadata"]["folderid"]
            LOGGER.info("pCloud folder ready: %s (id=%s)", path, folder_id)
            return folder_id
        return None

    def get_folder_public_link(self, folder_id):
        """Get or create a public link for the folder."""
        data = self._call("getfolderpublink", {"folderid": folder_id})
        if data and "link" in data:
            LOGGER.info("pCloud public link: %s", data["link"])
            return data["link"]
        # Try listing existing public links
        data = self._call("listpublinks")
        if data and "publinks" in data:
            for link in data["publinks"]:
                if link.get("folderid") == folder_id:
                    return link.get("link", "")
        LOGGER.warning("Could not get public link for folder %s", folder_id)
        return ""

    def upload_file(self, local_path, remote_folder_path):
        """Upload a single file to the given pCloud folder."""
        filename = os.path.basename(local_path)
        LOGGER.info("Uploading %s to pCloud:%s", filename, remote_folder_path)

        try:
            with open(local_path, 'rb') as f:
                data = self._call(
                    "uploadfile",
                    params={"path": remote_folder_path, "filename": filename,
                            "nopartial": 1, "renameifexists": 1},
                    files={"file": (filename, f)},
                    timeout=120,
                )
        except OSError as e:
            LOGGER.error("Cannot read file %s: %s", local_path, e)
            return False

        if data:
            LOGGER.info("Photo uploaded to pCloud successfully: %s", filename)
            return True

        LOGGER.error("Upload to pCloud failed for %s", filename)
        return False
