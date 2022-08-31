..
    INVENIO-SIP2
    Copyright (C) 2020 UCLouvain

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, version 3 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

Changes
=======
Version 0.6.16 (released 2022-08-31)

**Bug fix:**

* Fixes project dependency.

Version 0.6.15 (released 2022-08-30)

**Bug fix:**

* Fixes sphinx dependency.

Version 0.6.14 (released 2022-08-30)

**Bug fix:**

* Fixes datastore local proxy.

**Minor change:**

* Changes logging level for `CommandNotFound` and `UnicodeDecodeError`.
* Moves to poetry.


Version 0.6.13 (released 2021-08-25)

**Bug fix:**

* Fixes request resend wrong decoding.

**Minor change:**

* Adds CommandNotFound exception.
* Catchs all exceptions when reading the request.


Version 0.6.12 (released 2021-08-24)

**Bug fix:**

* Fix missing parsing date.
* Fix request resend checksum validation.

**Minor change:**

* Adds module version in logging formatter.

Version 0.6.11 (released 2021-08-17)

**Bug fix:**

* Forces text encoding on checksum generation

Version 0.6.10 (released 2021-08-09)

**Minor change:**

* Improves server logging.
* Ensures that the sequence number is present in the message if the selfchek terminal sends it.
* Adds sequence number and checksum in dumped message.
* Adds cached property to extension.

**Bug fix:**

* Fixes circulation date parsing.
* Rewrites error detection for request and response message.

Version 0.6.9 (released 2021-07-28)

**Bug fix:**

* Fixes invenio-search version.
* Fixes invenio-db version.

Version 0.6.8 (released 2021-07-27)

**Minor change:**

* Catches runtime error.
* Uses pydocstyle and pycodestyle.
* Increase code coverage.
* Cleans code.

Version 0.6.7 (released 2021-07-19)

**Bug fix:**

* Fixes missing conversion of i18n language.
* Fixes date format.

Version 0.6.6 (released 2021-07-14)

**Minor changes:**

* Defines supported messages from handlers config.

**Bug fix:**

* Fixes empty patron session.
* Improves i18n language.

Version 0.6.5 (released 2021-07-12)

**Minor changes:**

* Logs more information for debugging

Version 0.6.4 (released 2021-06-30)

**Bug fix:**

* Fixes wrong circulation messages response.
* Fixes no such process in command line utilities.

Version 0.6.3 (released 2021-06-15)

**Bug fix:**

* Fixes error on renew action.

Version 0.6.2 (released 2021-06-14)

**Minor changes:**

* implement summary for patron information.
* Fixes fixed field wrong length.

Version 0.6.1 (released 2021-06-14)

**Minor changes:**

- Use invenio-sip2 logger for server error logs.

Version 0.6.0 (released 2021-06-11)

**Implemented enhancements:**

- Implements request resend action.
- Adds CLI to stop the server.
- Implements sequence number error detection.

Version 0.5.1 (released 2021-05-06)

**Minor changes:**

- Increase code coverage.
- Updates documentation.
- Cleans and rewrites code.

Version 0.5.0 (released 2021-03-25)

**Implemented enhancements:**

- Adds datastore to save clients and servers state.
- Adds record metadata management.
- Adds APIs to monitor servers and clients.
- Implements specific logger to log selfcheck requests and server responses.

Version 0.4.0 (released 2020-11-26)

**Implemented enhancements:**

- Implements Patron status action.
- Moves to github action for continuous Integration.

**Fixed bugs:**

- Increase code coverage

Version 0.3.0 (released 2020-10-13)

**Implemented enhancements:**

- Adds Item information action.
- Implements circulation actions
- Adds base of patron session.
- Uses pycountry for language management.

**Fixed bugs:**

- Missing line terminator to tell to client that all bytes are sent.

Version 0.2.0 (released 2020-08-10)

**Implemented enhancements:**

- Implements Patron information action.
- Adds Remote ILS handlers configuration.

Version 0.1.0 (released 2020-05-25)

- Base of automated circulation system.
