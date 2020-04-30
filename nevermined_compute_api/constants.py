class ConfigSections:
    RESOURCES = 'resources'


class BaseURLs:
    BASE_OPERATOR_URL = '/api/v1/nevermined-compute-api'
    SWAGGER_URL = '/api/v1/docs'  # URL for exposing Swagger UI (without trailing '/')


class Metadata:
    TITLE = 'Nevermined Compute API'
    DESCRIPTION = 'Infrastructure Nevermined Compute API Micro-service' \
                  '. When running with our Docker images, ' \
                  'it is exposed under `http://localhost:8050`.'
    HOST = 'neverminedcompute.com'