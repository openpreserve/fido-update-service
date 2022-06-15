#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FIDO Signature service.

Copyright 2022 The Open Preservation Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

FastAPI application routes for the FIDO sig service.
"""
import logging
import os
from xml.etree.ElementTree import Element, SubElement, tostring
import importlib_resources

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse, PlainTextResponse 

APP = FastAPI()

XML_MIME = 'text/xml'
XML_APP_MIME = 'application/xml'

class XMLResponse(Response):
    media_type = XML_APP_MIME

@APP.get(
    "/",
    response_class=XMLResponse
)
def root() -> XMLResponse:
    """Return a list of the available services as XML."""
    services_xml = Element('services')
    SubElement(services_xml, 'format', url='format')
    SubElement(services_xml, 'container', url='container')
    return tostring(services_xml, encoding='utf8', method='xml')

@APP.get(
    "/format",
    response_class=XMLResponse
)
def formats() -> XMLResponse:
    """Return a list of the available format signature files as XML."""
    format_xml = Element('format')
    sigs = SubElement(format_xml, 'signatures')
    for sigdir in _get_sig_dirs():
        SubElement(sigs, 'signature', version=sigdir)
    return tostring(format_xml, encoding='utf8', method='xml')


@APP.get(
    "/format/latest",
    response_class=XMLResponse
)
def latest_ver() -> XMLResponse:
    """Return the latest available format signature file version number as XML."""
    latest = ''
    for sigdir in _get_sig_dirs():
        latest = _latest(latest, sigdir)
    format_xml = Element('signature', version=latest)
    return tostring(format_xml, encoding='utf8', method='xml')


@APP.get(
    "/format/{version}",
    response_class=XMLResponse
)
def version_details(version) -> XMLResponse:
    """List the file resources available for a particualr version as XML."""
    ver_dir = _get_sig_dir(version)
    logging.debug('Version {} dir is {}'.format(version, ver_dir))
    if ver_dir is None:
        raise HTTPException (status_code=404, detail='No sig files found for version {}'.format(version))
    version_xml = Element('signature', version=version)
    SubElement(version_xml, 'droid', url='DROID_SignatureFile-{}.xml'.format(version))
    SubElement(version_xml, 'formats', url='formats-{}.xml'.format(version))
    SubElement(version_xml, 'pronom', url='pronom-xml-{}.zip'.format(version))
    return tostring(version_xml, encoding='utf8', method='xml')


@APP.get(
    "/format/{version}/{action}",
    response_class=FileResponse
)
def version_collatoral(version, action) -> FileResponse:
    """Return the appropriate resource file for version parameter, or latest for latest.
       Action can be one of fido | droid | pronom.
    """
    if version.lower() == 'latest':
        version = ''
        for sigdir in _get_sig_dirs():
            version = _latest(version, sigdir)
    ver_dir = _get_sig_dir(version)
    if ver_dir is None or action.lower() not in ['droid', 'pronom', 'fido']:
        message = 'No resources found for version {}, action {}'.format(version, action)
        logging.info(message)
        raise HTTPException (status_code=404, detail=message)
    logging.debug('Version {} dir is {} for action {}'.format(version, ver_dir, action))
    filename = 'formats-v{}.xml'.format(version)
    if action.lower() == 'droid':
        logging.debug("Sending DROID")
        filename = 'DROID_SignatureFile-v{}.xml'.format(version)
    elif action.lower() == 'pronom':
        logging.debug("Sending PRONOM")
        filename = 'pronom-xml-v{}.zip'.format(version)
    else:
        logging.debug("Sending FIDO")
    return FileResponse(os.path.join(ver_dir, filename), filename=filename)


@APP.get(
    "/container/",
    responses={
      200: {
          "content": {XML_APP_MIME: {}},
      }
    },
)
def containers() -> XMLResponse:
    """Return a list of the available services as XML."""
    services_xml = Element('services')
    SubElement(services_xml, 'signature', url='signature')
    SubElement(services_xml, 'container', url='container')
    return tostring(services_xml, encoding='utf8', method='xml')


def _latest(latest: str, to_compare: str) -> str:
    """Return the most recent version number of latest and to_compare."""
    if not latest:
        return to_compare
    if not to_compare:
        return latest
    lat_ver = _remove_prefix(latest)
    comp_ver = _remove_prefix(to_compare)
    return latest if int(lat_ver) > int(comp_ver) else to_compare


def _remove_prefix(text: str, prefix: str='v') -> str:
    """Return the value text with a single prefix character removed if present."""
    return text[len(prefix):] if text.startswith(prefix) else text


def _get_sig_dirs():
    dirs = []
    root = str(importlib_resources.files('fidosigs.resources').joinpath('format'))
    for _, subdirs, _ in os.walk(root):
        for subdir in subdirs:
            if str(subdir).startswith('v'):
                dirs.append(str(subdir))
    return dirs


def _get_sig_dir(version: str):
    if not version.startswith('v'):
        version = 'v' + version
    root = str(importlib_resources.files('fidosigs.resources').joinpath('format'))
    for _, subdirs, _ in os.walk(root):
        for subdir in subdirs:
            if str(subdir) == version:
                return os.path.join(root, subdir)
    return None


if __name__ == "__main__":
    APP.run(host='0.0.0.0', threaded=True)
