#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2017 Apple Inc. All rights reserved.
#
# Use of this source code is governed by a BSD-3-clause license that can
# be found in the LICENSE.txt file or at https://opensource.org/licenses/BSD-3-Clause

import os
import sys
from setuptools import setup, find_packages, Extension
from setuptools.dist import Distribution
from setuptools.command.install import install

PACKAGE_NAME = "turicreate"
VERSION = "6.4.2"  # {{VERSION_STRING}}
# pkgs not needed for minimal pkg
NON_MINIMAL_LIST = [
    "coremltools",
    "pandas",
    "resampy",
    "scipy",
    "tensorflow",
]


# Prevent distutils from thinking we are a pure python package
class BinaryDistribution(Distribution):
    def is_pure(self):
        return False


class InstallEngine(install):
    """Helper class to hook the python setup.py install path to download
    client libraries and engine
    """

    user_options = install.user_options + [
        ("minimal", None, "control minimal installation"),  # a 'flag' option
    ]

    def initialize_options(self):
        install.initialize_options(self)
        self.minimal = None

    def run(self):
        if self.minimal is not None:

            def do_not_install(require):
                require = require.strip()
                for name in NON_MINIMAL_LIST:
                    if require.startswith(name):
                        return False
                return True

            install_requires_minimal = list(
                filter(do_not_install, self.distribution.install_requires)
            )

            orig_install_requires = self.distribution.install_requires
            self.distribution.install_requires = install_requires_minimal

            print(" minimal install: ", install_requires_minimal)
            print("original install: ", orig_install_requires)

        import platform

        # start by running base class implementation of run
        install.run(self)

        # Check correct version of architecture (64-bit only)
        arch = platform.architecture()[0]
        if arch != "64bit":
            msg = (
                "Turi Create currently supports only 64-bit operating systems, and only recent Linux/OSX "
                + "architectures. Please install using a supported version. Your architecture is currently: %s"
                % arch
            )

            sys.stderr.write(msg)
            sys.exit(1)

        # if OSX, verify >= 10.8
        from distutils.util import get_platform
        from pkg_resources import parse_version

        cur_platform = get_platform()

        if cur_platform.startswith("macosx"):

            mac_ver = platform.mac_ver()[0]
            if parse_version(mac_ver) < parse_version("10.8.0"):
                msg = (
                    "Turi Create currently does not support versions of OSX prior to 10.8. Please upgrade your Mac OSX "
                    "installation to a supported version. Your current OSX version is: %s"
                    % mac_ver
                )
                sys.stderr.write(msg)
                sys.exit(1)
        elif cur_platform.startswith("linux"):
            pass
        elif cur_platform.startswith("win"):
            win_ver = platform.version()
            # Verify this is Vista or above
            if parse_version(win_ver) < parse_version("6.0"):
                msg = (
                    "Turi Create currently does not support versions of Windows"
                    " prior to Vista, or versions of Windows Server prior to 2008."
                    "Your current version of Windows is: %s" % platform.release()
                )
                sys.stderr.write(msg)
                sys.exit(1)
        else:
            msg = (
                "Unsupported Platform: '%s'. Turi Create is only supported on Windows, Mac OSX, and Linux."
                % cur_platform
            )
            sys.stderr.write(msg)
            sys.exit(1)


