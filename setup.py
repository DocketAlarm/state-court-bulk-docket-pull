from setuptools import find_packages, setup
import pathlib

with open("README.md") as f:
    long_description = f.read()

HERE = pathlib.Path(__file__).parent

setup(name='docket-alarm-api-bulk-download',
    version='1.0',
    description="Uses the Docket Alarm API to pull state court cases in bulk. Simply supply a spreadsheet full of case numbers!",
    long_description=long_description,
    author='Ryan Fitzpatrick',
    author_email='ryanfitz514@gmail.com',
    url="https://github.com/ryanfitz514/state-court-bulk-docket-pull",
    license="Apache-2.0 License",
    keywords=['DOCKET', 'ALARM', 'API', 'BULK', 'DOWNLOAD', 'COURT', 'COURTS', 'PACER', 'FASTCASE'],
    install_requires=[
'stdiomask',
'colorama',
'progress',
'pandas',
'tqdm',
'requests',
'retrying',
'PyPDF2',
'PySimpleGUI',
'openpyxl',
    ],
    entry_points={
        'console_scripts':['docket-alarm-api-bulk-download=project.__main__:welcome'],
    }
    )