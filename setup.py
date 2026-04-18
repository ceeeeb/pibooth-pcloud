#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from io import open
import os.path as osp
from setuptools import setup


HERE = osp.abspath(osp.dirname(__file__))

with open(osp.join(HERE, 'pibooth_pcloud.py'), encoding='utf-8') as f:
    content = f.read()
    version = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content).group(1)


def main():
    setup(
        name='pibooth_pcloud',
        version=version,
        description="Pibooth plugin to upload photos to pCloud and display a QR code",
        long_description=open(osp.join(HERE, 'README.rst'), encoding='utf-8').read(),
        long_description_content_type='text/x-rst',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Other Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.11',
            'Natural Language :: English',
            'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
        ],
        author="Christophe",
        url="https://github.com/ceeeeb/pibooth-pcloud",
        download_url="https://github.com/ceeeeb/pibooth-pcloud/archive/{}.tar.gz".format(version),
        license='MIT license',
        platforms=['unix', 'linux'],
        keywords=[
            'Raspberry Pi',
            'camera',
            'photobooth',
            'pcloud',
        ],
        py_modules=['pibooth_pcloud'],
        install_requires=[
            'pibooth>=2.0.0',
            'qrcode>=6.1',
            'requests',
        ],
        options={
            'bdist_wheel': {'universal': True},
        },
        zip_safe=False,
        entry_points={'pibooth': ["pibooth_pcloud = pibooth_pcloud"]},
    )


if __name__ == '__main__':
    main()
