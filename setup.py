from setuptools import find_packages, setup
import pathlib

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(name='docket-alarm-api-bulk-download',
    version='0.0.1',
    description="Uses the Docket Alarm API to pull state court cases in bulk",
    long_description=README,
    long_description_content_type='text/markdown',
    description_content_type='text/markdown',
    author='Ryan Fitzpatrick',
    author_email='ryanfitz514@gmail.com',
    url="https://github.com/DocketAlarm/state-court-bulk-docket-pull",
    license="Apache",
    keywords=['DOCKET', 'ALARM', 'API', 'BULK', 'DOWNLOAD', 'COURT', 'COURTS', 'PACER', 'FASTCASE'],
    packages=["docket_alarm_api_bulk_download"],
    package_dir = {'docket_alarm_api_bulk_download':'docket_alarm_api_bulk_download'},
    package_data = {'docket_alarm_api_bulk_download':['docket_alarm_api_bulk_download/csv/input.sample.csv','docket_alarm_api_bulk_download/docs/.gitkeep','docket_alarm_api_bulk_download/json-output/.gitkeep','docket_alarm_api_bulk_download/log/.gitkeep','docket_alarm_api_bulk_download/pdf-output/.gitkeep', 'docket_alarm_api_bulk_download/sav/.gitkeep']},
    include_package_data=True,
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
        'console_scripts':['docket-alarm-api-bulk-download=docket_alarm_api_bulk_download.__main__:run'],
    }
    )