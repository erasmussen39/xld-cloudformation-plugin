#
# Copyright 2017 XEBIALABS
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
            while self.stack_exists(deployed.name) and wait:
                time.sleep(sleep_interval)
            return True
        return False

    # def log_events(self, env_id, event_log):
    #     response = self.cf_client.describe_events(StackName=self.deployed.application_name,
    #                                               EnvironmentId=env_id)
    #     events = sorted(response["Events"], key=lambda x: x["EventDate"])
    #     for e in events:
    #         if e["EventDate"] not in event_log:
    #             event_log.append(e["EventDate"])
    #             print "%s: %s" % (e["EventDate"], e["Message"])
    #     return event_log

    def wait_for_ready_status(self, env_id, sleep_interval=5):
        ready_statuses = ['CREATE_COMPLETE', 'UPDATE_COMPLETE']
        stopped_statuses = ['CREATE_FAILED', 'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE']
        wait_statuses = ['CREATE_IN_PROGRESS', 'ROLLBACK_IN_PROGRESS', 'DELETE_IN_PROGRESS', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_IN_PROGRESS', 'REVIEW_IN_PROGRESS']

        event_log = []
        while True:
            # self.log_events(env_id, event_log)
            stack_status = self.describe_stack()['StackStatus']
            if stack_status in ready_statuses:
                return True
            elif stack_status in stopped_statuses:
                raise Exception("Expected environment [%s] to be in 'Ready' state, but was '%s'" % (env_id, stack_status))
            elif stack_status in wait_statuses:
                time.sleep(sleep_interval)
            else:
                raise Exception("Unknown environment status '%s'" % stack_status)

    def wait_for_terminated_status(self, env_id, sleep_interval=5):
        stopped_statuses = ['DELETE_COMPLETE']
        failed_statuses = ['CREATE_FAILED', 'DELETE_FAILED', 'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE']
        wait_statuses = ['CREATE_IN_PROGRESS', 'ROLLBACK_IN_PROGRESS', 'DELETE_IN_PROGRESS', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_IN_PROGRESS', 'REVIEW_IN_PROGRESS']
        event_log = []
        while True:
            # self.log_events(env_id, event_log)
            stack_status = self.describe_stack()['StackStatus']
            if stack_status in stopped_statuses:
                return True
            elif stack_status in failed_statuses:
                raise Exception ("Stack termination failed with '%s'" % stack_status)
            elif stack_status in wait_statuses:
                time.sleep(sleep_interval)
            else:
                raise Exception("Unknown environment status '%s'" % stack_status)


    # def prepare_options(self, stack_vars):
    #     # http://docs.aws.amazon.com/cloudformation/latest/dg/command-options-general.html#command-options-general-ec2vpc
    #     options = []

    #     def add_option(ns, name, value):
    #         if value is not None and len(value.strip()) > 0:
    #             options.append({"Namespace": ns, "OptionName": name, "Value": value})

    #     o = self.deployed
    #     add_option("aws:autoscaling:launchconfiguration", "IamInstanceProfile", o.iamInstanceProfile)
    #     add_option("aws:autoscaling:launchconfiguration", "InstanceType", o.instanceType)
    #     add_option("aws:autoscaling:updatepolicy:rollingupdate", "RollingUpdateType", o.rollingUpdateType)
    #     add_option("aws:autoscaling:updatepolicy:rollingupdate", "RollingUpdateEnabled", o.rollingUpdateEnabled)
    #     add_option("aws:cloudformation:command", "BatchSize", o.batchSize)
    #     add_option("aws:cloudformation:command", "BatchSizeType", o.batchSizeType)
    #     add_option("aws:cloudformation:environment", "ServiceRole", o.serviceRole)
    #     add_option("aws:cloudformation:healthreporting:system", "SystemType", o.systemType)
    #     add_option("aws:elb:loadbalancer", "CrossZone", o.crossZone)
    #     add_option("aws:elb:policies", "ConnectionDrainingEnabled", o.connectionDrainingEnabled)

    #     add_option("aws:ec2:vpc", "VPCId", o.vpcId)
    #     add_option("aws:ec2:vpc", "Subnets", o.subnets)
    #     add_option("aws:ec2:vpc", "ELBSubnets", o.elbSubnets)
    #     add_option("aws:ec2:vpc", "ELBScheme", o.elbScheme)
    #     add_option("aws:ec2:vpc", "DBSubnets", o.dbSubnets)
    #     add_option("aws:ec2:vpc", "AssociatePublicIpAddress", o.associatePublicIpAddress)

    #     if len(stack_vars.keys()) > 0:
    #         for k, v in stack_vars.items():
    #             add_option("aws:cloudformation:application:environment", k, v)
    #     return options

    @staticmethod
    def not_empty(value):
        return value is not None and len(value.strip()) > 0

    # def prepare_env_details(self, stack_vars, is_update=False):
    #     def add_detail(name, value, target):
    #         if self.not_empty(value):
    #             target[name] = value

    #     o = self.deployed
    #     details = {}
    #     add_detail("StackName", o.name, details)
    #     add_detail("Description", o.description, details)
    #     add_detail("StackSetName", o.set_name, details)

    #     if self.not_empty(o.tier_name) or self.not_empty(o.tier_type) or self.not_empty(o.tier_version):
    #         tier = {}
    #         add_detail("Name", o.tier_name, tier)
    #         add_detail("Type", o.tier_type, tier)
    #         add_detail("Version", o.tier_version, tier)
    #         details["Tier"] = tier

    #     if not is_update:
    #         tags = []
    #         for k, v in o.env_tags.items():
    #             tags.append({"Key": k, "Value": v})
    #         details["Tags"] = tags
    #     details["OptionSettings"] = self.prepare_options(stack_vars)
    #     return details


    # def bucket_exists(self):
    #     buckets = self.s3_client.list_buckets()["Buckets"]
    #     return arr.find_by_attr(buckets, 'Name', self.deployed.s3_bucket_name) is not None

    # def create_bucket_if_needed(self):
    #     if not self.bucket_exists():
    #         self.s3_client.create_bucket(ACL='private', Bucket=self.deployed.s3_bucket_name,
    #                                      CreateBucketConfiguration={'LocationConstraint': self.deployed.region})

    # def delete_bucket(self):
    #     if self.bucket_exists():
    #         self.s3_client.delete_bucket(Bucket=self.deployed.s3_bucket_name)

    # def upload_artifact(self, name, version, source_file_path):
    #     target_name = self.create_target_file_name(name, version)
    #     self.create_bucket_if_needed()
    #     response = self.s3_client.list_objects(Bucket=self.deployed.s3_bucket_name)
    #     if "Contents" in response.keys():
    #         contents = response["Contents"]
    #     else:
    #         contents = []
    #     if not arr.find_by_attr(contents, 'Key', target_name):
    #         with open(source_file_path, 'rb') as data:
    #             self.s3_client.put_object(Bucket=self.deployed.s3_bucket_name, Key=target_name, Body=data)
    #         return True
    #     return False

    # @staticmethod
    # def create_target_file_name(name, version):
    #     name = name.replace(" ", "_")
    #     target_name = "%s-%s.zip" % (name, version)
    #     return target_name

    # def delete_artifact(self, name, version):
    #     target_name = self.create_target_file_name(name, version)
    #     contents = self.s3_client.list_objects(Bucket=self.deployed.s3_bucket_name)["Contents"]
    #     if arr.find_by_attr(contents, 'Key', target_name):
    #         self.s3_client.delete_object(Bucket=self.deployed.s3_bucket_name, Key=target_name)
    #         return True
    #     return False

    # def application_version_exists(self, version):
    #     application_versions = self.cf_client.describe_application_versions(
    #         ApplicationName=self.deployed.application_name)['ApplicationVersions']
    #     return arr.find_by_attr(application_versions, 'VersionLabel', version) is not None

    # def get_application_version(self, version_label):
    #     result = self.cf_client.describe_application_versions(ApplicationName=self.deployed.application_name,
    #                                                           VersionLabels=[version_label])
    #     versions = result["ApplicationVersions"]
    #     result_size = len(versions)
    #     if result_size != 1:
    #         raise Exception("Application version '%s' not found for Application '%s'. Instances found %s" %
    #                         (version_label, self.deployed.application_name, result_size))
    #     return versions[0]

    # def wait_for_application_version_proccessed_status(self, version_label, sleep_interval=5):
    #     ready_statuses = ['processed', 'unprocessed']
    #     stopped_statuses = ['failed']
    #     wait_statuses = ['processing', 'building']
    #     while True:
    #         version_status = self.get_application_version(version_label)['Status'].lower()
    #         if version_status in ready_statuses:
    #             return True
    #         elif version_status in stopped_statuses:
    #             raise Exception("Expected application version [%s] to be in 'Processed' state, but was '%s'"
    #                             % (version_label, version_status))
    #         elif version_status in wait_statuses:
    #             time.sleep(sleep_interval)
    #         else:
    #             raise Exception("Unknown application version status '%s'" % version_status)

    # @staticmethod
    # def version_label(name, version):
    #     return "%s-%s" % (name, version)

    # def create_application_version(self, name, version, wait=True, sleep_interval=5):
    #     version_label = self.version_label(name, version)
    #     created = False
    #     target_file = self.create_target_file_name(name, version)
    #     if not self.application_version_exists(version_label):
    #         self.cf_client.create_application_version(
    #                                 ApplicationName=self.deployed.application_name,
    #                                 VersionLabel=version_label,
    #                                 SourceBundle={
    #                                     'S3Bucket': self.deployed.s3_bucket_name,
    #                                     'S3Key': target_file
    #                                 })
    #         created = True
    #     else:
    #         self.get_application_version(version_label)

    #     if wait:
    #         self.wait_for_application_version_proccessed_status(version_label, sleep_interval=sleep_interval)
    #     return [created, version_label]

