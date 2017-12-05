#
# Copyright 2018 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


from cloudformation import create_session
from cloudformation.array_utils import ArrayUtil as arr
from boto3.session import Session
import time

# TODO: for create_stack, should it wait and process output variables?  Or should it some later process
# run describe_stack to get the output; e.g. when something later deployes to the stack?  Or maybe
# we don't care about output variables?

class CFClient(object):
    def __init__(self, access_key, access_secret, region):
        self.session = Session(aws_access_key_id=access_key,
                               aws_secret_access_key=access_secret,
                               botocore_session=create_session())
        self.cf_client = self.session.client('cloudformation', region_name=region)
        self.s3_client = self.session.client('s3', region_name=region)


    @staticmethod
    def new_instance(container):
        return CFClient(container.account.accesskey, container.account.accessSecret, container.region)


    def stack_exists(self, name):
        stacks = self.cf_client.list_stacks()['StackSummaries']
        return arr.find_by_attr(stacks, 'StackName', name) is not None


    def create_stack(self, deployed):
        if not self.stack_exists(deployed.name):
            # get content of cf file
            with open(deployed.file.path, 'r') as tfile:
                template=tfile.read()

            parameters = []
            for k in deployed.inputVariables:
                param = {}
                param['ParameterKey'] = k
                param['ParameterValue'] = deployed.inputVariables[k]
                parameters.append(param)

            self.cf_client.create_stack(StackName=deployed.name, TemplateBody=template, Parameters=parameters)
            return True
        return False


    def describe_stack(self, deployed):
        if self.stack_exists(deployed.name):
            return self.cf_client.describe_stacks(StackName=deployed.name)
        return None


    def destroy_stack(self, deployed, wait=True, sleep_interval=5):
        if self.stack_exists(deployed.name):
            self.cf_client.delete_stack(StackName=deployed.name)

            self.wait_for_terminated_status(deployed)

            return True
        return False


    def wait_for_ready_status(self, deployed, sleep_interval=5):
        ready_statuses = ['CREATE_COMPLETE', 'UPDATE_COMPLETE']
        stopped_statuses = ['CREATE_FAILED', 'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE']
        wait_statuses = ['CREATE_IN_PROGRESS', 'ROLLBACK_IN_PROGRESS', 'DELETE_IN_PROGRESS', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_IN_PROGRESS', 'REVIEW_IN_PROGRESS']

        while True:
            stack_status = self.describe_stack(deployed)['StackStatus']
            if stack_status in ready_statuses:
                return True
            elif stack_status in stopped_statuses:
                raise Exception("Expected stack [%s] to be 'Complete', but was '%s'" % (deployed.name, stack_status))
            elif stack_status in wait_statuses:
                time.sleep(sleep_interval)
            else:
                raise Exception("Unknown stack status '%s'" % stack_status)


    def wait_for_terminated_status(self, deployed, sleep_interval=5):
        stopped_statuses = ['DELETE_COMPLETE']
        failed_statuses = ['CREATE_FAILED', 'DELETE_FAILED', 'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE']
        wait_statuses = ['CREATE_IN_PROGRESS', 'ROLLBACK_IN_PROGRESS', 'DELETE_IN_PROGRESS', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_IN_PROGRESS', 'REVIEW_IN_PROGRESS']

        while True:
            stack_status = self.describe_stack(deployed)['StackStatus']
            if stack_status in stopped_statuses:
                return True
            elif stack_status in failed_statuses:
                raise Exception ("Stack termination failed with '%s'" % stack_status)
            elif stack_status in wait_statuses:
                time.sleep(sleep_interval)
            else:
                raise Exception("Unknown stack status '%s'" % stack_status)

