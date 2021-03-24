Storage
##########

Amazon S3
*********

AlekSIS allows you to configure an Amazon S3 endpoint for static and media
files. This is useful e.g. for loadbalancing with multiple AlekSIS
instances.

Configure an S3 endpoint
=======================

If you want to use an S3 endpoint to store files you have to configure the
endpoint in your configuration file (`/etc/aleksis/aleksis.toml`)::

  # Default values
  [storage.s3]
  enabled = true
  endpoint_url = "https://minio.example.com"
  bucket_name = "aleksis-test"
  access_key_id = "XXXXXXXXXXXXXX"
  secret_key = "XXXXXXXXXXXXXXXXXXXXXX"
