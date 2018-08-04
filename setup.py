from setuptools import setup

setup(name='subway',
      version='0.1.0',
      packages=['schedule'],
      entry_points={
          'schedule': [
              'schedule = schedule.__main__:main'
          ]
      },
      )
