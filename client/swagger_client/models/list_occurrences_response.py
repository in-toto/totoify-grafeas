# coding: utf-8

"""
    Grafeas API

    An API to insert and retrieve annotations on cloud artifacts.

    OpenAPI spec version: 0.1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from pprint import pformat
from six import iteritems
import re


class ListOccurrencesResponse(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, occurrences=None, next_page_token=None):
        """
        ListOccurrencesResponse - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'occurrences': 'list[Occurrence]',
            'next_page_token': 'str'
        }

        self.attribute_map = {
            'occurrences': 'occurrences',
            'next_page_token': 'nextPageToken'
        }

        self._occurrences = occurrences
        self._next_page_token = next_page_token

    @property
    def occurrences(self):
        """
        Gets the occurrences of this ListOccurrencesResponse.
        The occurrences requested.

        :return: The occurrences of this ListOccurrencesResponse.
        :rtype: list[Occurrence]
        """
        return self._occurrences

    @occurrences.setter
    def occurrences(self, occurrences):
        """
        Sets the occurrences of this ListOccurrencesResponse.
        The occurrences requested.

        :param occurrences: The occurrences of this ListOccurrencesResponse.
        :type: list[Occurrence]
        """

        self._occurrences = occurrences

    @property
    def next_page_token(self):
        """
        Gets the next_page_token of this ListOccurrencesResponse.
        The next pagination token in the List response. It should be used as page_token for the following request. An empty value means no more results.

        :return: The next_page_token of this ListOccurrencesResponse.
        :rtype: str
        """
        return self._next_page_token

    @next_page_token.setter
    def next_page_token(self, next_page_token):
        """
        Sets the next_page_token of this ListOccurrencesResponse.
        The next pagination token in the List response. It should be used as page_token for the following request. An empty value means no more results.

        :param next_page_token: The next_page_token of this ListOccurrencesResponse.
        :type: str
        """

        self._next_page_token = next_page_token

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
