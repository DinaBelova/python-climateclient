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

import datetime
import json
import os
import re

from climateclient import exception


HEX_ELEM = '[0-9A-Fa-f]'
UUID_PATTERN = '-'.join([HEX_ELEM + '{8}', HEX_ELEM + '{4}',
                         HEX_ELEM + '{4}', HEX_ELEM + '{4}',
                         HEX_ELEM + '{12}'])


def env(*args, **kwargs):
    """Returns the first environment variable set.

    if none are non-empty, defaults to '' or keyword arg default.
    """
    for v in args:
        value = os.environ.get(v)
        if value:
            return value
    return kwargs.get('default', '')


def to_primitive(value):
    if isinstance(value, list) or isinstance(value, tuple):
        o = []
        for v in value:
            o.append(to_primitive(v))
        return o
    elif isinstance(value, dict):
        o = {}
        for k, v in value.iteritems():
            o[k] = to_primitive(v)
        return o
    elif isinstance(value, datetime.datetime):
        return str(value)
    elif hasattr(value, 'iteritems'):
        return to_primitive(dict(value.iteritems()))
    elif hasattr(value, '__iter__'):
        return to_primitive(list(value))
    else:
        return value


def dumps(value, indent=None):
    try:
        return json.dumps(value, indent=indent)
    except TypeError:
        pass
    return json.dumps(to_primitive(value))


def get_item_properties(item, fields, mixed_case_fields=None, formatters=None):
    """Return a tuple containing the item properties.

    :param item: a single item resource (e.g. Server, Tenant, etc)
    :param fields: tuple of strings with the desired field names
    :param mixed_case_fields: tuple of field names to preserve case
    :param formatters: dictionary mapping field names to callables
       to format the values
    """
    row = []
    if mixed_case_fields is None:
        mixed_case_fields = []
    if formatters is None:
        formatters = {}

    for field in fields:
        if field in formatters:
            row.append(formatters[field](item))
        else:
            if field in mixed_case_fields:
                field_name = field.replace(' ', '_')
            else:
                field_name = field.lower().replace(' ', '_')
            if not hasattr(item, field_name) and isinstance(item, dict):
                data = item[field_name]
            else:
                data = getattr(item, field_name, '')
            if data is None:
                data = ''
            row.append(data)
    return tuple(row)


def find_resource_id_by_name_or_id(client, resource, name_or_id):
    resource_manager = getattr(client, resource)
    is_id = re.match(UUID_PATTERN, name_or_id)
    if is_id:
        resources = resource_manager.list()
        for resource in resources:
            if resource['id'] == name_or_id:
                return name_or_id
        raise exception.ClimateClientException('No %s found with ID %s' %
                                               (resource, name_or_id))
    return _find_resource_id_by_name(client, resource, name_or_id)


def _find_resource_id_by_name(client, resource, name):
    resource_manager = getattr(client, resource)
    resources = resource_manager.list()

    named_resources = []

    for resource in resources:
        if resource['name'] == name:
            named_resources.append(resource['id'])
    if len(named_resources) > 1:
        raise exception.NoUniqueMatch(message="There are more than one "
                                              "appropriate resources for the "
                                              "name '%s' and type '%s'" %
                                              (name, resource))
    elif len(named_resources) == 0:
        message = "Unable to find %s with name '%s'" % (resource, name)
        raise exception.ClimateClientException(message=message,
                                               status_code=404)
    else:
        return named_resources[0]
