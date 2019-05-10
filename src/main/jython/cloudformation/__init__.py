#
# Copyright 2019 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import os
import tempfile
from java.nio.file import Files, Paths, StandardCopyOption

import com.xebialabs.deployit.plugin.aws.support.BotoLoader as BotoLoader
from botocore.session import Session


def create_session():
    boto_session = Session()
    boto_session.lazy_register_component('data_loader', lambda: create_loader())
    if 'REQUESTS_CA_BUNDLE' not in os.environ:
        ca_bundle_path = extract_file_from_jar("botocore/vendored/requests/cacert.pem")
        os.environ['REQUESTS_CA_BUNDLE'] = ca_bundle_path
    return boto_session


def create_loader():
    return Loader()


def extract_file_from_jar(config_file):
    file_url = BotoLoader.getResourceBySelfClassLoader(config_file)
    if file_url:
        tmp_file, tmp_abs_path = tempfile.mkstemp()
        tmp_file.close()
        Files.copy(file_url.openStream(), Paths.get(tmp_abs_path), StandardCopyOption.REPLACE_EXISTING)
        return tmp_abs_path

    else:
        return None


class Loader(object):
    def __init__(self):
        self._cache = {}
        self._search_paths = []

    @property
    def search_paths(self):
        return self._search_paths

    def list_available_services(self, type_name):
        return BotoLoader.listAvailableServices()

    def determine_latest_version(self, service_name, type_name):
        return max(self.list_api_versions(service_name, type_name))

    def list_api_versions(self, service_name, type_name):
        return BotoLoader.listApiVersion(service_name, type_name)

    def load_service_model(self, service_name, type_name, api_version=None):
        if api_version is None:
            api_version = self.determine_latest_version(
                service_name, type_name)
        full_path = os.path.join(service_name, api_version, type_name)
        return self.load_data(full_path)

    def load_data(self, name):
        import json

        return json.loads(BotoLoader.loadFile(name))


# Botocore looks for the HOME variable but UNIX init.d service doesn't pass environment variables.
# The script breaks if it doesn't find the variable, thus setting it externally.

if 'HOME' not in os.environ:
    os.environ['HOME'] = os.getenv('xldeploy_home', '/')
