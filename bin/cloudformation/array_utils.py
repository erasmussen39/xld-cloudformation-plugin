#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


class ArrayUtil(object):

    @staticmethod
    def must_find_by_attr(source, attr_name, attr_value):
        return ArrayUtil.find(source, lambda a: a[attr_name].lower() == attr_value.lower())

    @staticmethod
    def find_by_attr(source, attr_name, attr_value):
        return ArrayUtil.find(source, lambda a: a[attr_name].lower() == attr_value.lower(), must_exist=False)

    @staticmethod
    def must_find(source, value):
        return ArrayUtil.find(source, lambda a: a.lower() == value.lower())

    @staticmethod
    def find(source, lamda_func, must_exist=True):
        result = [i for i in source if lamda_func(i)]
        arr_size = len(result)
        if arr_size == 1:
            return result[0]
        elif arr_size == 0:
            if must_exist:
                raise Exception("Expected to find single item but found none. Available values are [%s]" % source)
            else:
                return None
        else:
            raise Exception("Expected to find single item but found %s instead." % arr_size)
