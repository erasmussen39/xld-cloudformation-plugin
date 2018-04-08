#
# Copyright 2018 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


from cloudformation.ci_factory import CIFactory
from cloudformation.cf_client import CFClient

def process(task_vars):
    deployed = task_vars['deployed']

    client = CFClient.new_instance(deployed.container)
    template_metadata = client.get_template_body(deployed)['Metadata']
    for key in template_metadata:
        if key.startswith('XLD'):
            repo_root = key[5:]
            ci_tmpl = template_metadata[key]

            ci_fact = CIFactory.new_instance(repositoryService, metadataService, repo_root, ci_tmpl, deployed.outputVariables)
            ci_fact.createCis()

    print "Done"


if __name__ == '__main__' or __name__ == '__builtin__':
    process(locals())
