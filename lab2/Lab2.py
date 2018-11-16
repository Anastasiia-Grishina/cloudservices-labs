
# coding: utf-8

# In[22]:

from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver
import libcloud.security
# asdfczx


# In[24]:

# TODO Verify SSL
# https://libcloud.readthedocs.io/en/0.20.1/other/ssl-certificate-validation.html
libcloud.security.VERIFY_SSL_CERT = False
CREDIENTIALS_PATH = r'C:\Users\aagri\Desktop\PERCCOM Studies\3 Sweden\Cloud Services\Lab 2\credentials.txt'
CREDIENTIALS_FILE = open(CREDIENTIALS_PATH, 'r')
access_id  = CREDIENTIALS_FILE.readline()
access_key = CREDIENTIALS_FILE.readline()

cls = get_driver(Provider.S3)
driver = cls(access_id.strip('\n'), access_key)

container = driver.create_container(container_name='mannasbucketfromcode')


# In[14]:

access_id.strip('\n')


# In[13]:

access_key


# In[ ]:



