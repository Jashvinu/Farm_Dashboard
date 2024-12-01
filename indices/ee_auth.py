import ee

try:
    ee.Initialize(project='wrkfarm-415118')
except Exception as e:
    ee.Authenticate()
    ee.Initialize(project='wrkfarm-415118')
