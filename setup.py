from setuptools import setup, find_packages

setup(
    name='helga-reviews',
    version='0.0.4',
    description=('A helga command to query reviewboard pending reviews targeted at a user, group'
                 'or channel (using a channel-to-group mapping).'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'Framework :: Twisted',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='helga reviewboard',
    author="Shaun Duncan",
    author_email="shaun.duncan@gmail.com",
    url="https://github.com/shaunduncan/helga-reviews",
    packages=find_packages(),
    py_modules=['helga_reviews'],
    include_package_data=True,
    install_requires=[
        'RBTools==0.6.1'
    ],
    zip_safe=True,
    entry_points=dict(
        helga_plugins=[
            'reviews = helga_reviews:reviews',
        ],
    ),
)
