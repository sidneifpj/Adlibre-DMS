"""
Module: MDTUI tests
Project: Adlibre DMS
Copyright: Adlibre Pty Ltd 2012
License: See LICENSE for license information
Author: Iurii Garmash
"""

import json, os, urllib, datetime
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings
import re

# auth user
username = 'admin'
password = 'admin'

couchdb_url = 'http://127.0.0.1:5984'

test_mdt_docrule_id = 2 # should be properly assigned to fixtures docrule that uses CouchDB plugins

indexes_form_match_pattern = '(Employee ID|Employee Name|Friends ID|Friends Name|Required Date).+?name=\"(\d+)\"'

mdt1 = {
    "_id": 'mdt1',
    "docrule_id": [str(test_mdt_docrule_id),],
    "description": "Test MDT Number 1",
    "fields": {
       "1": {
           "type": "integer",
           "field_name": "Friends ID",
           "description": "ID of Friend for tests"
       },
       "2": {
           "type": "string",
           "length": 60,
           "field_name": "Friends Name",
           "description": "Name of tests person"
       },
       "3": {
           "type": "date",
           "field_name": "Required Date",
           "description": "Testing Date Type Secondary Key"
       },
    },
    "parallel": {
       "1": [ "1", "2"],
    }
}

mdt2 = {
    "_id": 'mdt2',
    "docrule_id": [str(test_mdt_docrule_id),],
    "description": "Test MDT Number 2",
    "fields": {
       "1": {
           "type": "integer",
           "field_name": "Employee ID",
           "description": "Unique (Staff) ID of the person associated with the document"
       },
       "2": {
           "type": "string",
           "field_name": "Employee Name",
           "description": "Name of the person associated with the document"
       },
    },
    "parallel": {
       "1": [ "1", "2"],
    }
}

mdt3 = {
    "_id": 'mdt3',
    "docrule_id": [str(test_mdt_docrule_id),],
    "description": "Test MDT Number 1",
    "fields": {
        "1": {
            "type": "string",
            "length": 3,
            "field_name": "Reporting Entity",
            "description": "Reporting Entity (e.g. JTG, QH, etc)"
        },
        "2": {
            "type": "string",
            "length": 60,
            "field_name": "Report Type",
            "description": "Report Type (e.g. Reconciliation, Pay run etc)"
        },
        "3": {
            "type": "date",
            "field_name": "Report Date",
            "description": "Date the report was generated"
        },
    },
    "parallel": {}
}

# Static dictionary of document to be indexed.
doc1_dict = {
    'date': '2012-03-06',
    'description': 'Test Document Number 1',
    'Employee ID': '123456',
    'Required Date': '2012-03-07',
    'Employee Name': 'Iurii Garmash',
    'Friends ID': '123',
    'Friends Name': 'Andrew',
}

doc2_dict = {
    'date': '2012-03-20',
    'description': 'Test Document Number 2',
    'Employee ID': '111111',
    'Required Date': '2012-03-21',
    'Employee Name': 'Andrew Cutler',
    'Friends ID': '321',
    'Friends Name': 'Yuri',
}

doc3_dict = {
    'date': '2012-03-28',
    'description': 'Test Document Number 3',
    'Employee ID': '111111',
    'Required Date': '2012-03-29',
    'Employee Name': 'Andrew Cutler',
    'Friends ID': '222',
    'Friends Name': 'Someone',
}

doc1 = 'ADL-0001'
doc2 = 'ADL-0002'
doc3 = 'ADL-1111'

# Proper for doc1
typehead_call1 = {
                'key_name': "Friends ID",
                "autocomplete_search": "1"
                }
typehead_call2 = {
                'key_name': "Employee ID",
                "autocomplete_search": "12"
                }

# Improper for doc1
typehead_call3 = {
                'key_name': "Employee ID",
                "autocomplete_search": "And"
                }

