from setuptools import setup
import sys

#mac - virtualenv then python setup.py py2app
#linux -  pyi-makespec sfftk.py -n SFFToolKit --onefile --icon=./data/icon.ico --windowed --add-data 'data/*:./data'
#windows - pyi-makespec sfftk.py -n SFFToolKit --onefile --icon=./data/icon.ico --windowed --add-data data\*;data\
#linux and win - pyinstaller SFFToolKit.spec

if sys.platform == "win32":
    #windows
    setup(name='sfftoolkit',
      version='0.3',
      description='Tools to pull data from Solforge Fusion Website and make stuff with it.',
      url='na',
      author='gchristian',
      author_email='na',
      license='',
      packages=['sfftk'],
      zip_safe=False,
      install_requires=[
          'reportlab','Pillow','wxPython','requests'
      ],
      include_package_data=True)
elif sys.platform == 'darwin':
    #mac
    APP = ['./sfftk/sfftk.py']
    DATA_FILES = ["./sfftk/data"]
    OPTIONS = {
        'argv_emulation': False, 
        'site_packages': True,
        'iconfile': './sfftk/icon.icns',
        'packages': ['wx', 'requests','reportlab'],
        'plist': {
            'CFBundleName': 'SFFToolKit',
            'CFBundleShortVersionString':'0.3.0', # must be in X.X.X format
            'CFBundleVersion': '0.3.0',
            'CFBundleIdentifier':'com.extraneous.sfftoolkit', 
            'NSHumanReadableCopyright': '@ Gorman Christian 2022',
            }   
    }
    setup(
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )
else:
    #unix/linux
    setup(name='sfftoolkit',
      version='0.3',
      description='Tools to pull data from Solforge Fusion Website and make stuff with it.',
      url='na',
      author='gchristian',
      author_email='na',
      license='',
      packages=['sfftk'],
      zip_safe=False,
      install_requires=[
          'reportlab','Pillow','wxPython','requests'
      ],
      include_package_data=True)
