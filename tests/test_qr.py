# -*- coding: utf-8 -*-

"""Tests of the QR code kept on the wait screen."""

from unittest import mock

import pygame

import pibooth_pcloud as plugin


def make(position='bottom-left', shown=True):
    cfg = mock.Mock()
    cfg.getboolean.return_value = shown
    pcloud = mock.Mock(qr_image=pygame.Surface((185, 185)), qr_position=position, qr_margin=62)
    win = mock.Mock()
    win.get_rect.return_value = pygame.Rect(0, 0, 1600, 900)
    return cfg, mock.Mock(pcloud=pcloud), win


def test_qr_code_is_drawn_again_at_each_frame():
    cfg, app, win = make()
    plugin.state_wait_do(cfg, app, win)
    plugin.state_wait_do(cfg, app, win)
    assert win.surface.blit.call_count == 2
    assert win.surface.blit.call_args[0][1] == (62, 900 - 185 - 62)


def test_hidden_qr_code_is_not_drawn():
    cfg, app, win = make(shown=False)
    plugin.state_wait_do(cfg, app, win)
    win.surface.blit.assert_not_called()
