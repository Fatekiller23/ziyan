# ziyan
A easy-to-use data collector with your device.

## Support

Python 3.4+

Python 2.7.13

Python 2.7.12

## Dependence

The backend depends on redis or influxdb

Depending on the `send_to_where` option in the configuration file

## Installation

The last stable release is available on [releases](https://github.com/maboss-YCMan/ziyan/releases) or you can download the source code for installation.

```
python setup.py install
```

## Example

1. Generate project catalogs:

```
$ ziyan_make projectname

$ cd progectname
```

2. The generated project is a test project that can run

3. Write the logical and custom configuration of the fetch data in the plugin

4. Manage command

```
$ python manage.py run  # project run

$ python manage.py test  # test the log output options
```