#
# Copyright 2019 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


from cloudformation import create_session
from cloudformation.array_utils import ArrayUtil as arr
from cloudformation.ci_factory import CIFactory

from boto3.session import Session
from botocore.exceptions import ClientError

import time
import re

# AWS CloudFormation client

class CFClient(object):
    def __init__(self, access_key, access_secret, region):
        self.session = Session(aws_access_key_id=access_key,
                               aws_secret_access_key=access_secret,
                               botocore_session=create_session())
        self.cf_client = self.session.client('cloudformation', region_name=region)


    @staticmethod
    def new_instance(container):
        return CFClient(container.account.accesskey, container.account.accessSecret, container.region)


    def create_stack(self, deployed):
        stackname = self._sanatize_name(deployed.name)
        if not self._stack_exists(stackname):
            # get content of cf file
            with open(deployed.file.path, 'r') as tfile:
                template=tfile.read()

            parameters = []
            for k in deployed.inputVariables:
                param = {}
                param['ParameterKey'] = k
                param['ParameterValue'] = deployed.inputVariables[k]
                parameters.append(param)

            self.cf_client.create_stack(StackName=stackname, TemplateBody=template, Parameters=parameters)
            return True
        return False


    def describe_stack(self, deployed):
        stackname = self._sanatize_name(deployed.name)
        if self._stack_exists(stackname):
            # I've seen a scenario where the stack exists as checked above
            # but describe_stacks fails with the stack not found.
            try:
                return self.cf_client.describe_stacks(StackName=stackname)['Stacks'][0]
            except ClientError, arg:
                print "WARN: Describe Stack generated exception. The stack probably doesn't exist. '%s'" % arg
                return None

        return None


    def list_resources(self, deployed):
        stackname = self._sanatize_name(deployed.name)
        if self._stack_exists(stackname):
            return self.cf_client.list_stack_resources(StackName=stackname)['StackResourceSummaries']
        return None


    def capture_output(self, deployed):
        stackname = self._sanatize_name(deployed.name)
        if self._stack_exists(stackname):
            output_variables = {}
            outputs = self.cf_client.describe_stacks(StackName=stackname)['Stacks'][0]['Outputs']
            for output in outputs:
                output_variables[output['OutputKey']] = output['OutputValue']

            deployed.outputVariables = output_variables
            return True

        return False


    def destroy_stack(self, deployed, wait=True, sleep_interval=5):
        stackname = self._sanatize_name(deployed.name)
        if self._stack_exists(stackname):
            self.cf_client.delete_stack(StackName=stackname)

            return True
        return False


    def wait_for_ready_status(self, deployed, sleep_interval=6, max_intervals=50):
        ready_statuses = ['CREATE_COMPLETE', 'UPDATE_COMPLETE']
        stopped_statuses = ['CREATE_FAILED', 'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE']
        wait_statuses = ['CREATE_IN_PROGRESS', 'ROLLBACK_IN_PROGRESS', 'DELETE_IN_PROGRESS', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_IN_PROGRESS', 'REVIEW_IN_PROGRESS']

        interval_cnt = 0
        while True:
            interval_cnt += 1
            if interval_cnt > max_intervals:
                raise Exception("Stack [%s] timed out waiting for 'Complete'" % (deployed.name))

            stack = self.describe_stack(deployed)
            if stack is None:
                time.sleep(sleep_interval)
                continue

            stack_status = stack['StackStatus']
            if stack_status in ready_statuses:
                return True
            elif stack_status in stopped_statuses:
                raise Exception("Expected stack [%s] to be 'Complete', but was '%s'" % (deployed.name, stack_status))
            elif stack_status in wait_statuses:
                time.sleep(sleep_interval)
            else:
                raise Exception("Unknown stack status '%s'" % stack_status)


    def wait_for_terminated_status(self, deployed, sleep_interval=6, max_intervals=50):
        stackname = self._sanatize_name(deployed.name)
        if not self._stack_exists(stackname):
            return False

        stopped_statuses = ['DELETE_COMPLETE']
        failed_statuses = ['CREATE_FAILED', 'DELETE_FAILED', 'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE']
        wait_statuses = ['CREATE_IN_PROGRESS', 'ROLLBACK_IN_PROGRESS', 'DELETE_IN_PROGRESS', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_IN_PROGRESS', 'REVIEW_IN_PROGRESS']

        interval_cnt = 0
        while True:
            interval_cnt += 1
            if interval_cnt > max_intervals:
                raise Exception("Stack [%s] timed out waiting for 'Delete'" % (deployed.name))
                
            stack = self.describe_stack(deployed)
            if stack is None:
                return True

            stack_status = stack['StackStatus']
            if stack_status in stopped_statuses:
                return True
            elif stack_status in failed_statuses:
                raise Exception ("Stack termination failed with '%s'" % stack_status)
            elif stack_status in wait_statuses:
                time.sleep(sleep_interval)
            else:
                raise Exception("Unknown stack status '%s'" % stack_status)


    def get_template_body(self, deployed):
        stackname = self._sanatize_name(deployed.name)
        if not self._stack_exists(stackname):
            return None

        stackname = self._sanatize_name(deployed.name)
        return self.cf_client.get_template(StackName=stackname)['TemplateBody']


    # INTERNAL FUNCTIONS =========================================================

    # AWS requires that stack names match regex [a-zA-Z][-a-zA-Z0-9]*
    def _sanatize_name(self, name):
        p = re.compile('_| |$|&|%|@|!|#')
        return p.sub('-', name)        

    # Get a list of stacks and see if any match the given name.
    def _stack_exists(self, name):
        stacks = self.cf_client.list_stacks()['StackSummaries']
        for stack in stacks:
            if 'StackName' in stack and stack['StackName'] != name:
                continue

            if 'StackStatus' not in stack or stack['StackStatus'] != 'DELETE_COMPLETE':
                # name matches and not deleted
                return True

        return False

