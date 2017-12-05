#
# Copyright 2018 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


import unittest
from itests import ApplicationEnvironmentCi, ApplicationBundleCi
from cloudformation.cf_client import CFClient

from cf_rules import create_application, delete_application, delete_environment, list_solution_stacks
from cf_rules import deploy_application, undeploy_application


class CFClientTest(unittest.TestCase):

    def setUp(self):
        app_env_ci = ApplicationEnvironmentCi()
        deployed = ApplicationBundleCi()
        self.client = CFClient.new_instance(app_env_ci)
        self.task_vars = {"thisCi": app_env_ci}
        self.deployment_vars = {"deployed": deployed, "previousDeployed": deployed, "appVersion": "1.0"}

    def tearDown(self):
        self.client.delete_application()

    def test_control_tasks(self):
        list_solution_stacks.process(self.task_vars)
        create_application.process(self.task_vars)
        delete_environment.process(self.task_vars)
        delete_application.process(self.task_vars)

    def test_deployment(self):
        deploy_application.process(self.deployment_vars)
        undeploy_application.process(self.deployment_vars)






