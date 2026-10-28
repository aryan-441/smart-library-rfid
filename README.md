# Smart Library RFID Prototype

A Python library checkout prototype that combines a book catalogue and borrowing records with RFID input. Later versions add a Tkinter interface; the project also contains Arduino sketch files for the reader side.

## Technologies

Python, JSON, Tkinter, serial communication (`pyserial`), and Arduino/C++.

## Setup

The current versions contain a Windows serial-port setting and expect local JSON files in the working directory. Select one canonical implementation, install its verified dependencies, configure the reader port, and start from that project directory before using this README as a final run guide.

## Privacy and limitations

The source tree includes embedded member names and RFID identifiers. Replace those with placeholders and remove real transaction data before publishing. This draft intentionally includes no sample user records. The project has several divergent versions and needs a correctness review of borrowing/returns, storage, and overdue handling. Drive timestamps for representative sources are 2024-12-18 (`SmartLibrary.py.py`) and 2025-05-08 (`UPDATED/main (2).py`); these do not establish the project start or completion date.

No license has been selected.
