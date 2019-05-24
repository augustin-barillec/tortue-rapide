from setuptools import setup, find_packages


setup(name='tortue-rapide',
      version='1.0.0',
      entry_points={
          'console_scripts': [
              'donkey=donkeycar.management.base:execute_from_command_line',
          ],
      },
      install_requires=['numpy',
                        'pillow',
                        'docopt',
                        'tornado==4.5.3',
                        'requests',
                        'h5py',
                        'python-socketio',
                        'flask',
                        'eventlet',
                        'moviepy',
                        'pandas',
                        ],

      extras_require={
                      'tf': ['tensorflow>=1.7.0'],
                      'tf_gpu': ['tensorflow-gpu>=1.7.0'],
                      'pi': [
                          'picamera',
                          'Adafruit_PCA9685',
                          ],
                  },

      include_package_data=True,

      packages=find_packages())
