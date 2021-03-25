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
    along with this program. If not, see <http://www.gnu.org/licenses/>.

Changes
=======
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
