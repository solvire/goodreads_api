'''
Created on Jan 24, 2015

@author: SS
'''
import json
import logging
import xmltodict
from dicttoxml import dicttoxml

class GRResponse:
    
    content_type = 'text'
    content = ''
    content_types = ['xml','Response','json','text']
    _logger = None
    
    def __init__(self,content,content_type):
        self.content_type = content_type
        if content_type == 'xml':
            self.content = content.encode('utf8')
        else:
            self.content = content
        self._logger = logging.getLogger(__name__)
    
    def set_content_type(self,content_type):
        self.content_type = content_type
        
    def get_content_type(self):
        return self.content_type
        
    def set_content(self,content):
        self.content = content
    
    def get_content(self):
        return self.content
    
    def get_content_types(self):
        return self.content_types
    
    
class ResponseFormatter:
    """ All the various response types"""
    response_types = []
    _logger = None
    
    def __init__(self):
        self.response_types = GRResponse.content_types
        self._logger = logging.getLogger(__name__)
        return
    
    def get_formatted_response(self,response,output_type):
        """
        Gets the form of the response and returns back the type as a string
        
        """
        if(response is None):
            raise Exception("Invalid response type None")

        response_content_type = response.headers['content-type']
        
        self._logger.info('In Formatting - with ' + response_content_type + ' and ' + output_type)
        #TODO need to set up a check on the content type incase we fibbing 
        
        if output_type == 'xml':
            print("Returning the xml type")
            return response.text
        
        if output_type == 'json':
            print("Returning the json type")
            return json.dumps(xmltodict.parse(response.text))
        
        if output_type == 'dict':
            print("Returning dict type")
            return xmltodict.parse(response.text)
        