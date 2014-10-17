OIPA_auth
=========
OIPA_auth is a middleware that can be used in oipa to authorise and authenticate api users users.

Usage
-----
This middleware allows authentication and authoriasation in OIPA's API by using a 'token=xxx' parameter
After installation each api call made to OIPA gets intercepted by this middleware. The provided key gets validated in SSO-Django.
If the key is valid the request is processed. If not, the user gets an Unauthorised response.

Installation instructions
-------------------------
Clone this repository
```
git clone https://github.com/Murrx/OIPA_auth.git
```
change directory to the OIPA_auth folder
```
cd OIPA_auth
```
package the source using setup.py. the package is stored inside the newly created dist folder
```
python setup.py sdist
```
install the package using pip (do not forget to activate virtualenv if your are using one
```
pip install OIPA_auth --no-index --find-links dist
```
Now OIPA_auth is successfully installed. next it has to be activated in OIPA

Add the middleware to OIPA's settings.py. Maek sure to place AuthorizationMiddleware after Authenticationmiddleware. the result should look someting like:
```
MIDDLEWARE_CLASSES = (
    ...
    'OIPA_auth.middleware.AuthenticationMiddleware',
    'OIPA_auth.middleware.AuthorizationMiddleware',
    ...
)
```
add OIPA_auth_settings to settings.py this should look someting like, where <HOST> is the hostname of the SSO-Django and <PORT> is the port it listens to.
```
    OIPA_AUTH_SETTINGS = {
        'HOST': '<HOST>',
        'PORT': '<PORT',
    }
```
    
