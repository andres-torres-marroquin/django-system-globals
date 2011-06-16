from sure import that
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.test import TestCase
from system_globals.models import SystemGlobal

class SystemGlobalTest(TestCase):
    
    def setUp(self):
        self.sg1 = SystemGlobal.objects.create(var_name='testing_one', value='test value')
        self.sg2 = SystemGlobal.objects.create(var_name='TESTING_TWO', value='\t t')
        self.sg3 = SystemGlobal.objects.create(var_name='testing_three', value='3.0 ')
        
    def tearDown(self):
        cache.clear()
        self.sg1.delete()
        self.sg2.delete()
        self.sg3.delete()
        
    def test_as_dict_with_prefix(self):
        dictionary = SystemGlobal.objects.as_dict(prefix='testing_')
        assert that(dictionary).has('one')
        assert that(dictionary).has('TWO')
        assert that(dictionary).has('three')
        
        assert that(dictionary['one']).equals('test value')
        assert that(dictionary['TWO']).equals(True)
        assert that(dictionary['three']).equals(3.0)
        
        dictionary = SystemGlobal.objects.as_dict(prefix='teSTinG_')
        assert that(dictionary).has('one')
        assert that(dictionary).has('TWO')
        assert that(dictionary).has('three')
        
        assert that(dictionary['one']).equals('test value')
        assert that(dictionary['TWO']).equals(True)
        assert that(dictionary['three']).equals(3.0)
        
        dictionary = SystemGlobal.objects.as_dict(prefix='non_existent')
        assert that(dictionary).equals({})
        
    def test_as_dict_without_prefix(self):
        dictionary = SystemGlobal.objects.as_dict()
        assert that(dictionary).has('testing_one')
        assert that(dictionary).has('TESTING_TWO')
        assert that(dictionary).has('testing_three')
        
        assert that(dictionary['testing_one']).equals('test value')
        assert that(dictionary['TESTING_TWO']).equals(True)
        assert that(dictionary['testing_three']).equals(3.0)
    
    def test_as_dict_without_coerce(self):
        dictionary = SystemGlobal.objects.as_dict(coerce=False)
        assert that(dictionary).has('testing_one')
        assert that(dictionary).has('TESTING_TWO')
        assert that(dictionary).has('testing_three')
        
        assert that(dictionary['testing_one']).equals('test value')
        assert that(dictionary['TESTING_TWO']).equals('\t t')
        assert that(dictionary['testing_three']).equals('3.0 ')
        
    def test_as_dict_with_to_lower(self):
        dictionary = SystemGlobal.objects.as_dict(to_lower=True)
        assert that(dictionary).has('testing_one')
        assert that(dictionary).has('testing_two')
        assert that(dictionary).has('testing_three')
        
        assert that(dictionary['testing_one']).equals('test value')
        assert that(dictionary['testing_two']).equals(True)
        assert that(dictionary['testing_three']).equals(3.0)
        
    def test_as_dict_using_cache(self):
        # Storing the original DEBUG value
        original_debug = settings.DEBUG
        
        # The Django docs says that DEBUG should be set to True for store queries
        # https://docs.djangoproject.com/en/dev/faq/models/#how-can-i-see-the-raw-sql-queries-django-is-running
        settings.DEBUG = True
        SystemGlobal.objects.as_dict()
        SystemGlobal.objects.as_dict()
        SystemGlobal.objects.as_dict()
        SystemGlobal.objects.as_dict(prefix='Test01')
        SystemGlobal.objects.as_dict(prefix='Test02')
        SystemGlobal.objects.as_dict(prefix='Test03')
        SystemGlobal.objects.as_dict(prefix='Test04', to_lower=True)
        SystemGlobal.objects.as_dict(prefix='Test05', to_lower=True)
        SystemGlobal.objects.as_dict(prefix='Test06', to_lower=True)
        SystemGlobal.objects.as_dict(prefix='Test07', to_lower=True, coerce=False)
        SystemGlobal.objects.as_dict(prefix='Test08', to_lower=True, coerce=False)
        SystemGlobal.objects.as_dict(prefix='Test09', to_lower=True, coerce=False)
        SystemGlobal.objects.as_dict(prefix='Test10', coerce=False)
        SystemGlobal.objects.as_dict(prefix='Test11', coerce=False)
        SystemGlobal.objects.as_dict(prefix='Test12', coerce=False)
        
        assert that(connection.queries).len_is(1)
        
        # Restoring the original DEBUG value
        settings.DEBUG = original_debug 
    
    def test_as_dict_after_set_a_integer(self):
        SystemGlobal.objects.set('TESTING_ONE', 1010)
        SystemGlobal.objects.as_dict()
        
    def test_as_dict_after_set_a_float(self):
        SystemGlobal.objects.set('TESTING_ONE', 3.1416)
        SystemGlobal.objects.as_dict()
        
    def test_as_dict_after_set_a_boolean(self):
        SystemGlobal.objects.set('TESTING_ONE', True)
        SystemGlobal.objects.as_dict()
        
    def test_set(self):
        SystemGlobal.objects.set('TESTING_TWO', ' SystemGlobals Testing\n')
        value = SystemGlobal.objects.get_value('TESTING_TWO')
        assert that(value).equals('SystemGlobals Testing')
        
        SystemGlobal.objects.set('TESTING_four', ' SystemGlobals new Testing\n')
        value = SystemGlobal.objects.get_value('TESTING_four')
        assert that(value).equals('SystemGlobals new Testing')
        
        SystemGlobal.objects.set('TESTING_five', 123)
        value = SystemGlobal.objects.get_value('TESTING_five')
        assert that(value).equals(123)
        
        # TearDown
        SystemGlobal.objects.filter(var_name='TESTING_four').delete()
        SystemGlobal.objects.filter(var_name='TESTING_five').delete()
        
    def test_get_value(self):
        value = SystemGlobal.objects.get_value('TESTING_TWO')
        assert that(value).equals(True)
        
        value = SystemGlobal.objects.get_value('testing_three')
        assert that(value).equals(3.0)
    
    def test_coerce(self):
        """
        Testing SystemGlobal.coerce static method.
        """
        
        # Float
        coerced_value = SystemGlobal.coerce('1.0')
        assert that(coerced_value).equals(1.0)
        
        coerced_value = SystemGlobal.coerce('3.33')
        assert that(coerced_value).equals(3.33)
        
        # Int
        coerced_value = SystemGlobal.coerce(' 3 ')
        assert that(coerced_value).equals(3)
        
        # True
        coerced_value = SystemGlobal.coerce(' true ')
        assert that(coerced_value).equals(True)
        
        coerced_value = SystemGlobal.coerce('\n yEs ')
        assert that(coerced_value).equals(True)
        
        coerced_value = SystemGlobal.coerce('\n Y \t')
        assert that(coerced_value).equals(True)
        
        coerced_value = SystemGlobal.coerce('t')
        assert that(coerced_value).equals(True)
        
        # False
        coerced_value = SystemGlobal.coerce(' faLse ')
        assert that(coerced_value).equals(False)
        
        coerced_value = SystemGlobal.coerce(' no ')
        assert that(coerced_value).equals(False)
        
        coerced_value = SystemGlobal.coerce('\t\tn\n\n')
        assert that(coerced_value).equals(False)
        
        coerced_value = SystemGlobal.coerce('F')
        assert that(coerced_value).equals(False)
        
        # String
        coerced_value = SystemGlobal.coerce(' value ')
        assert that(coerced_value).equals('value')
    
