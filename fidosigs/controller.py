#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FIDO: Format Identifier for Digital Objects.

Copyright 2010 The Open Preservation Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Flask application routes for E-ARK Python IP Validator.
"""
import logging
import os
from xml.etree.ElementTree import Element, SubElement, tostring
import importlib_resources

from flask import render_template, send_from_directory
from werkzeug.exceptions import BadRequest, Forbidden, NotFound, InternalServerError

from fidosigs.app import APP

ROUTES = True

XML_MIME = 'text/xml'
XML_APP_MIME = 'application/xml'


@APP.route("/")
def services():
    """Return a list of the available services as XML."""
    services_xml = Element('services')
    SubElement(services_xml, 'format', url='format')
    SubElement(services_xml, 'container', url='container')
    return tostring(services_xml)


@APP.route("/format/")
def formats():
    """Return a list of the available services as XML."""
    format_xml = Element('format')
    sigs = SubElement(format_xml, 'signatures')
    for sigdir in _get_sig_dirs():
        SubElement(sigs, 'signature', version=sigdir)
    return tostring(format_xml)


@APP.route("/format/latest/")
def latest_ver():
    """Return the latest sig file version number."""
    latest = ''
    for sigdir in _get_sig_dirs():
        latest = _latest(latest, sigdir)
    return tostring(Element('signature', version=latest))


@APP.route("/format/<string:version>/")
def version_details(version):
    """Return a list of the available services as XML."""
    ver_dir = _get_sig_dir(version)
    logging.debug('Version {} dir is {}'.format(version, ver_dir))
    if ver_dir is None:
        return {'message': 'No sig files found for version {}'.format(version)}, 404
    version_xml = Element('signature', version=version)
    SubElement(version_xml, 'droid', url='DROID_SignatureFile-{}.xml'.format(version))
    SubElement(version_xml, 'formats', url='formats-{}.xml'.format(version))
    SubElement(version_xml, 'pronom', url='pronom-xml-{}.zip'.format(version))
    return tostring(version_xml)


@APP.route("/format/<string:version>/<string:action>/")
def version_collatoral(version, action):
    """Return the appropriate resource file."""
    if version.lower() == 'latest':
        version = ''
        for sigdir in _get_sig_dirs():
            version = _latest(version, sigdir)
    ver_dir = _get_sig_dir(version)
    if ver_dir is None:
        return {'message': 'No resources found for version {}, action {}'.format(version, action)}, 404
    logging.debug('Version {} dir is {} for action {}'.format(version, ver_dir, action))
    if action.lower() == 'droid':
        logging.debug("Sending DROID")
        return send_from_directory(ver_dir, 'DROID_SignatureFile-v{}.xml'.format(version))
    if action.lower() == 'pronom':
        logging.debug("Sending PRONOM")
        return send_from_directory(ver_dir, 'pronom-xml-v{}.zip'.format(version))
    if action.lower() == 'fido':
        logging.debug("Sending FIDO")
        return send_from_directory(ver_dir, 'formats-v{}.xml'.format(version))
    return {'message': 'No resources found for version {}, action {}'.format(version, action)}, 404


def _latest(latest, to_compare):
    if not latest:
        return to_compare
    if not to_compare:
        return latest
    lat_ver = _remove_prefix(latest, 'v')
    comp_ver = _remove_prefix(to_compare, 'v')
    return latest if int(lat_ver) > int(comp_ver) else to_compare


def _remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def _get_sig_dirs():
    dirs = []
    root = str(importlib_resources.files('fidosigs.resources').joinpath('format'))
    for _, subdirs, _ in os.walk(root):
        for subdir in subdirs:
            if str(subdir).startswith('v'):
                dirs.append(str(subdir))
    return dirs


def _get_sig_dir(version):
    if not version.startswith('v'):
        version = 'v' + version
    root = str(importlib_resources.files('fidosigs.resources').joinpath('format'))
    for _, subdirs, _ in os.walk(root):
        for subdir in subdirs:
            if str(subdir) == version:
                return os.path.join(root, subdir)
    return None


@APP.route("/containers/")
def containers():
    """Return a list of the available services as XML."""
    services_xml = Element('services')
    SubElement(services_xml, 'signature', url='signature')
    SubElement(services_xml, 'container', url='container')
    return tostring(services_xml)


@APP.teardown_appcontext
def shutdown_session(exception=None):
    """Tear down the database session."""
    if exception:
        logging.warning("Shutting down database session with exception.")


if __name__ == "__main__":
    APP.run(host='0.0.0.0', threaded=True)
