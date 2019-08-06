from setuptools import setup, find_packages


setup(
        name='simon-etsy',
        version='1.0.0',
        description="Etsy shop keyword finder",
        author="Jacob Alheid",
        author_email="shakefu@gmail.com",
        packages=find_packages(exclude=['test']),
        install_requires=[
            'configargparse',
            'nltk',
            'pytool',
            'requests',
            ],
        entry_points={
            'console_scripts': [
                'simon-etsy=simon_etsy.__main__:Main.console_script',
            ],
        },
        test_suite='nose.collector',
        tests_require=[
            'nose',
            'mock',
            ],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.6',
            'Topic :: Utilities',
            ]
        )

