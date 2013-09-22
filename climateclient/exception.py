# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class ClimateClientException(Exception):
    """Base exception class."""
    message = "An unknown exception occurred %s."
    code = 500

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            message = self.message % kwargs

        super(ClimateClientException, self).__init__(message)


class CommandError(ClimateClientException):
    """Occurs if not all authentication vital options are set."""
    message = "You have to provide all options like user name or tenant id " \
              "to make authentication possible."


class NotAuthorized(ClimateClientException):
    """HTTP 401 - Not authorized.

    User have no enough rights to perform action.
    """
    code = 401
    message = "Not authorized request."


class NoClimateEndpoint(ClimateClientException):
    """Occurs if no endpoint for Climate set in the Keystone."""
    message = "No publicURL endpoint for Climate found. Set endpoint for " \
              "Climate in the Keystone"


class NoUniqueMatch(ClimateClientException):
    """Occurs if there are more than one appropriate resources."""
    code = 409
