from django.core.cache import cache

# Set a test cache value
cache.set('dashboard_data_test', 'test_value', timeout=60)

# Retrieve the test cache value
value = cache.get('dashboard_data_test')
print(value)  # Should print 'test_value'
