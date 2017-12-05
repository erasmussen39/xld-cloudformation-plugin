#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


import os
import json
from java.io import File


def load_test_resource(file_path):
    with open("src/test/resources/%s" % file_path, "r") as data_file:
        return data_file.read()


class ItestConf(object):

    def __init__(self):
        file_location = os.getenv('itest_conf_file')
        if not file_location:
            raise Exception("No environment variable named 'itest_conf_file' set." +
                            " This variable should point to the file containing connection info.")

        with open(file_location) as data_file:
            data = json.load(data_file)
        self.settings = {o['name']: o for o in data}

    def apply_settings(self, name, target, expects_params):
        if name not in self.settings:
            raise Exception("'%s' is not found in the itest_conf_file" % name)
        settings = self.settings[name]
        for k, v in settings.items():
            target.__dict__[k] = v
        for p in expects_params:
            if target.__dict__[p] is None:
                raise Exception("%s is a required property missing from '%s' in the itest_conf_file" % (p, name))


itest_conf = ItestConf()


class CiStub(object):

    def getProperty(self, name):
        return self.__dict__[name]

    def setProperty(self, name, value):
        self.__dict__[name] = value

    def __getitem__(self, key):
        return self.__dict__[key]


class Ci(CiStub):
    def __init__(self, parent, name, ci_type):
        self.name = name
        self.id = "%s/%s" % (parent, self.name)
        self.type = ci_type


class AwsCloudCi(Ci):
    def __init__(self):
        super(AwsCloudCi, self).__init__("Infrastructure", "aws_cloud", "aws.Cloud")
        itest_conf.apply_settings("aws_cloud", self, ["accesskey", "accessSecret"])


class ApplicationEnvironmentCi(Ci):
    def __init__(self):
        self.account = AwsCloudCi()
        super(ApplicationEnvironmentCi, self).__init__(self.account.id, "app_env", "cf.ApplicationEnvironment")
        self.region = "eu-central-1"
        self.application_name = "EBPluginTestApp"
        self.environment_name = "test"
        self.stack_name = "64bit Amazon Linux 2017.03 v4.3.0 running Node.js"
        self.s3_bucket_name = "cloudformation-plugin-test-eu-central-1"
        self.iamInstanceProfile = "aws-cloudformation-ec2-role"
        self.description = "test environment"
        self.cname_prefix = None
        self.tier_name = None
        self.tier_type = None
        self.tier_version = None
        self.env_tags = {"mytag": "mytagvalue"}
        self.instanceType = None
        self.rollingUpdateType = None
        self.rollingUpdateEnabled = None
        self.batchSize = None
        self.batchSizeType = None
        self.serviceRole = "aws-cloudformation-service-role"
        self.systemType = None
        self.crossZone = None
        self.connectionDrainingEnabled = None
        self.vpcId = None
        self.subnets = None
        self.elbSubnets = None
        self.elbScheme = None
        self.dbSubnets = None
        self.associatePublicIpAddress = None


class ApplicationBundleCi(Ci):
    def __init__(self):
        self.container = ApplicationEnvironmentCi()
        super(ApplicationBundleCi, self).__init__("Applications/TestApp/1.0", "my_app", "cf.ApplicationVersion")
        self.file = File("./src/test/resources/nodejs-v1.zip")
        self.stack_version = "v1"
        self.stack_vars = {"SomeVar": "SomeVarValue"}

