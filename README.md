# dropbox_console
Use dropbox in console

# Installation

```
$ git clone https://github.com/sidra-asa/dropbox_console.git
$ cd dropbox_console
$ git submodule init
$ git submodule update
$ cd modules/dropbox-sdk-python
$ python setup.py install

```

# How to use

This tool access to Dropbox via Dropbox API v2,
you need the access token of your account.
Please follow the instruction:
[Get access token](https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/)


Then start the console:

```
$ python run.py

```

In the beginning, Input the token:

```
console > token ACCESS_TOKEN
```

Then you can list the remote directory, even upload the files.
