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
        self.assertTrue('one' in dictionary)
        self.assertTrue('TWO' in dictionary)
        self.assertTrue('three' in dictionary)

        self.assertEqual(dictionary['one'], 'test value')
        self.assertEqual(dictionary['TWO'], True)
        self.assertEqual(dictionary['three'], 3.0)

        dictionary = SystemGlobal.objects.as_dict(prefix='teSTinG_')
        self.assertTrue('one' in dictionary)
        self.assertTrue('TWO' in dictionary)
        self.assertTrue('three' in dictionary)

        self.assertEqual(dictionary['one'], 'test value')
        self.assertEqual(dictionary['TWO'], True)
        self.assertEqual(dictionary['three'], 3.0)

        dictionary = SystemGlobal.objects.as_dict(prefix='non_existent')
        self.assertEqual(dictionary, {})

    def test_as_dict_without_prefix(self):
        dictionary = SystemGlobal.objects.as_dict()
        self.assertTrue('testing_one' in dictionary)
        self.assertTrue('TESTING_TWO' in dictionary)
        self.assertTrue('testing_three' in dictionary)

        self.assertEqual(dictionary['testing_one'], 'test value')
        self.assertEqual(dictionary['TESTING_TWO'], True)
        self.assertEqual(dictionary['testing_three'], 3.0)

    def test_as_dict_without_coerce(self):
        dictionary = SystemGlobal.objects.as_dict(coerce=False)
        self.assertTrue('testing_one' in dictionary)
        self.assertTrue('TESTING_TWO' in dictionary)
        self.assertTrue('testing_three' in dictionary)

        self.assertEqual(dictionary['testing_one'], 'test value')
        self.assertEqual(dictionary['TESTING_TWO'], '\t t')
        self.assertEqual(dictionary['testing_three'], '3.0 ')

    def test_as_dict_with_to_lower(self):
        dictionary = SystemGlobal.objects.as_dict(to_lower=True)
        self.assertTrue('testing_one' in dictionary)
        self.assertTrue('testing_two' in dictionary)
        self.assertTrue('testing_three' in dictionary)

        self.assertEqual(dictionary['testing_one'], 'test value')
        self.assertEqual(dictionary['testing_two'], True)
        self.assertEqual(dictionary['testing_three'], 3.0)

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

        self.assertEqual(len(connection.queries), 0)

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
        self.assertEquals(value, 'SystemGlobals Testing')

        SystemGlobal.objects.set('TESTING_four', ' SystemGlobals new Testing\n')
        value = SystemGlobal.objects.get_value('TESTING_four')
        self.assertEquals(value, 'SystemGlobals new Testing')

        SystemGlobal.objects.set('TESTING_five', 123)
        value = SystemGlobal.objects.get_value('TESTING_five')
        self.assertEquals(value, 123)

        # TearDown
        SystemGlobal.objects.filter(var_name='TESTING_four').delete()
        SystemGlobal.objects.filter(var_name='TESTING_five').delete()

    def test_get_value(self):
        value = SystemGlobal.objects.get_value('TESTING_TWO')
        self.assertEquals(value, True)

        value = SystemGlobal.objects.get_value('testing_three')
        self.assertEquals(value, 3.0)

    def test_coerce(self):
        """
        Testing SystemGlobal.coerce static method.
        """

        # Float
        coerced_value = SystemGlobal.coerce('1.0')
        self.assertEquals(coerced_value, 1.0)

        coerced_value = SystemGlobal.coerce('3.33')
        self.assertEquals(coerced_value, 3.33)

        # Int
        coerced_value = SystemGlobal.coerce(' 3 ')
        self.assertEquals(coerced_value, 3)

        # True
        coerced_value = SystemGlobal.coerce(' true ')
        self.assertEquals(coerced_value, True)

        coerced_value = SystemGlobal.coerce('\n yEs ')
        self.assertEquals(coerced_value, True)

        coerced_value = SystemGlobal.coerce('\n Y \t')
        self.assertEquals(coerced_value, True)

        coerced_value = SystemGlobal.coerce('t')
        self.assertEquals(coerced_value, True)

        # False
        coerced_value = SystemGlobal.coerce(' faLse ')
        self.assertEquals(coerced_value, False)

        coerced_value = SystemGlobal.coerce(' no ')
        self.assertEquals(coerced_value, False)

        coerced_value = SystemGlobal.coerce('\t\tn\n\n')
        self.assertEquals(coerced_value, False)

        coerced_value = SystemGlobal.coerce('F')
        self.assertEquals(coerced_value, False)

        # String
        coerced_value = SystemGlobal.coerce(' value ')
        self.assertEquals(coerced_value, 'value')

    def test_stale_cache(self):
        self.assertEqual(SystemGlobal.objects.get_value('testing_one'), 'test value')

        one = SystemGlobal.objects.get(var_name='testing_one')
        one.value = 'test2 value'
        one.save()
        self.assertEqual(SystemGlobal.objects.get_value('testing_one'), 'test2 value')

        SystemGlobal.objects.filter(var_name='testing_one').update(value='test3 value')
        self.assertEqual(SystemGlobal.objects.get_value('testing_one'), 'test3 value')

    def test_system_global_queryset(self):
        """ Test SystemGlobal.SystemGlobalQuerySet """
        updated_rows = SystemGlobal.objects.all().update(value='test value')
        total_globals = SystemGlobal.objects.count()
        self.assertEqual(updated_rows, total_globals)

        # extra check to make sure SystemGlobal are saving values in db
        SystemGlobal.objects.set('SAVED', ' SystemGlobals Testing')
        self.assertTrue(SystemGlobal.objects.get_value('SAVED'))

        new_total_globals = SystemGlobal.objects.count()
        self.assertEqual(new_total_globals, total_globals + 1)