# TODO: Expand this (especially search). Need to add at least 1 more docs...
class MDTUI(TestCase):

    def setUp(self):
        # We are using only logged in client in this test
        self.client.login(username=username, password=password)

    def test_00_setup_mdt1(self):
        """
        Setup MDT 1 for the test suite. Made like standalone test because we need it to be run only once
        """
        # adding our MDT's required through API. (MDT API should be working)
        mdt = json.dumps(mdt1)
        url = reverse('api_mdt')
        response = self.client.post(url, {"mdt": mdt})
        self.assertEqual(response.status_code, 200)

    def test_00_setup_mdt2(self):
        """
        Setup MDT 2 for the test suite. Made like standalone test because we need it to be run only once
        """
        # adding our MDT's required through API. (MDT API should be working)
        mdt = json.dumps(mdt2)
        url = reverse('api_mdt')
        response = self.client.post(url, {"mdt": mdt})
        self.assertEqual(response.status_code, 200)

    def test_00_setup_mdt3(self):
        """
        Setup MDT 3 for the test suite. Made like standalone test because we need it to be run only once
        """
        # adding our MDT's required through API. (MDT API should be working)
        mdt = json.dumps(mdt3)
        url = reverse('api_mdt')
        response = self.client.post(url, {"mdt": mdt})
        self.assertEqual(response.status_code, 200)

    def test_01_opens_app(self):
        """
        If MDTUI app opens normally at least
        """
        url = reverse('mdtui-home')
        response = self.client.get(url)
        self.assertContains(response, 'To continue, choose from the options below')
        self.assertEqual(response.status_code, 200)

    def test_02_step1(self):
        """
        MDTUI Indexing has step 1 rendered properly.
        """
        url = reverse('mdtui-index')
        response = self.client.get(url)
        self.assertContains(response, '<legend>Step 1: Select Document Type</legend>')
        self.assertContains(response, 'Adlibre Invoices')
        self.assertEqual(response.status_code, 200)
    
    def test_03_step1_post_redirect(self):
        """
        MDTUI Displays Step 2 Properly (after proper call)
        """
        url = reverse('mdtui-index-type')
        response = self.client.post(url, {'docrule': test_mdt_docrule_id})
        self.assertEqual(response.status_code, 302)
        new_url = self._retrieve_redirect_response_url(response)
        response = self.client.get(new_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<label class="control-label">Description</label>')
        self.assertContains(response, 'Creation Date')

    def test_04_indexing_step2_proper_form_rendering(self):
        """
        MDTUI renders Indexing form according to MDT's exist for testsuite's Docrule
        Step 2. Indexing Form contains MDT fields required.
        """
        # Selecting Document Type Rule
        url = reverse('mdtui-index-type')
        response = self.client.post(url, {'docrule': test_mdt_docrule_id})
        self.assertEqual(response.status_code, 302)
        # Checking Step 2 Form
        url = reverse("mdtui-index-details")
        response = self.client.get(url)
        # contains Date field
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<label class="control-label">Description</label>')
        self.assertContains(response, 'Creation Date')
        # Description field
        self.assertContains(response, 'id_description')
        # MDT based Fields:
        self.assertContains(response, "Friends ID")
        self.assertContains(response, "Required Date")
        self.assertContains(response, "ID of Friend for tests")
        self.assertContains(response, "Friends Name")
        self.assertContains(response, "Name of tests person")
        self.assertContains(response, "Employee ID")
        self.assertContains(response, "Unique (Staff) ID of the person associated with the document")
        self.assertContains(response, "Employee Name")
        self.assertContains(response, "Name of the person associated with the document")
        self.assertContains(response, "Required Date")
        self.assertContains(response, "Testing Date Type Secondary Key")

    def test_05_adding_indexes(self):
        """
        MDTUI Indexing Form parses data properly.
        Step 3 Displays appropriate indexes fro document will be uploaded.
        Posting to Indexing Step 3 returns proper data.
        """
        # Selecting Document Type Rule
        url = reverse('mdtui-index-type')
        response = self.client.post(url, {'docrule': test_mdt_docrule_id})
        self.assertEqual(response.status_code, 302)
        url = reverse("mdtui-index-details")
        # Getting indexes form and matching form Indexing Form fields names
        response = self.client.get(url)
        rows_dict = self._read_indexes_form(response)
        post_dict = self._convert_doc_to_post_dict(rows_dict, doc1_dict)
        # Adding Document Indexes
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 302)
        new_url = self._retrieve_redirect_response_url(response)
        response = self.client.get(new_url)
        # Response contains proper document indexes
        self.assertContains(response, 'Friends ID: 123')
        self.assertContains(response, 'Friends Name: Andrew')
        self.assertContains(response, 'Description: Test Document Number 1')
        self.assertContains(response, 'Creation Date: 2012-03-06')
        self.assertContains(response, 'Employee ID: 123456')
        self.assertContains(response, 'Employee Name: Iurii Garmash')
        self.assertContains(response, 'Required Date: 2012-03-07')
        # Contains Upload form
        self.assertContains(response, 'Upload File')
        self.assertContains(response, 'id_file')
        self.assertEqual(response.status_code, 200)

    def test_06_rendering_form_without_first_step(self):
        """
        Indexing Page 3 without populating previous forms contains proper warnings.
        """
        url = reverse("mdtui-index-source")
        response = self.client.get(url)
        self.assertContains(response, "You have not entered Document Indexing Data.")

    def test_07_posting_document_with_all_keys(self):
        """
        Uploading File though MDTUI, adding all Secondary indexes accordingly.
        """
        # Selecting Document Type Rule
        url = reverse('mdtui-index-type')
        response = self.client.post(url, {'docrule': test_mdt_docrule_id})
        self.assertEqual(response.status_code, 302)
        # Getting indexes form and matching form Indexing Form fields names
        url = reverse('mdtui-index-details')
        response = self.client.get(url)
        rows_dict = self._read_indexes_form(response)
        post_dict = self._convert_doc_to_post_dict(rows_dict, doc1_dict)
        # Adding Document Indexes
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 302)
        url = reverse('mdtui-index-source')
        response = self.client.get(url)
        self.assertContains(response, 'Friends ID: 123')
        self.assertEqual(response.status_code, 200)
        # Make the file upload
        file = os.path.join(settings.FIXTURE_DIRS[0], 'testdata', doc1+'.pdf')
        data = { 'file': open(file, 'rb'), 'post_data':'to make request post type'}
        response = self.client.post(url, data)
        # Follow Redirect
        self.assertEqual(response.status_code, 302)
        new_url = self._retrieve_redirect_response_url(response)
        response = self.client.get(new_url)
        self.assertContains(response, 'Your document has been indexed successfully')
        self.assertContains(response, 'Friends Name: Andrew')
        self.assertContains(response, 'Start Again')

    def test_08_metadata_exists_for_uploaded_documents(self):
        """
        Document now exists in couchDB
        Querying CouchDB itself to test docs exist.
        """
        url = couchdb_url + '/dmscouch/'+doc1+'?revs_info=true'
        # HACK: faking 'request' object here
        r = self.client.get(url)
        cou = urllib.urlopen(url)
        resp = cou.read()
        r.status_code = 200
        r.content = resp
        self.assertContains(r, doc1)
        self.assertContains(r, 'Iurii Garmash')

    def test_09_search_works(self):
        """
        Testing Search part opens.
        """
        url = reverse('mdtui-search')
        response = self.client.get(url)
        self.assertContains(response, 'Adlibre Invoices')
        self.assertContains(response, 'Document Search')
        self.assertEqual(response.status_code, 200)

    def test_10_search_indexes_warning(self):
        """
        Testing Search part Warning for indexes.
        """
        url = reverse('mdtui-search-options')
        response = self.client.get(url)
        self.assertContains(response, 'You have not defined Document Type.')
        self.assertEqual(response.status_code, 200)

    def test_11_search_results_warning(self):
        """
        Testing Search part  warning for results.
        """
        url = reverse('mdtui-search-results')
        response = self.client.get(url)
        self.assertContains(response, 'You have not defined Document Searching Options')
        self.assertEqual(response.status_code, 200)

    def test_12_search_docrule_select_improper_call(self):
        """
        Makes wrong request to view. Response returns back to docrule selection.
        """
        url = reverse('mdtui-search-type')
        response = self.client.post(url)
        self.assertContains(response, 'Adlibre Invoices')
        self.assertEqual(response.status_code, 200)

    def test_13_search_docrule_selection(self):
        """
        Proper Indexing call.
        """
        url = reverse('mdtui-search-type')
        data = {'docrule': test_mdt_docrule_id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        new_url = self._retrieve_redirect_response_url(response)
        response = self.client.get(new_url)
        # checking for proper fields rendering
        self.assertContains(response, "Creation Date From")
        self.assertContains(response, "To")
        self.assertContains(response, "Employee ID")
        self.assertContains(response, "Employee Name")
        self.assertContains(response, "Friends ID")
        self.assertContains(response, "Friends Name")
        self.assertContains(response, "Required Date")
        self.assertNotContains(response, "Description</label>")
        self.assertNotContains(response, "You have not selected Doccument Type Rule")
        self.assertEqual(response.status_code, 200)

    def test_14_search_by_date_proper(self):
        """
        Proper call to search by date.
        MDTUI Search By Index Form parses data properly.
        Search Step 3 displays proper captured indexes.
        """
        # setting docrule
        url = reverse('mdtui-search-type')
        data = {'docrule': test_mdt_docrule_id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        url = reverse('mdtui-search-options')
        # Searching by Document 1 Indexes
        response = self.client.post(url, {'date': doc1_dict["date"], 'end_date': '', '0':'', '1':'', '2':'', '3':'', '4':''})
        self.assertEqual(response.status_code, 302)
        new_url = self._retrieve_redirect_response_url(response)
        response = self.client.get(new_url)
        self.assertEqual(response.status_code, 200)
        # no errors appeared
        self.assertNotContains(response, "You have not defined Document Searching Options")
        # document found
        self.assertContains(response, doc1)
        self.assertContains(response, doc1_dict['description'])
        # context processors provide docrule name
        self.assertContains(response, "Adlibre Invoices")

    def test_15_search_by_key_proper(self):
        """
        Proper call to search by secondary index key.
        Search Step 3 displays proper captured indexes.
        """
        # setting docrule
        url = reverse('mdtui-search-type')
        data = {'docrule': test_mdt_docrule_id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        # assigning form fields
        url = reverse('mdtui-search-options')
        response = self.client.get(url)
        # Getting indexes form and matching form Indexing Form fields names
        rows_dict = self._read_indexes_form(response)
        search_dict = self._createa_search_dict(doc1_dict)
        # Search without a description (we can't yet search on this field)
        del search_dict['description']
        # Searching without date
        search_dict["date"] = ''
        post_dict = self._convert_doc_to_post_dict(rows_dict, search_dict)
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 302)
        new_url = self._retrieve_redirect_response_url(response)
        response = self.client.get(new_url)
        self.assertEqual(response.status_code, 200)
        # no errors appeared
        self.assertNotContains(response, "You have not defined Document Searching Options")
        # document found
        self.assertContains(response, doc1)
        # context processors provide docrule name
        self.assertContains(response, "Adlibre Invoices")

    def test_16_search_by_date_improper(self):
        """
        Improper call to search by date.
        Search Step 3 does not display doc1.
        """
        # using today's date to avoid doc exists.
        date_req = datetime.datetime.now()
        date_str = datetime.datetime.strftime(date_req, "%Y-%m-%d")
        # setting docrule
        url = reverse('mdtui-search-type')
        data = {'docrule': test_mdt_docrule_id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        url = reverse('mdtui-search-options')
        # Searching by Document 1 Indexes
        response = self.client.post(url, {'date': date_str, '0':'', '1':'', '2':'', '3':''})
        self.assertEqual(response.status_code, 302)
        new_url = self._retrieve_redirect_response_url(response)
        response = self.client.get(new_url)
        self.assertEqual(response.status_code, 200)
        # no errors appeared
        self.assertNotContains(response, "You have not defined Document Searching Options")
        # document not found
        self.assertNotContains(response, doc1)

    def test_17_add_indexes_unvalidated_form_preserves_prepopulated_data(self):
        """
        MDTUI Indexing Form .
        Step 2 adding indexes into several fields instead of all required
        returns prepopulated form with errors.
        """
        # Selecting Document Type Rule
        url = reverse('mdtui-index-type')
        response = self.client.post(url, {'docrule': test_mdt_docrule_id})
        self.assertEqual(response.status_code, 302)
        url = reverse("mdtui-index-details")
        # Getting indexes form and matching form Indexing Form fields names
        response = self.client.get(url)
        rows_dict = self._read_indexes_form(response)
        post_dict = self._convert_doc_to_post_dict(rows_dict, doc1_dict)
        # Modifying post to brake it
        post_dict["description"]=u''
        post_dict["0"] = u''
        # Adding Document Indexes
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 200)
        # Response contains proper validation data
        self.assertContains(response, 'Brief Document Description') # form fields help exists
        self.assertContains(response, 'Name of tests person')
        self.assertContains(response, '2012-03-06') # docs data populated into form
        self.assertContains(response, 'Andrew')
        self.assertContains(response, '123456')
        self.assertContains(response, 'Iurii Garmash')
        self.assertContains(response, '// autocomplete for field Friends ID') # autocomplete (typehead) scripts rendered
        self.assertContains(response, '// autocomplete for field Friends Name')
        self.assertContains(response, 'This field is required') # form renders errors

    def test_18_parallel_keys_indexing_proper(self):
        """
        Testing Parallel keys lookup for recently uploaded document
        """
        # Selecting Document Type Rule
        url = reverse('mdtui-index-type')
        response = self.client.post(url, {'docrule': test_mdt_docrule_id})
        self.assertEqual(response.status_code, 302)
        url = reverse("mdtui-parallel-keys")
        response = self.client.post(url, typehead_call1)
        self.assertEqual(response.status_code, 200)
        # Response contains proper data
        self.assertNotContains(response, '<html>') # json but not html response
        self.assertContains(response, 'Friends ID') # Proper keys
        self.assertContains(response, '123')
        self.assertContains(response, 'Friends Name')
        self.assertContains(response, 'Andrew')
        self.assertNotContains(response, 'Iurii Garmash') # Improper key
        self.assertNotContains(response, 'Employee Name')
        self.assertNotContains(response, 'Required Date')

    def test_19_parallel_keys_indexing_wrong(self):
        """
        Testing Parallel keys lookup for recently uploaded document
        """
        # Selecting Document Type Rule
        url = reverse('mdtui-index-type')
        response = self.client.post(url, {'docrule': test_mdt_docrule_id})
        self.assertEqual(response.status_code, 302)
        url = reverse("mdtui-parallel-keys")
        response = self.client.post(url, typehead_call3)
        self.assertEqual(response.status_code, 200)
        # Response contains proper data
        self.assertNotContains(response, '<html>')
        self.assertNotContains(response, 'Friends ID')
        self.assertNotContains(response, '123')
        self.assertNotContains(response, 'Friends Name')
        self.assertNotContains(response, 'Andrew')
        self.assertNotContains(response, 'Iurii Garmash')
        self.assertNotContains(response, 'Employee Name')
        self.assertNotContains(response, 'Required Date')

    def test_20_parallel_keys_indexing_set2_proper(self):
        """
        Testing Parallel keys lookup for recently uploaded document
        """
        # Selecting Document Type Rule
        url = reverse('mdtui-index-type')
        response = self.client.post(url, {'docrule': test_mdt_docrule_id})
        self.assertEqual(response.status_code, 302)
        url = reverse("mdtui-parallel-keys")
        response = self.client.post(url, typehead_call2)
        self.assertEqual(response.status_code, 200)
        # Response contains proper data
        self.assertNotContains(response, '<html>')
        self.assertNotContains(response, 'Friends ID')
        self.assertNotContains(response, 'Friends Name')
        self.assertNotContains(response, 'Andrew')
        self.assertNotContains(response, 'Required Date')
        self.assertContains(response, 'Iurii Garmash')
        self.assertContains(response, 'Employee Name')
        self.assertContains(response, 'Employee ID')
        self.assertContains(response, '123456')

    def test_21_parallel_keys_search_proper(self):
        """
        Testing Parallel keys lookup for recently uploaded document
        """
        # Selecting Document Type Rule
        url = reverse('mdtui-search-type')
        response = self.client.post(url, {'docrule': test_mdt_docrule_id})
        self.assertEqual(response.status_code, 302)
        url = reverse("mdtui-parallel-keys")
        # Adding Document Indexes
        response = self.client.post(url, typehead_call1)
        self.assertEqual(response.status_code, 200)
        # Response contains proper data
        self.assertNotContains(response, '<html>') # json but not html response
        self.assertContains(response, 'Friends ID') # Proper keys
        self.assertContains(response, '123')
        self.assertContains(response, 'Friends Name')
        self.assertContains(response, 'Andrew')
        self.assertNotContains(response, 'Iurii Garmash') # Improper key
        self.assertNotContains(response, 'Employee Name')

    def test_22_parallel_keys_searching_set2_proper(self):
        """
        Testing Parallel keys lookup for recently uploaded document
        """
        # Selecting Document Type Rule
        url = reverse('mdtui-search-type')
        response = self.client.post(url, {'docrule': test_mdt_docrule_id})
        self.assertEqual(response.status_code, 302)
        url = reverse("mdtui-parallel-keys")
        response = self.client.post(url, typehead_call2)
        self.assertEqual(response.status_code, 200)
        # Response contains proper data
        self.assertNotContains(response, '<html>')
        self.assertNotContains(response, 'Friends ID')
        self.assertNotContains(response, 'Friends Name')
        self.assertNotContains(response, 'Andrew')
        self.assertContains(response, 'Iurii Garmash')
        self.assertContains(response, 'Employee Name')
        self.assertContains(response, 'Employee ID')
        self.assertContains(response, '123456')

    def test_23_parallel_keys_indexing_wrong(self):
        """
        Testing Parallel keys lookup for recently uploaded document
        """
        # Selecting Document Type Rule
        url = reverse('mdtui-search-type')
        response = self.client.post(url, {'docrule': test_mdt_docrule_id})
        self.assertEqual(response.status_code, 302)
        url = reverse("mdtui-parallel-keys")
        response = self.client.post(url, typehead_call3)
        self.assertEqual(response.status_code, 200)
        # Response contains proper data
        self.assertNotContains(response, '<html>')
        self.assertNotContains(response, 'Friends ID')
        self.assertNotContains(response, '123')
        self.assertNotContains(response, 'Friends Name')
        self.assertNotContains(response, 'Andrew')
        self.assertNotContains(response, 'Iurii Garmash')
        self.assertNotContains(response, 'Employee Name')
#
#    def test_24_additional_docs_adding(self):
#        """
#        Adds additional document 2 and 3 for more complex tests.
#        Those docs must be used farther for complex searches.
#        """
#        """
#        Uploading File though MDTUI, adding all Secondary indexes accordingly.
#        """
#        # Selecting Document Type Rule
#        url = reverse('mdtui-index-type')
#        response = self.client.post(url, {'docrule': test_mdt_docrule_id})
#        self.assertEqual(response.status_code, 302)
#        # Getting indexes form and matching form Indexing Form fields names
#        url = reverse('mdtui-index-details')
#        response = self.client.get(url)
#        rows_dict = self._read_indexes_form(response)
#        post_dict = self._convert_doc_to_post_dict(rows_dict, doc2_dict)
#        # Adding Document Indexes
#        response = self.client.post(url, post_dict)
#        self.assertEqual(response.status_code, 302)
#        uurl = self._retrieve_redirect_response_url(response)
#        response = self.client.get(uurl)
#        print uurl
#        #print response
#        self.assertContains(response, 'Friends ID: 321')
#        self.assertEqual(response.status_code, 200)
#        # Make the file upload
#        file = os.path.join(settings.FIXTURE_DIRS[0], 'testdata', doc2+'.pdf')
#        print file
#        data = { 'file': open(file, 'rb') , 'post_data':'to make this request post type'}
#        print data
#        response = self.client.post(uurl, data)
#        # Follow Redirect
#        self.assertEqual(response.status_code, 302)
#        new_url = self._retrieve_redirect_response_url(response)
#        response = self.client.get(new_url)
#        self.assertContains(response, 'Your document has been indexed successfully')
#        self.assertContains(response, 'Friends Name: Yuri')
#        self.assertContains(response, 'Start Again')
#
#
#        # Selecting Document Type Rule
#        url = reverse('mdtui-index-type')
#        response = self.client.post(url, {'docrule': test_mdt_docrule_id})
#        self.assertEqual(response.status_code, 302)
#        # Getting indexes form and matching form Indexing Form fields names
#        url = reverse('mdtui-index-details')
#        response = self.client.get(url)
#        rows_dict = self._read_indexes_form(response)
#        post_dict = self._convert_doc_to_post_dict(rows_dict, doc1_dict)
#        # Adding Document Indexes
#        response = self.client.post(url, post_dict)
#        self.assertEqual(response.status_code, 302)
#        uurl = self._retrieve_redirect_response_url(response)
#        response = self.client.get(uurl)
#        print uurl
#        #print response
#        self.assertContains(response, 'Friends ID: 123')
#        self.assertEqual(response.status_code, 200)
#        # Make the file upload
#        file = os.path.join(settings.FIXTURE_DIRS[0], 'testdata', doc1+'.pdf')
#        print file
#        data = { 'file': open(file, 'rb') , 'post_data':'to make this request post type'}
#        print data
#        response = self.client.post(uurl, data)
#        # Follow Redirect
#        self.assertEqual(response.status_code, 302)
#        new_url = self._retrieve_redirect_response_url(response)
#        response = self.client.get(new_url)
#        self.assertContains(response, 'Your document has been indexed successfully')
#        self.assertContains(response, 'Friends Name: Andrew')
#        self.assertContains(response, 'Start Again')
#
#    def test_25_search_by_date_range_only_proper(self):
#        """
#        Proper call to search by date range only.
#        MDTUI Search By Index Form parses data properly.
#        Search Step 3 displays proper captured indexes.
#        """
#        # setting docrule
#        url = reverse('mdtui-search-type')
#        data = {'docrule': test_mdt_docrule_id}
#        response = self.client.post(url, data)
#        self.assertEqual(response.status_code, 302)
#        url = reverse('mdtui-search-options')
#        # Searching by Document 1 Indexes
#        response = self.client.post(url, {'date': '2012-03-05', 'end_date': '2012-03-07', '0':'', '1':'', '2':'', '3':'', '4':''})
#        self.assertEqual(response.status_code, 302)
#        new_url = self._retrieve_redirect_response_url(response)
#        response = self.client.get(new_url)
#        self.assertEqual(response.status_code, 200)
#        # no errors appeared
#        self.assertNotContains(response, "You have not defined Document Searching Options")
#        # document found
#        self.assertContains(response, doc1)
#        self.assertContains(response, doc1_dict['description'])
#        # context processors provide docrule name
#        self.assertContains(response, "Adlibre Invoices")

    def test_z_cleanup(self):
        """
        Cleaning up after all tests finished.
        Must be ran after all tests in this test suite.
        """
        # Deleting all- test MDT's (with doccode from var "test_mdt_docrule_id") using MDT's API.
        url = reverse('api_mdt')
        response = self.client.get(url, {"docrule_id": str(test_mdt_docrule_id)})
        data = json.loads(str(response.content))
        for key, value in data.iteritems():
            mdt_id =  data[key]["mdt_id"]
            response = self.client.delete(url, {"mdt_id": mdt_id})
            self.assertEqual(response.status_code, 204)

        # Delete file "doc1"
        url = reverse('api_file', kwargs={'code': doc1,})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def _read_indexes_form(self, response):
        """
        Helper to parse response with Document Indexing Form (MDTUI Indexing Step 2 Form)
        And returns key:value dict of form's dynamical fields for our tests.
        """
        prog = re.compile(indexes_form_match_pattern, re.DOTALL)
        matches_set = prog.findall(str(response))
        matches = {}
        for key,value in matches_set: matches[key]=value
        return matches

    def _convert_doc_to_post_dict(self, matches, doc):
        """
        Helper to convert Tests Documents into proper POST dictionary for Indexing Form testing.
        """
        post_doc_dict = {}
        for key, value in doc.iteritems():
            if key in matches.keys():
                post_doc_dict[matches[key]] = value
            else:
                post_doc_dict[key] = value
        return post_doc_dict

    def _retrieve_redirect_response_url(self, response):
        """
        helper parses 302 response object.
        Returns redirect url, parsed by regex.
        """
        self.assertEqual(response.status_code, 302)
        new_url = re.search("(?P<url>https?://[^\s]+)", str(response)).group("url")
        return new_url

    def _createa_search_dict(self, doc_dict):
        """
        Creates a search dict to avoid rewriting document dict constants.
        """
        search_dict = {}
        for key in doc_dict.keys():
            search_dict[key] = doc_dict[key]
        return search_dict