if __name__ == "__main__":
    from distutils.util import get_platform

    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Other Audience",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ]
    cur_platform = get_platform()
    if cur_platform.startswith("macosx"):
        classifiers.append("Operating System :: MacOS :: MacOS X")
    elif cur_platform.startswith("linux"):
        classifiers += [
            "Operating System :: POSIX :: Linux",
            "Operating System :: POSIX :: BSD",
            "Operating System :: Unix",
        ]
    elif cur_platform.startswith("win"):
        classifiers += ["Operating System :: Microsoft :: Windows"]
    else:
        msg = (
            "Unsupported Platform: '%s'. Turi Create is only supported on Windows, Mac OSX, and Linux."
            % cur_platform
        )
        sys.stderr.write(msg)
        sys.exit(1)

    with open(os.path.join(os.path.dirname(__file__), "README.rst"), "rb") as f:
        long_description = f.read().decode("utf-8")

    install_requires = [
        "decorator >= 4.0.9",
        "numpy",
        "pandas >= 0.23.2",
        "pillow >= 5.2.0",
        "prettytable == 0.7.2",
        "resampy == 0.2.1",
        "requests >= 2.9.1",
        "scipy >= 1.1.0",
        "six >= 1.10.0",
        "coremltools==5.0b2",
    ]
    if sys.version_info[0] == 2 or (
        sys.version_info[0] == 3 and sys.version_info[1] == 5
    ):
        install_requires.append("llvmlite == 0.31.0")
    if sys.version_info[0] == 3 and sys.version_info[1] == 9:
        install_requires.append("llvmlite == 0.36.0")

    if sys.platform == "darwin":
        install_requires.append("tensorflow >= 2.0.0")
    else:
        # ST, OD, AC and DC segfault on Linux with TensorFlow 2.1.0 and 2.1.1
        # See: https://github.com/apple/turicreate/issues/3003

        # SC errors out on Linux with TensorFlow 2.2 and 2.3
        # See: https://github.com/apple/turicreate/issues/3303

        if sys.version_info[0] != 3 or sys.version_info[1] < 8:
            install_requires.append("tensorflow >= 2.0.0,<2.1.0")
        else:
            # Only TensorFlow >= 2.2 supports Python 3.8
            install_requires.append("tensorflow >= 2.0.0")

        # numba 0.51 started using "manylinux2014" rather than "manylinux2010".
        # This breaks a lot of Linux installs.
        if sys.version_info[0] != 3 and sys.version_info[1] != 9:
            install_requires.append("numba < 0.51.0")

    setup(
        name="turicreate",
        version=VERSION,
        # This distribution contains platform-specific C++ libraries, but they are not
        # built with distutils. So we must create a dummy Extension object so when we
        # create a binary file it knows to make it platform-specific.
        ext_modules=[Extension("turicreate.__dummy", sources=["dummy.c"])],
        author="Apple Inc.",
        author_email="turi-create@group.apple.com",
        cmdclass=dict(install=InstallEngine),
        distclass=BinaryDistribution,
        package_data={
            "turicreate": [
                "_cython/*.so",
                "_cython/*.pyd",
                "*.so",
                "*.dylib",
                "toolkits/*.so",
                # macOS visualization
                "Turi Create Visualization.app/Contents/*",
                "Turi Create Visualization.app/Contents/_CodeSignature/*",
                "Turi Create Visualization.app/Contents/MacOS/*",
                "Turi Create Visualization.app/Contents/Resources/*",
                "Turi Create Visualization.app/Contents/Resources/Base.lproj/*",
                "Turi Create Visualization.app/Contents/Resources/Base.lproj/Main.storyboardc/*",
                "Turi Create Visualization.app/Contents/Resources/build/*",
                "Turi Create Visualization.app/Contents/Resources/build/static/*",
                "Turi Create Visualization.app/Contents/Resources/build/static/css/*",
                "Turi Create Visualization.app/Contents/Resources/build/static/js/*",
                "Turi Create Visualization.app/Contents/Resources/build/static/media/*",
                "Turi Create Visualization.app/Contents/Frameworks/*",
                # Linux visualization
                "Turi Create Visualization/*.*",
                "Turi Create Visualization/visualization_client",
                "Turi Create Visualization/swiftshader/*",
                "Turi Create Visualization/locales/*",
                "Turi Create Visualization/html/*.*",
                "Turi Create Visualization/html/static/js/*",
                "Turi Create Visualization/html/static/css/*",
                # Plot.save dependencies
                "visualization/vega_3.2.1.js",
                "visualization/vg2png",
                "visualization/vg2svg",
            ]
        },
        packages=find_packages(exclude=["test"]),
        url="https://github.com/apple/turicreate",
        license="LICENSE.txt",
        description="Turi Create simplifies the development of custom machine learning models.",
        long_description=long_description,
        classifiers=classifiers,
        install_requires=install_requires,
    )
